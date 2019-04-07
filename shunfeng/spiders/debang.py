# -*- coding: utf-8   在xpath里的下标是从1开始  [1] [2] [3] -*-
# 命名比较标准了
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
from shunfeng.util import Extract
import scrapy

class DebangSpider(scrapy.Spider):
    name = 'debang'
    allowed_domains = ['www.deppon.com']
    start_urls = ['https://www.deppon.com/newwebsite/products',
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce917d4a04a2&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1',     
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce917e5204b2&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1',
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce917e7404b4&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1',
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce916eee03e6&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1']
    
    
    ValueAddedServicesrUrls = [
    #其他
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce917d4a04a2&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1',
    #代收货款        
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce917e5204b2&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1',
    #报价运输
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce917e7404b4&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1',
    #安全包装
    'https://www.deppon.com/newwebsite/products/detail?contentid=ff80808165ce45970165ce916eee03e6&tagname=%E4%BA%A7%E5%93%81%E4%BB%8B%E7%BB%8D-%E5%A2%9E%E5%80%BC%E6%9C%8D%E5%8A%A1'
    ]
    links = []
    prefix = '德邦快递-'
    def parse(self, response):
        if response.url == self.start_urls[0]:
            ulNodes =  response.xpath('//div[@class="row no-gutters align-content-center white"]')[1].xpath('.//ul') 
            for ul in ulNodes :
                typeItem = TypeItem()
                aNodes = ul.xpath('./li/a')
                for i,aNode in enumerate(aNodes):
                    if i == 0:
                        typeItem['typeName'] = self.prefix + aNode.xpath('./text()').extract()[0]
                    else:
                        if typeItem['typeName'] != '德邦快递-增值服务':
                            self.links.append(aNode.xpath('./@href').extract()[0])
                        typeItem['serviceName'] = self.prefix + aNode.xpath('./text()').extract()[0]
#                        yield typeItem
                        print(typeItem)
            typeItem['typeName'] = '德邦快递-增值服务'
            typeItem['serviceName'] = '超重货操作费'
            #yield typeItem
            #print('#',typeItem)
            for link in self.links:  
                link = link.replace('{{baseUrl}}','https://www.deppon.com/newwebsite')
                yield scrapy.Request(link, callback=self.parse)
        elif response.url in self.ValueAddedServicesrUrls:
            serviceItem = ServiceItem()
            if response.url == self.ValueAddedServicesrUrls[0]:
                nodes = response.xpath('//section[@class="component fs14 lh24 border_line"]')                
                for node in nodes:
                    text = ''
                    ps = node.xpath('.//p')
                    for p in ps:
                        t = Extract.extractNodeText(p)
                        ptext = p.extract()
                        if p == ps[-1]:
                            text = text+t
                            serviceItem['serviceItemDesc'] = text
                            text =''
                            print(serviceItem)
                        elif p == ps[0]:
                            serviceItem['serviceName'] = self.prefix + t
                            serviceItem['serviceItemName'] = '服务介绍'
                            text = ''
                        elif 'fs18 lh28' in ptext or '18px' in ptext:
                            if p != ps[1]:
                                serviceItem['serviceItemDesc'] = text
                                print(serviceItem)
                            serviceItem['serviceName'] = self.prefix + t
                            serviceItem['serviceItemName'] = '服务介绍'
                            text = ''
                        elif '24' in ptext or '15px' in ptext:
                            serviceItem['serviceItemDesc'] = text
                            print(serviceItem)
                            serviceItem['serviceItemName'] = t
                            text = ''
                        else:
                            text = text + t
                serviceItem['serviceName'] = '德邦快递-超重货操作费'
                serviceItem['serviceItemName'] = '服务介绍'
                serviceItem['serviceItemDesc'] = '单件货物重量大于500KG且小于等于1000KG范围内，收取超重货操作服务费100元/件；单件货物重量大于1000KG且小于等于2000KG范围内，收取超重货操作服务费200元/件；若一票货中多件货物满足超重货操作费收取标准，则这一票货收取的重货操作服务费为各件超重货操作费总和。'
                print(serviceItem)
            elif response.url == self.ValueAddedServicesrUrls[1]: 
                ps = response.xpath('//section[@class="component fs14 lh24 border_line"]/p')
                text = ''
                serviceItem['serviceName'] = self.prefix + '代收货款'
                for p in ps:
                    t = Extract.extractNodeText(p)
                    ptext = p.extract()
                    if p == ps[-1]:
                        text = text+t
                        serviceItem['serviceItemDesc'] = text
                        text =''
                        print(serviceItem)
                    elif p == ps[0]:
                        serviceItem['serviceItemName'] = t
                        text = ''
                    elif '28' in ptext:
                        serviceItem['serviceItemDesc'] = text
                        print(serviceItem)
                        serviceItem['serviceItemName'] = t
                        text = ''
                    else:
                        text = text + t
                serviceItem['serviceItemName'] = '服务介绍'
                serviceItem['serviceItemDesc'] = '提供“即日退”和“三日退”两种代收货款服务。替您收回货款后，在承诺的退款时效内将货款汇出，让您安全、及时地回笼资金'
                print(serviceItem)
            elif response.url == self.ValueAddedServicesrUrls[2]:
                ps = response.xpath('//section[@class="fs14 lh24 border_line"]/p')
                text = ''
                serviceItem['serviceName'] = self.prefix + '保价运输'
                for p in ps:
                    t = Extract.extractNodeText(p)
                    ptext = p.extract()
                    if p == ps[-1]:
                        text = text+t
                        serviceItem['serviceItemDesc'] = text
                        text =''
                        print(serviceItem)
                    elif p == ps[0]:
                        serviceItem['serviceItemName'] = t
                        text = ''
                    elif '28' in ptext:
                        serviceItem['serviceItemDesc'] = text
                        print(serviceItem)
                        serviceItem['serviceItemName'] = t
                        text = ''
                    else:
                        text = text + '\n' + t
                serviceItem['serviceItemName'] = '服务介绍'
                serviceItem['serviceItemDesc'] = '保价运输是指德邦与您共同确定的以托运人申明货物价值为基础的一种特殊运输方式。您向德邦声明托运货物的实际价值，若货物出险，即可获得我司的相应赔偿'
                print(serviceItem)
            else: 
                serviceItem['serviceName'] = self.prefix + '安全包装'
                serviceItem['serviceItemName'] = '服务介绍'
                serviceItem['serviceItemDesc'] = '德邦将为您的货物量身定制安全放心的包装解决方案，让您更安心'
                print(serviceItem)
                serviceItem['serviceItemName'] = '服务区域'
                serviceItem['serviceItemDesc'] = '中国大陆地区、香港地区'
                print(serviceItem)
                cardNodes = response.xpath('//div[@class = "card-body"]')
                for card in cardNodes:
                    if card.xpath('./h4') != []:
                        serviceItem['serviceItemName'] = card.xpath('./h4/text()').extract()[0]
                        serviceItem['serviceItemDesc'] = card.xpath('./p/text()').extract()[0]
                    elif card.xpath('./p[2]') != []:
                        serviceItem['serviceItemName'] = '包装材料介绍-' + card.xpath('./p[1]/text()').extract()[0]
                        serviceItem['serviceItemDesc'] = card.xpath('./p[2]/text()').extract()[0]
                    else:
                        serviceItem['serviceItemDesc'] = '新型塑料缓冲材料，质地轻、透明性好，良好的减震性、抗冲击性，是易碎易损货物包装的首选良材'
                        serviceItem['serviceItemName'] = '包装材料介绍-' + card.xpath('./p[1]/text()').extract()[0]
                    print(serviceItem)
        else:
            print('$$$$$',response.url)
            serviceItem = ServiceItem()
            #serviceName serviceItemName serviceItemDesc
            pNodes = response.xpath('//section[@class = "content_wrapper h-100"]/section/section/p')
            for i,p in enumerate(pNodes):
                if i == 0:
                    serviceItem['serviceName'] = self.prefix +Extract.extractNodeText(p)
                    print(serviceItem['serviceName'])
                if i == 1:
                    serviceItem['serviceItemName'] = '服务介绍'
                    serviceItem['serviceItemDesc'] = Extract.extractNodeText(p)
                    print(serviceItem)
            cardNodes = response.xpath('//div[@class = "card-body"]')
            for card in cardNodes:
                if card.xpath('./h4') == []:
                    continue
                else:
                    serviceItem['serviceItemName'] = '产品优势-' + card.xpath('./h4/text()').extract()[0]
                    if card.xpath('./p') == []:
                        serviceItem['serviceItemDesc'] = card.xpath('./ul/li/text()').extract()[0]
                    else:
                        serviceItem['serviceItemDesc'] = card.xpath('./p/text()').extract()[0]
                    print(serviceItem)