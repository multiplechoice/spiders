import re

import scrapy

from jobs.common import decode_date_string
from jobs.items import JobsItem


def get_page_id(page_title):
    """
    Extracts the page id from the page title

    Args:
        page_title (unicode): page title

    Returns:
        int: page id

    Examples:
        >>> get_page_id(u'Tvinna \u2013 Page 21')
        21
    """
    regex = re.compile(r'\d+')
    match = regex.search(page_title)
    if match is None:
        # the front page doesn't have the page # in it's title
        return 1
    return int(match.group(0))


class TvinnaSpider(scrapy.Spider):
    name = "tvinna"
    start_urls = ['http://www.tvinna.is/']

    def parse(self, response):
        for job in response.css('.job-listing li a'):
            item = JobsItem()
            item['title'] = job.css('a h2::text').extract_first()
            item['company'] = job.css('a p::text').extract_first().strip()
            item['url'] = job.css('a::attr(href)').extract_first()
            item['posted'] = decode_date_string(job.css('span.year::text').extract_first())
            item['views'] = job.css('span.view-track::text').extract_first().strip()
            yield item

        next_page = response.css('div.next-link a::attr(href)').extract_first()
        page_id = get_page_id(response.css('title::text').extract_first())
        if next_page is not None and page_id <= 2:
            yield scrapy.Request(next_page, callback=self.parse)
