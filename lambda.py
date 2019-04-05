from collections import OrderedDict
import datetime
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def format_response(response):
    # the stats object has datetime objects and they won't serialise properly
    fixed = OrderedDict()
    for key, value in sorted(response.items()):
        if isinstance(value, datetime.datetime):
            fixed[key] = str(value)
        else:
            fixed[key] = value

    return fixed


def run(event, context):
    process = CrawlerProcess(get_project_settings())
    process.settings.update({
        'LOG_ENABLED': False
    })

    name = event.get('spider', os.getenv('SCRAPY_SPIDER'))
    spider = process.create_crawler(name)

    process.crawl(spider)
    process.start()
    return format_response(spider.stats.get_stats())


if __name__ == '__main__':
    event = {'spider': os.getenv('SCRAPY_SPIDER', 'tvinna')}
    print(run(event, ''))
