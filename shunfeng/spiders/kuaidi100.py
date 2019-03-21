# -*- coding: utf-8 -*-
import scrapy
from shunfeng.items import Kuaidi100Item

class Kuaidi100Spider(scrapy.Spider):
    name = 'kuaidi100'
    start_urls = ['https://www.kuaidi100.com/all/']
    
    def parse(self, response):
        if(response.url == 'https://www.kuaidi100.com/all/'):
            links = response.xpath('/html/body/div[3]/div[4]//a/@href').extract()
            links2 = response.xpath('/html/body/div[3]/div[5]//a/@href').extract()
            links.append(links2)
            print(len(links))
            for link in links:
                yield scrapy.Request(link, callback=self.parse)
        else:
            item = Kuaidi100Item()
            name = response.xpath('/html/body/div[3]/div[6]/div[1]/div/h3/text()').extract()
            description = response.xpath('/html/body/div[3]/div[6]/div[1]/div/p/text()').extract()
            item['name'] = name[0]
            item['description'] = description[0]
            yield item