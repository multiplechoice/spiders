from collections import OrderedDict
import datetime
import logging
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils import display
from scrapy.utils.project import get_project_settings


# it's necessary to remove the lambda loggers first, otherwise the Scrapy log
# settings aren't respected and we flood CloudWatch with logs anyway
root = logging.getLogger()
root.handlers = []


def format_response(response):
    # the stats object has datetime objects and they won't serialise properly
    fixed = OrderedDict()
    for key, value in sorted(response.items()):
        if isinstance(value, datetime.datetime):
            fixed[key] = str(value)
        else:
            fixed[key] = value

    return fixed


def put_metrics(stats, function_name):
    import boto3
    cloudwatch = boto3.client('cloudwatch')
    for key, name, value in (
        ('item_scraped_count', 'scraped',  'items'),
        ('postgresql/add',     'added',    'items'),
        ('postgresql/modify',  'modified', 'items'),
        ('postgresql/ignore',  'ignored',  'items')
    ):
        cloudwatch.put_metric_data(
            Namespace='spiders',
            MetricData=[
                {
                    'MetricName': '/'.join([function_name, key]),  # 'spiders-dev-tvinna/postgresql/add
                    'Dimensions': [{'Name': name, 'Value': value}, ],
                    'Unit': 'Count',
                    'Value': stats.get(key, 0)
                },
            ]
        )


def run(event, context):
    settings = get_project_settings()
    settings.update({
        'LOG_ENABLED': False,
        'LOG_LEVEL': 'WARNING',
        'TELNETCONSOLE_ENABLED': False,
        'PG_CREDS': os.getenv('PG_CREDS')
    })

    process = CrawlerProcess(settings)
    name = event.get('spider', os.getenv('SCRAPY_SPIDER'))
    spider = process.create_crawler(name)
    process.crawl(spider)
    process.start()

    stats = spider.stats.get_stats()
    put_metrics(stats, function_name=context.function_name)
    return format_response(stats)


if __name__ == '__main__':
    event = {'spider': os.getenv('SCRAPY_SPIDER', 'tvinna')}
    display.pprint(run(event, ''))
