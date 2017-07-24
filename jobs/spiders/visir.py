import urlparse

import dateutil.parser
import scrapy

from jobs.common import clean_html
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
            parsed_url = urlparse.urlparse(url)
            if parsed_url.query:
                # each search generates a new `searchId` value which messes up the storage layer
                item['url'] = url = parsed_url._replace(query='').geturl()

            timestamp = job.css('td::text').re(r'[\d.]+')[0]
            item['posted'] = dateutil.parser.parse(timestamp, dayfirst=True).isoformat()

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
        item['description'] = clean_html(response.css('div.displayField').extract())

        # sometimes visir items have an image/advert too
        image_src = response.css('a.info-picture::attr(href)').extract_first()
        if image_src is not None:
            item['file_urls'] = [image_src]

        yield item
