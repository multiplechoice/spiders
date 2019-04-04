import json
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def run(event, context):
    process = CrawlerProcess(get_project_settings())
    process.settings.update({
        'LOG_ENABLED': False
    })

    name = event.get('spider', os.getenv('SCRAPY_SPIDER'))
    spider = process.create_crawler(name)

    process.crawl(spider)
    process.start()
    return json.dumps(spider.stats.get_stats(), default=str)


if __name__ == '__main__':
    event = {'spider': os.getenv('SCRAPY_SPIDER', 'tvinna')}
    run(event, '')
