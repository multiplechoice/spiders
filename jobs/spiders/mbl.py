import scrapy

from jobs.common import decode_date_string, clean_html
from jobs.items import JobsItem


class MblSpider(scrapy.Spider):
    name = "mbl"
    start_urls = ['http://www.mbl.is/atvinna/']

    def parse(self, response):
        for job in response.css('.item-wrapper'):
            item = JobsItem()
            item['spider'] = self.name
            item['title'] = job.css('.title::text').extract_first()
            item['company'] = job.css('div.company-wrapper span.company::text').extract_first()
            item['deadline'] = decode_date_string(job.css('span.date::text').extract_first())

            url = response.urljoin(job.css('a::attr(href)').extract_first())
            item['url'] = url

            request = scrapy.Request(url, callback=self.parse_specific_job)
            request.meta['item'] = item
            yield request

    def parse_specific_job(self, response):
        item = response.meta['item']
        item['posted'] = decode_date_string(response.css('.ad_created::text').re(r'Sett inn: (.+)')[0])
        item['description'] = clean_html(response.css('.maintext-wrapper').extract())

        # some mbl items are just a title and an image, so we need to save the image and upload it to s3
        # so that we can show it later without hot-linking issues
        image_src = response.css('.img-responsive::attr(src)').extract_first()
        if image_src is not None:
            # adding to the `file_urls` causes this to be picked up by the FilesPipeline plugin
            item['file_urls'] = [response.urljoin(image_src)]

        yield item
