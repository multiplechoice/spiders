import scrapy

from jobs.items import JobsItem
from jobs.common import decode_date_string


class MblSpider(scrapy.Spider):
    name = "mbl"

    def start_requests(self):
        urls = [
            'http://www.mbl.is/atvinna/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for job in response.css('.item-wrapper'):
            item = JobsItem()
            item['title'] = job.css('.title::text').extract_first(),
            item['company'] = job.css('div.company-wrapper span.company::text').extract_first(),
            item['url'] = response.urljoin(job.css('a::attr(href)').extract_first()),
            item['deadline'] = decode_date_string(job.css('span.date::text').extract_first()),
            yield item
