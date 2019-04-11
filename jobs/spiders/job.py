import dateutil.parser
import scrapy
import scrapy.spiders

from jobs.common import clean_html
from jobs.items import JobsItem


class JobSpider(scrapy.spiders.XMLFeedSpider):
    name = 'job.is'
    start_urls = ['https://atvinna.frettabladid.is/feeds/rss.xml']
    itertag = 'item'
    namespaces = [('atom', 'http://www.w3.org/2005/Atom')]

    def parse_node(self, response, node):
        item = JobsItem()
        item['spider'] = self.name
        item['url'] = url = node.xpath('guid/text()').extract_first()
        time_posted = node.xpath('pubDate/text()').extract_first()
        item['posted'] = dateutil.parser.parse(time_posted).isoformat()

        request = scrapy.Request(url, callback=self.parse_specific_job)
        request.meta['item'] = item
        yield request

    def parse_specific_job(self, response):
        item = response.meta['item']
        item['title'] = clean_html(response.css('.details-header__title::text').get())
        item['company'] = clean_html(response.css('.listing-item__info--item-company::text').get())
        item['description'] = clean_html(response.css('.details-body__content').get())
        yield item

