import scrapy

from jobs.common import decode_date_string
from jobs.items import JobsItem


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
