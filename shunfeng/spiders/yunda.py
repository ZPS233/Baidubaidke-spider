# -*- coding: utf-8 -*-
#4servicetype 45service 118item  很多出口的service都是表格 爬不到item
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
    prefix = '韵达快递-'
    def parse(self, response):
        if response.url == self.start_urls[0]:
            boxNodes =  response.xpath('/html/body/div[1]/div/div[3]/ul/li[2]/div/dl[2]/div')[0:2]
            typeItem = TypeItem()
            for box in boxNodes :
                typeItem['typeName'] = self.prefix + box.xpath('./div[@class="title"]/text()').extract()[0]
                childDds = box.xpath('.//dd')
                for dd in childDds:
                    name = dd.xpath('./a/text()').extract()[0]
                    if name == '禁寄物品范围' or name == '分拨中心招商信息':
                        continue
                    else:
                        self.links.append(dd.xpath('./a/@href').extract()[0])
                        if name == '国际快递服务':
                            continue
                        elif name == '当天件快递':
                            name = name + '服务'
                        elif name == '项目快递管理综合服务':
                            name = '项目客户快递管理综合服务'
                    typeItem['serviceName'] = self.prefix + name
                    yield typeItem
            
            #把左栏中的国际快递服务单独拿出来做类型
            typeItem['typeName'] = self.prefix + '国际快递服务'
            linodes = response.xpath('/html/body/div[2]/div[1]/div[1]/ul[1]/li[10]/ul/li/ul/li')
            typeItem['serviceName'] = self.prefix + '国际快递业务'
            yield typeItem
            for li in linodes:
                a = li.xpath('./a')
                self.links.append(a.xpath('./@href').extract()[0])
                typeItem['serviceName'] = self.prefix + a.xpath('./text()').extract()[0]
                yield typeItem
                
            #对在线服务中的禁品信息查询页面处理
            typeItem['typeName'] = self.prefix + '禁寄物品'
            expressPrinciple = response.xpath('/html/body/div[2]/div[2]/div[3]/div[3]')
            typeItem['serviceName'] = self.prefix + '收寄原则'
            yield typeItem
            
            serviceItem = ServiceItem()
            serviceItem['serviceName'] = self.prefix + '收寄原则'
            serviceItem['serviceItemName'] = '详细介绍'
            serviceItem['serviceItemDesc'] = Extract.extractNodeText(expressPrinciple.xpath('./p[1]')).replace('\t','').replace('\r','')
            yield serviceItem
            
            wjcontents = response.xpath('/html/body/div[2]/div[2]/div[3]/div[2]/div')
            for content in wjcontents:
                title = content.xpath('./h4/text()').extract()
                if title != []:
                    typeItem['serviceName'] = self.prefix + title[0]
                    yield typeItem
                    serviceItem['serviceName'] = self.prefix + title[0]
                    serviceItem['serviceItemName'] = '禁止寄递物品名录'
                    if content.xpath('./p[2]')!= []:
                        serviceItem['serviceItemDesc'] = Extract.extractNodeText(content.xpath('./p[2]')).replace('\t','').replace('\r','')
                    else:
                        serviceItem['serviceItemDesc'] = Extract.extractNodeText(content.xpath('./p[1]')).replace('\t','').replace('\r','')
                    yield serviceItem
            for link in self.links:  
                new_full_url = urllib.parse.urljoin('http://www.yundaex.com/cn/', link)
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
                    if p == ps[0]:
                        serviceItem['serviceItemName'] = t
                    elif '<p> *' in ptext:
                        serviceItem['serviceItemDesc'] = text
                        yield serviceItem
                    elif '<p>*' in ptext:
                        text = text+t
                    elif '26' in ptext:
                        text = text + t 
                    elif '：</p>' in ptext or '： </p>' in ptext:
                        serviceItem['serviceItemDesc'] = text
                        yield serviceItem
                        serviceItem['serviceItemName'] = t.split('：')[0].replace(' ','')
                        text = ''
        else:
            serviceItem = ServiceItem()
            serviceItem['serviceName'] = self.prefix + response.xpath('/html/body/div[2]/div[2]/div[3]/h2/text()').extract()[0]
            if serviceItem['serviceName'] ==  self.prefix + '国际快递服务':
                serviceItem['serviceName'] = self.prefix + '国际快递业务'
            contents = response.xpath('//div[@class="main_box_content_left"]')
            for c in contents:
                text =''
                ps = c.xpath('./*')
                for p in ps:
                    t = Extract.extractNodeText(p)
                    if p == ps[-1]:
                        text = text+t
                        serviceItem['serviceItemDesc'] = text
                        yield serviceItem
                    elif p == ps[0]:
                        #中文的:号
                        t = t.split('：')[0].replace(' ','')
                        serviceItem['serviceItemName'] = t
                    elif 'h4' in p.extract():
                        t = t.split('：')[0].replace(' ','')
                        serviceItem['serviceItemDesc'] = text
                        yield serviceItem
                        serviceItem['serviceItemName'] = t
                        text = ''
                    else:
                        text = text + t    