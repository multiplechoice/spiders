import scrapy
from jobs.items import JobsItem


def decode_date_string(date_string):
    """
    Re-parses the job.visir.is date strings into a ISO8601 compatible timestamp.

    Args:
        date_string (unicode): unicode string with the date extracted from visir.is

    Examples:
        >>> decode_date_string(u'23.12.2015')
        '2015-12-23'

    """
    date, month, year = date_string.split(u'.')
    return '{}-{:02}-{:02}'.format(int(year), int(month), int(date))


class VisirSpider(scrapy.Spider):
    name = "visir"

    def start_requests(self):
        urls = [
            'https://job.visir.is/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for job in response.css('.job'):
            company, posted = job.css('.green::text').re(r'(.+)- Skr\xe1\xf0 (\d.+)')
            item = JobsItem()
            item['title'] = job.css('.jobtitill::text').extract_first(),
            item['company'] = company,
            item['url'] = job.css('.jobtitill::attr(href)').extract_first(),
            item['posted'] = decode_date_string(posted),
            yield item
