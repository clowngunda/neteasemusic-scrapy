# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item,Field

class NeteasemusicItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #使用serializer序列化函数将其类型转变
    title=Field(serializer=str)
    singer=Field(serializer=str)
    credits=Field(serializer=str)
    link=Field()
    crawled=Field()
    spider=Field()


