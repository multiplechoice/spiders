import dateutil.parser
import scrapy.spiders

from jobs.items import JobsItem


class TvinnaSpider(scrapy.spiders.XMLFeedSpider):
    name = "tvinnafeed"
    start_urls = ['http://www.tvinna.is/feed/?post_type=job_listing']
    itertag = 'item'
    namespaces = [
        ('atom', 'http://www.w3.org/2005/Atom'),
        ('content', 'http://purl.org/rss/1.0/modules/content/'),
        ('dc', 'http://purl.org/dc/elements/1.1/'),
        ('slash', 'http://purl.org/rss/1.0/modules/slash/'),
        ('sy', 'http://purl.org/rss/1.0/modules/syndication/'),
        ('wfw', 'http://wellformedweb.org/CommentAPI/'),
    ]

    def parse_node(self, response, node):
        item = JobsItem()
        item['spider'] = self.name
        item['title'] = node.xpath('title/text()').extract_first()
        item['company'] = node.xpath('dc:creator/text()').extract_first()
        item['url'] = node.xpath('link/text()').extract_first()
        time_posted = node.xpath('pubDate/text()').extract_first()
        item['posted'] = dateutil.parser.parse(time_posted).isoformat()
        return item
