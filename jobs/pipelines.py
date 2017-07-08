# -*- coding: utf-8 -*-
import logging

from mappings import ScrapedJob
from mappings.utils import session_scope
from scrapy.exceptions import NotConfigured
from scrapy.pipelines.files import FilesPipeline, S3FilesStore, FSFilesStore


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


class S3FilesStore_V4(S3FilesStore):
    AWS_ACCESS_KEY_ID = None
    AWS_SECRET_ACCESS_KEY = None
    AWS_DEFAULT_REGION = None

    def __init__(self, uri):
        super(S3FilesStore_V4, self).__init__(uri)
        import botocore.session
        session = botocore.session.get_session()
        self.s3_client = session.create_client(
            's3',
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
            region_name=self.AWS_DEFAULT_REGION
        )


class ImageDownloader(FilesPipeline):
    STORE_SCHEMES = {
        '': FSFilesStore,
        'file': FSFilesStore,
        's3': S3FilesStore_V4,
    }

    @classmethod
    def from_settings(cls, settings):
        s3store = cls.STORE_SCHEMES['s3']
        s3store.AWS_ACCESS_KEY_ID = settings['AWS_ACCESS_KEY_ID']
        s3store.AWS_SECRET_ACCESS_KEY = settings['AWS_SECRET_ACCESS_KEY']
        s3store.AWS_DEFAULT_REGION = settings['AWS_DEFAULT_REGION']
        s3store.POLICY = settings['FILES_STORE_S3_ACL']

        store_uri = settings['FILES_STORE']
        return cls(store_uri, settings=settings)

    def item_completed(self, results, item, info):
        completed_item = super(ImageDownloader, self).item_completed(results, item, info)
        images = []
        for image_details in completed_item[self.files_result_field]:
            image_details['s3_path'] = \
                'https://s3.eu-central-1.amazonaws.com/multiplechoice/images/' + image_details['path']
            images.append(image_details)
        completed_item[self.files_result_field] = images
        return completed_item
