# -*- coding: utf-8 -*-
from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector
from DangdangSpider.items import DangdangspiderItem


class Dangdang(CrawlSpider):
    name = 'DangdangTOP'
    start_urls = ['http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-24hours-0-0-1-1']
    Link = 'http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-24hours-0-0-1-'
    def parse(self, response):
        item = DangdangspiderItem()
        selector = Selector(response)
        Books = selector.xpath('//div[@class="name"]')
        for EachBook in Books:
            ListNum = EachBook.xpath('../div[@class="list_num red"]/text()').extract() + EachBook.xpath('../div[@class="list_num "]/text()').extract()
            BookName = EachBook.xpath('../div[@class="name"]/a/text()').extract()
            Writer = EachBook.xpath('../div[@class="publisher_info"][1]/a/text()').extract()
            AllWriter = ''
            for each in Writer:
                AllWriter += each
            PublishTime = EachBook.xpath('../div[@class="publisher_info"]/span/text()').extract()
            Publisher = EachBook.xpath('../div[@class="publisher_info"][2]/a/text()').extract()
            RealPrice = EachBook.xpath('../div[@class="price"]/p/span[@class="price_r"]/text()').extract()
            NowPrice = EachBook.xpath('../div[@class="price"]/p[1]/span[@class="price_n"]/text()').extract()
            Discount = EachBook.xpath('../div[@class="price"]/p/span[@class="price_s"]/text()').extract()
            EPrice = EachBook.xpath('../div[@class="price"]/p[@class="price_e"]/span[@class="price_n"]/text()').extract()
            if not EPrice:
                EPrice = ''
            Tuijian = EachBook.xpath('../div[@class="star"]/span[@class="tuijian"]/text()').extract()
            BookUrl = EachBook.xpath('../div[@class="name"]/a/@href').extract()
            item['ListNumber'] = ListNum
            item['BookName'] = BookName
            item['Writer'] = AllWriter
            item['PublishTime'] = PublishTime
            item['Publisher'] = Publisher
            item['RealBookPrice'] = RealPrice
            item['NowBookPrice'] = NowPrice
            item['Discount'] = Discount
            item['EBookPrice'] = EPrice
            item['Tuijian'] = Tuijian
            item['BookUrl'] = BookUrl
            yield item
        for i in range (2,26):
            NewLink = str(i)
            yield Request(self.Link+NewLink,callback=self.parse)