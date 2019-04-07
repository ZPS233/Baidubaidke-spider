# -*- coding: utf-8 -*-
# 天天快递官网只有一个增值服务页面 即一个分类 五个服务 
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
import scrapy

class TiantianSpider(scrapy.Spider):
    name = 'tiantian'
    allowed_domains = ['www.ttkdex.com']
    start_urls = ['https://www.ttkdex.com/staticFiles/pages/expressServiceTab.html']
    links = []
    prefix = '天天快递-'
    def parse(self, response):
        typeNodes =  response.xpath('/html/body/div[1]/div[5]/div/div[1]/div')
        typeItem = TypeItem()
        serviceItem = ServiceItem()
        typeItem['typeName'] = self.prefix + '增值服务'
        for node in typeNodes:
            if node.xpath('./@class').extract()[0] == 'smallTitle':
                typeItem['serviceName'] = self.prefix + node.xpath('./text()').extract()[0]
                print(typeItem)
                serviceItem['serviceName'] = typeItem['serviceName']
                serviceItem['serviceItemName'] = '业务介绍'
            elif node.xpath('./@class').extract()[0] == 'smalldesc':
                serviceItem['serviceItemDesc'] = node.xpath('./text()').extract()[0]
                print(serviceItem)