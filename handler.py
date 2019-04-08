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

# stats example:
# {'downloader/request_bytes': 10055,
#  'downloader/request_count': 34,
#  'downloader/request_method_count/GET': 34,
#  'downloader/response_bytes': 174399,
#  'downloader/response_count': 34,
#  'downloader/response_status_count/200': 32,
#  'downloader/response_status_count/301': 2,
#  'finish_reason': 'finished',
#  'finish_time': datetime.datetime(2019, 4, 8, 11, 49, 32, 717749),
#  'item_scraped_count': 30,
#  'log_count/DEBUG': 112,
#  'log_count/INFO': 9,
#  'log_count/WARNING': 1,
#  'memusage/max': 76472320,
#  'memusage/startup': 76472320,
#  'postgresql/add': 30,
#  'request_depth_max': 1,
#  'response_received_count': 32,
#  'robotstxt/request_count': 1,
#  'robotstxt/response_count': 1,
#  'robotstxt/response_status_count/200': 1,
#  'scheduler/dequeued': 32,
#  'scheduler/dequeued/memory': 32,
#  'scheduler/enqueued': 32,
#  'scheduler/enqueued/memory': 32,
#  'start_time': datetime.datetime(2019, 4, 8, 11, 49, 22, 841506)}


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
