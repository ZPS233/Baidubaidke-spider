# -*- coding: utf-8 -*-
#selenium
#6type 27service 104item
#到付件 仓配一体 待取件 名字对不上
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
import scrapy
import urllib
from shunfeng.util import Extract

class YuanTongSpider(scrapy.Spider):
    name = 'yuantong'
    allowed_domains = ['www.yto.net.cn']
    start_urls = [#0-4 需要抽取的页面
            #圆通速递http://www.yto.net.cn/(express/(product|service))
            'http://www.yto.net.cn/express/product/timepro.html/',
            'http://www.yto.net.cn/express/product/addedservice.html/',
            'http://www.yto.net.cn/express/product/teseservice.html/',
            #圆通国际http://www.yto.net.cn/internat/
            'http://www.yto.net.cn/internat/service.html/',
            #特种物流
            'http://www.yto.net.cn/specialtraffic/about.html',
            
            #不需要抽取的页面
            'http://www.yto.net.cn/express/service/servicesupport.html/',
        
            'http://www.yto.net.cn/specialtraffic/contact.html/'
            ]
    newlinks = []
    
    def parse(self, response):
        prefix = '圆通速递-'
        if response.url in self.start_urls[:5]:
            typeNode =  response.xpath('//h4')
            typeItem = TypeItem()
            if response.url == self.start_urls[3]:
                typeItem['typeName'] = prefix + '国际服务'
            elif response.url == self.start_urls[4]:
                typeItem['typeName'] = prefix + '特种物流'
            else:
                typeItem['typeName'] = prefix + typeNode.xpath('./text()')[0].extract()
                
            serviceNodes = response.xpath('//div[@class = "fl product-text"]')
            for serviceNode in serviceNodes:
                s = serviceNode.xpath('./*')[0]
                #服务名称  服务简介
                name = s.xpath('./span/text()').extract()[0]
                if name == '通关服务' or name == '融合案例':
                    continue
                elif name == '仓配一体' :
                    name = '仓配一体服务'
                elif name == '到付件':
                    name = '到付件业务'
                elif name == '代取件':
                    name= '代取件业务'
                elif response.url == self.start_urls[4]:
                    name ='特种物流' + name
                typeItem['serviceName'] = prefix + name
#                desc = s.xpath('./div/text()').extract()[0]
                yield typeItem
                
            links = typeNode.xpath('..//a/@href').extract()
            for link in links :
                new_full_url = urllib.parse.urljoin('http://www.yto.net.cn', link)
                self.newlinks.append(new_full_url)
                yield scrapy.Request(new_full_url, callback=self.parse)
            print(self.newlinks) 
        elif response.url == self.start_urls[5]:
            typeItem = TypeItem()
            item = ServiceItem()
            typeItem['typeName'] = prefix + '服务支持'
            anodes = response.xpath('//div[@class ="tc"]')
            for a in anodes:
                typeItem['serviceName'] = prefix + a.xpath('./span/text()').extract()[0]
                yield typeItem
                item['serviceName'] = typeItem['serviceName']
                item['serviceItemName'] = '介绍'
                item['serviceItemDesc'] = a.xpath('./p/text()').extract()[0]
                yield item
        elif response.url == self.start_urls[6]:
            typeItem = TypeItem()
            item = ServiceItem()
            typeItem['typeName'] = prefix + '特种物流'
            typeItem['serviceName'] = prefix + '特种物流'+'联系方式'
            yield typeItem
            item['serviceName'] = typeItem['serviceName']
            item['serviceItemName'] = response.xpath('//p[@class = "subhead-name"]/text()').extract()[0]
            item['serviceItemDesc'] = response.xpath('//p[@class = "passages"]/text()').extract()[0]
            yield item 
        else:
            print('#############item页面',response.url)
            item = ServiceItem()
            if 'specialtraffic/about/' in response.url :
                item['serviceName'] = prefix +'特种物流'+ response.xpath('//p[@class = "subhead-name"]/text()').extract()[0]
                item['serviceItemName'] = '关于我们'
                ps = response.xpath('//p[@class = "passages"]/text()').extract()
                text = ''
                for p in ps:
                    text += p
                item['serviceItemDesc'] = text
                yield item 
            else:
                item['serviceName']= prefix + response.xpath('.//h4/text()').extract()[0]
                itemNodes = response.xpath('//div[@class = "service-item"]')
                if 'product/teseservice/tesejinji.html' in response.url:
                    for itemNode in itemNodes:
                        nodes = itemNode.xpath('.//p')
                        des = ''
                        for p in nodes:
                            if p == nodes[0]:
                                item['serviceItemName'] = Extract.extractNodeText(p)
                            else:
                                des = des + Extract.extractNodeText(p)
                        if '' == des:
                            continue
                        item['serviceItemDesc'] = des
                        yield item 

                else:
                    for itemNode in itemNodes:
                        titleNode = itemNode.xpath('./span/text()').extract()
                        if titleNode == []:
                            continue
                        else:
                            item['serviceItemName'] = titleNode[0]
                        desnodes = itemNode.xpath('.//p')
                        des = ''
                        for p in desnodes:
                            des = des + Extract.extractNodeText(p)
                        if '' == des:
                            continue
                        item['serviceItemDesc'] = des
                        yield item
        #圆通页面BUG 欧洲海外仓服务
        item = ServiceItem()
        item['serviceName'] = prefix + '欧洲海外仓服务'
        item['serviceItemName'] = '业务介绍'
        item['serviceItemDesc'] = '针对地区特色经济产品推出全新服务——特色经济产品个性化解决方案，通过“快递+电商”模式，打造“销售”、“运输”、“鲜配”一站式销售配送服务体系，整合圆通空运、陆运、冷链、仓储资源，利用国家工程实验室研发优势，为客户提供安全、高效、智能的快递运输服务'
        yield item
        item['serviceItemName'] = '服务品类'
        item['serviceItemDesc'] = '''1、生鲜产品：肉类、海鲜类；
                                    2、特殊包装产品：酒类、蛋类、鲜花类；
                                    3、水果产品；
                                    4、特产礼盒、节日礼盒产品；
                                    5、初级农产品：红薯、土豆、大蒜、药材等。'''
        yield item
        item['serviceItemName'] = '咨询方式'
        item['serviceItemDesc'] = '联系邮箱：00193553@yto.net.cn'
        yield item