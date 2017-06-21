# -*- coding: utf-8 -*-
from mappings import ScrapedJob
from mappings.utils import session_scope


class PostgresPipeline(object):
    def __init__(self, settings, stats):
        self.credentials = settings.get('PG_CREDS')
        self.scope = session_scope(self.credentials)
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
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
            if job.posted < matched_job.posted:
                # new record has an older timestamp
                matched_job.data['posted'] = job.posted
                # modifying the existing record will cause it to be marked as dirty
                # so when the session is committed it will emit an UPDATE for the row
                self.stats.inc_value('postgresql/modify')
            else:
                self.stats.inc_value('postgresql/ignore')

        return item
