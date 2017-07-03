# -*- coding: utf-8 -*-
import logging

from mappings import ScrapedJob
from mappings.utils import session_scope
from scrapy.exceptions import NotConfigured


class PostgresPipeline(object):
    def __init__(self, settings, stats):
        self.credentials = settings.get('PG_CREDS')
        self.scope = session_scope(self.credentials)
        self.stats = stats

    @property
    def logger(self):
        logger = logging.getLogger(self.__class__.__name__)
        return logging.LoggerAdapter(logger, {'pipeline': self})

    @classmethod
    def from_crawler(cls, crawler):
        if 'PG_CREDS' not in crawler.settings:
            raise NotConfigured

        return cls(settings=crawler.settings, stats=crawler.stats)

    def open_spider(self, spider):
        self.session = self.scope.__enter__()

    def close_spider(self, spider):
        self.scope.__exit__(None, None, None)

    def process_item(self, item, spider):
        job = ScrapedJob.from_dict(dict(item))

        query = self.session.query(ScrapedJob).filter(ScrapedJob.url == job.url)
        matched_job = query.one_or_none()
        if matched_job is None:
            # it's a new job, since it hasn't been seen before
            self.session.add(job)
            self.stats.inc_value('postgresql/add')
        else:
            if job.data != matched_job.data:
                # the scraped data is different
                matched_job.data = job.data
                self.logger.info('Replacing %r with %r', matched_job.data, job.data)
                self.stats.inc_value('postgresql/modify')
            else:
                self.stats.inc_value('postgresql/ignore')

        return item
