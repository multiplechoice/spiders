# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


def single_item_serializer(value):
    # values are nested inside a list: (u'Viltu vaxa me\xf0 Alvogen?',)
    # so need to return just the fist value when serializing
    return value[0]


class JobsItem(scrapy.Item):
    title = scrapy.Field(serializer=single_item_serializer)
    company = scrapy.Field(serializer=single_item_serializer)
    url = scrapy.Field(serializer=single_item_serializer)
    posted = scrapy.Field(serializer=single_item_serializer)
    deadline = scrapy.Field(serializer=single_item_serializer)
    views = scrapy.Field(serializer=int)
