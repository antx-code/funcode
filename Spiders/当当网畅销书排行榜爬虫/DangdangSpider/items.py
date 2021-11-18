# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

# import scrapy

from scrapy.item import Item,Field

class DangdangspiderItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ListNumber = Field()
    BookName = Field()
    Writer = Field()
    PublishTime = Field()
    Publisher = Field()
    RealBookPrice = Field()
    NowBookPrice = Field()
    Discount = Field()
    EBookPrice = Field()
    Tuijian = Field()
    BookUrl = Field()
