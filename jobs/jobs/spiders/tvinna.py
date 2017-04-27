import re

import scrapy

from jobs.items import JobsItem

months = [
    u'jan.',
    u'feb.',
    u'mars',
    u'apr\u00edl',
    u'ma\u00ed',
    u'j\u00fan\u00ed',
    u'j\u00fal\u00ed',
    u'\u00e1g\u00fast',
    u'sept.',
    u'okt.',
    u'n\u00f3v.',
    u'des.',
]


def decode_date_string(date_string):
    """
    Handles parsing the tvinna.is date strings into an ISO8601 compatible timestamp.

    Args:
        date_string (unicode): unicode string with the date extracted from tvinna.is

    Examples:
        >>> decode_date_string(u'27. apr\u00edl 2011')
        '2011-04-27'
    
    """
    date, localised_month, year = re.match(r'(\d+). ([\w.]+) (\d+)', date_string, re.UNICODE).groups()
    return '{}-{:02}-{:02}'.format(year, translate_month(localised_month), int(date))


def translate_month(month):
    """
    Translates the month string into an integer value 
    Args:
        month (unicode): month string parsed from the website listings.

    Returns:
        int: month index starting from 1
    
    Examples:
        >>> translate_month(u'jan.')
        1
    """
    return months.index(month) + 1


class TvinnaSpider(scrapy.Spider):
    name = "tvinna"

    def start_requests(self):
        urls = [
            'http://www.tvinna.is/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for job in response.css('.job-listing li a'):
            item = JobsItem()
            item['title'] = job.css('a h2::text').extract_first(),
            item['company'] = job.css('a p::text').extract_first().strip(),
            item['url'] = job.css('a::attr(href)').extract_first(),
            item['posted'] = decode_date_string(job.css('span.year::text').extract_first()),
            item['views'] = job.css('span.view-track::text').extract_first().strip()
            yield item

        next_page = response.css('div.next-link a::attr(href)').extract_first()
        if next_page is not None:
            yield scrapy.Request(next_page, callback=self.parse)
