# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SinanewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()        #链接
    title = scrapy.Field()      #标题
    date = scrapy.Field()       #日期
    content = scrapy.Field()    #内容
    editor = scrapy.Field()     #编辑
