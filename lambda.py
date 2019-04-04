from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

# Start sqlite3 fix
# https://stackoverflow.com/questions/52291998/unable-to-get-results-from-scrapy-on-aws-lambda
import types
import sys
sys.modules['sqlite'] = types.ModuleType('sqlite')
sys.modules['sqlite3.dbapi2'] = types.ModuleType('sqlite.dbapi2')
# End sqlite3 fix


def run(event, context):
    spider = event.get('spider', os.getenv('SCRAPY_SPIDER'))
    process = CrawlerProcess(get_project_settings())
    process.crawl(spider)
    process.start()
    return((event, context))


if __name__ == '__main__':
    event = {'spider': os.getenv('SCRAPY_SPIDER', 'tvinna')}
    run(event, '')
