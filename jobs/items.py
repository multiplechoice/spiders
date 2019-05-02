# -*- coding: utf-8 -*-
import scrapy


class JobsItem(scrapy.Item):
    spider = scrapy.Field()
    title = scrapy.Field()
    company = scrapy.Field()
    url = scrapy.Field()
    posted = scrapy.Field()
    deadline = scrapy.Field()
    description = scrapy.Field()
    file_urls = scrapy.Field()  # left for legacy
    image_urls = scrapy.Field()
    images = scrapy.Field()
    tags = scrapy.Field()
