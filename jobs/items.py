# -*- coding: utf-8 -*-
import scrapy


class JobsItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    url = scrapy.Field()
    posted = scrapy.Field()
    deadline = scrapy.Field()
    views = scrapy.Field(serializer=int)
