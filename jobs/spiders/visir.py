import dateutil.parser
import scrapy
import logging
from jobs.items import JobsItem


class VisirSpider(scrapy.Spider):
    name = "visir"
    start_urls = ['https://job.visir.is/search-results-jobs/']

    def parse(self, response):
        for job in response.css('.thebox'):
            info = job.css('a')[1]

            item = JobsItem()
            item['spider'] = self.name
            item['url'] = url = info.css('a::attr(href)').extract_first()
            timestamp = job.css('td::text').re(r'[\d.]+')[0]
            item['posted'] = dateutil.parser.parse(timestamp, dayfirst=False).isoformat()
            
            line = '%s -> %s (%s)' % (timestamp, item['posted'], item['url'])
            self.log(line, logging.INFO)

            request = scrapy.Request(url, callback=self.parse_specific_job)
            request.meta['item'] = item
            yield request

        next_page = response.urljoin(response.css('.nextBtn a::attr(href)').extract_first())
        if next_page != response.url:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_specific_job(self, response):
        item = response.meta['item']
        item['company'] = response.css('.company-name::text').extract_first()
        item['title'] = response.css('h2::text').extract_first()
        yield item
