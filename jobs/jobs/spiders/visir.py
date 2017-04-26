import scrapy
from jobs.items import JobsItem


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
            item['posted'] = posted,
            yield item
