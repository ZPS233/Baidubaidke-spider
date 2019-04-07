# -*- coding: utf-8 -*-
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
from shunfeng.util import Extract
import scrapy
import urllib

class YundaSpider(scrapy.Spider):
    name = 'yunda'
    allowed_domains = ['www.yundaex.com']
    start_urls = ['http://www.yundaex.com/cn/jinji.php']
    links = []
    prefix = '韵达-'
    def parse(self, response):
        if response.url == self.start_urls[0]:
            boxNodes =  response.xpath('/html/body/div[1]/div/div[3]/ul/li[2]/div/dl[2]/div')[0:2]
            typeItem = TypeItem()
            for box in boxNodes :
                typeItem['typeName'] = self.prefix + box.xpath('./div[@class="title"]/text()').extract()[0]
                childDds = box.xpath('.//dd')
                for dd in childDds:
                    a = dd.xpath('./a')
                    typeItem['serviceName'] = self.prefix + a.xpath('./text()').extract()[0]
                    if typeItem['serviceName'] == '韵达-禁寄物品范围' :
                        continue
                    if typeItem['serviceName'] == '韵达-国际快递服务':
                        self.links.append(a.xpath('./@href').extract()[0])
                        continue
                    else:
                        self.links.append(a.xpath('./@href').extract()[0])
                    print(typeItem)
            serviceItem = ServiceItem()
            typeItem['typeName'] = self.prefix + '国际快递服务'
            linodes = response.xpath('/html/body/div[2]/div[1]/div[1]/ul[1]/li[10]/ul/li/ul/li')
            for li in linodes:
                a = li.xpath('./a')
                self.links.append(a.xpath('./@href').extract()[0])
                typeItem['serviceName'] = self.prefix + a.xpath('./text()').extract()[0]
                print(typeItem)
            #对在线服务中的禁品信息查询页面处理
            typeItem['typeName'] = self.prefix + '禁寄物品信息'
            expressPrinciple = response.xpath('/html/body/div[2]/div[2]/div[3]/div[3]')
            typeItem['serviceName'] = self.prefix + '收寄原则'
            print(typeItem)
            serviceItem['serviceName'] = self.prefix + '收寄原则'
            serviceItem['serviceItemName'] = '详细介绍'
            serviceItem['serviceItemDesc'] = Extract.extractNodeText(expressPrinciple.xpath('./p[1]')).replace('\t','').replace('\r','')
#            print(serviceItem)
            print(serviceItem['serviceName'],'#########',serviceItem['serviceItemName'],'######\n',serviceItem['serviceItemDesc'])
            wjcontents = response.xpath('/html/body/div[2]/div[2]/div[3]/div[2]/div')
            for content in wjcontents:
                title = content.xpath('./h4/text()').extract()
                if title != []:
                    typeItem['serviceName'] = self.prefix + title[0]
                    print(typeItem)
                    serviceItem['serviceName'] = self.prefix + title[0]
                    serviceItem['serviceItemName'] = '禁止寄递物品名录'
                    if content.xpath('./p[2]')!= []:
                        serviceItem['serviceItemDesc'] = Extract.extractNodeText(content.xpath('./p[2]')).replace('\t','').replace('\r','')
                    else:
                        serviceItem['serviceItemDesc'] = Extract.extractNodeText(content.xpath('./p[1]')).replace('\t','').replace('\r','')
#                    print(serviceItem)
                    print(serviceItem['serviceName'],'#########',serviceItem['serviceItemName'],'######\n',serviceItem['serviceItemDesc'])   
            for link in self.links:  
                new_full_url = urllib.parse.urljoin('http://www.yundaex.com/cn/', link)
                print(new_full_url)
                yield scrapy.Request(new_full_url, callback=self.parse)
        elif 'product_export' in response.url:
            serviceItem = ServiceItem()
            serviceItem['serviceName'] = self.prefix + response.xpath('/html/body/div[2]/div[2]/div[3]/h2/text()').extract()[0]
            contents = response.xpath('//div[@class="main_box_content_left"]')
            for c in contents:
                text =''
                ps = c.xpath('./p')
                for p in ps:
                    ptext = p.extract()
                    t = Extract.extractNodeText(p)
                    if p == ps[3]:
                        serviceItem['serviceItemName'] = self.prefix + t
                    elif '<p> *' in ptext:
                        serviceItem['serviceItemDesc'] = text
#                        print(serviceItem)
                        print(serviceItem['serviceName'],'#########',serviceItem['serviceItemName'],'######\n',serviceItem['serviceItemDesc'])
                    elif '<p>*' in ptext:
                        text = text+t
                    elif '26' in ptext:
                        text = text + t 
                    elif '：</p>' in ptext or '： </p>' in ptext:
                        serviceItem['serviceItemDesc'] = text
#                        print(serviceItem) 
                        print(serviceItem['serviceName'],'#########',serviceItem['serviceItemName'],'######\n',serviceItem['serviceItemDesc'])
                        serviceItem['serviceItemName'] = self.prefix + t
                        text = ''
        else:
            serviceItem = ServiceItem()
            serviceItem['serviceName'] = self.prefix + response.xpath('/html/body/div[2]/div[2]/div[3]/h2/text()').extract()[0]
            contents = response.xpath('//div[@class="main_box_content_left"]')
            for c in contents:
                text =''
                ps = c.xpath('./*')
                for p in ps:
                    t = Extract.extractNodeText(p)
                    if p == ps[-1]:
                        text = text+t
                        serviceItem['serviceItemDesc'] = text
#                        print(serviceItem)
                        print(serviceItem['serviceName'],'#########',serviceItem['serviceItemName'],'######\n',serviceItem['serviceItemDesc'])
                    elif p == ps[0]:
                        #中文的:号
                        t = t.split('：')[0].replace(' ','')
                        serviceItem['serviceItemName'] = self.prefix + t
                    elif 'h4' in p.extract():
                        t = t.split('：')[0].replace(' ','')
                        serviceItem['serviceItemDesc'] = text
#                        print(serviceItem) 
                        print(serviceItem['serviceName'],'#########',serviceItem['serviceItemName'],'######\n',serviceItem['serviceItemDesc'])
                        serviceItem['serviceItemName'] = self.prefix + t
                        text = ''
                    else:
                        text = text + t    