# -*- coding: utf-8 -*-
#要运行两遍的  4 13 38
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
from shunfeng.util import Extract
import scrapy
import urllib

class EMSSpider(scrapy.Spider):
    name = 'ems'
    allowed_domains = ['www.ems.com.cn']
    start_urls = ['http://www.ems.com.cn/mainservice/ems/ci_chen_da.html',
                  'http://www.ems.com.cn/mainservice/cnpl/he_tong_wu_liu.html',
                  'http://www.ems.com.cn/mainservice/cnpl/guo_ji_wu_liu.html']
    links = []
    prefix = 'EMS-'
    def parse(self, response):
        if response.url == self.start_urls[0]:
            liNodes =  response.xpath('//ul[@class = "list_menu"]/li')
            typeItem = TypeItem()
            for li in liNodes :
                typeItem['typeName'] = self.prefix + li.xpath('./div/span/text()').extract()[0]
                childlis = li.xpath('./ul/li')
                for childli in childlis:
                    a = childli.xpath('./div/a')
                    if a!= []:
                        self.links.append(a.xpath('./@href').extract()[0])
                        typeItem['serviceName'] = self.prefix + a.xpath('./text()').extract()[0]
                        if typeItem['serviceName'] == self.prefix+ '鲜花礼仪':
                            typeItem['serviceName'] = self.prefix+'国内特快专递礼仪业务'
                        yield(typeItem)
            typeItem['typeName'] = self.prefix + '物流业务'
            typeItem['serviceName'] = self.prefix + '合同物流'
            yield(typeItem)
            typeItem['serviceName'] = self.prefix + '国际货代'
            yield(typeItem)
            for link in self.links:  
                new_full_url = urllib.parse.urljoin('http://www.ems.com.cn/mainservice/ems/', link)
                yield scrapy.Request(new_full_url, callback=self.parse)
        else:
            serviceItem = ServiceItem()
            ns = response.xpath('/html/body/div[2]/div[2]/*')
            text = ''
            if 'script' in ns[-1].extract():
                ns = ns[2:-1]
            else:
                ns = ns[2:]
            for n in ns:
                t = Extract.extractNodeText(n)
                nText = n.extract()
                if n == ns[0]:
                    serviceItem['serviceName'] = self.prefix + t
                    serviceItem['serviceItemName'] = '业务简介'
                elif n == ns[-1]:
                    text = text + t
                    serviceItem['serviceItemDesc'] = text
                    yield(serviceItem)
                elif 'title' in nText and n!= ns[1]:
                    serviceItem['serviceItemDesc'] = text
                    yield(serviceItem)
                    text = ''
                    serviceItem['serviceItemName'] =  t
                else:
                    text = text + t    
