# -*- coding: utf-8 -13service *-
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
                        print(typeItem)
            typeItem['typeName'] = self.prefix + '物流业务'
            typeItem['serviceName'] = self.prefix + '合同物流'
            print(typeItem)
            typeItem['serviceName'] = self.prefix + '国际货代'
            print(typeItem)
            for link in self.links:  
                new_full_url = urllib.parse.urljoin('http://www.ems.com.cn/mainservice/ems/', link)
                print(new_full_url)
                yield scrapy.Request(new_full_url, callback=self.parse)
        else:
            ps = response.xpath('/html/body/div[2]/div[2]/*')
            serviceItem = ServiceItem()
            text = ''
            for p in ps:
                t = Extract.extractNodeText(p)
                t= t.replace('\t','').replace('\r','')
                pclassText = p.xpath('./@class').extract()
                pclass = ''
                if pclassText != []:
                    pclass = pclassText[0]
                    if p == ps[-2]:
                        text = text+t
                        serviceItem['serviceItemDesc'] = text
                        print(serviceItem)
                    elif p == ps[2]:
#                        print('############################3\n',t,'\n####################3')
                        serviceItem['serviceName'] = self.prefix + t
                        serviceItem['serviceItemName'] = '业务简介'
                    elif pclass == 'title' or pclass == 'title p_text_middle':
                        if p != ps[3]:
                            serviceItem['serviceItemDesc'] = text
                            print(serviceItem)
                        serviceItem['serviceItemName'] = self.prefix + t
                        text = ''
                    else:
                        text = text + t    
