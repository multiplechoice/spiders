from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os


def run(event, context):
    spider = event.get('spider', os.getenv('SCRAPY_SPIDER'))
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider)
    process.start()
    return((event, context))


if __name__ == '__main__':
    event = {'spider': os.getenv('SCRAPY_SPIDER', 'tvinna')}
    run(event, '')
