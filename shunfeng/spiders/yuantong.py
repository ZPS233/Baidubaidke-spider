# -*- coding: utf-8 -*-
#到付件 仓配一体 待取件 名字对不上
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
import scrapy
import urllib

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
            'http://www.yto.net.cn/specialtraffic/about.html/',
            #不需要抽取的页面
            'http://www.yto.net.cn/express/service/largeclientarea.html/',
            'http://www.yto.net.cn/express/service/servicesupport.html/',
            'http://www.yto.net.cn/internat/company/contactcompany.html/',
            'http://www.yto.net.cn/aviation/about.html/',
            'http://www.yto.net.cn/aviation/contact.html/',
            'http://www.yto.net.cn/specialtraffic/contact.html/'
            ]
    start_urls2 = [#0-4 需要抽取的页面
            
            #不需要抽取的页面
            'http://www.yto.net.cn/express/service/largeclientarea.html/',
            'http://www.yto.net.cn/internat/company/contactcompany.html/',
            'http://www.yto.net.cn/aviation/about.html/',
            'http://www.yto.net.cn/aviation/contact.html/',
            'http://www.yto.net.cn/specialtraffic/contact.html/'
            ]
    newlinks = []

#    'http://www.yto.net.cn/express/service/servicesupport.html/'
    def extractNodeText(self,node):
#        print('开始提取    node为:',node.extract())
        summary_text = ''
        text = node.xpath('./text()').extract()
#        print('纯文本',text)
        elements = node.xpath('./*')
        if len(elements) != 0:
            #判断出现的第一个是标签还是文本,否则组合起来顺序不对,flag = 0代表 先出现标签
            flag = 1
            tempstr = str(node.extract()).split('>',1)
            if tempstr[1][0]=='<' :
                flag = 0;
            #判断结束                                    
            for i in range(len(elements)):
                e = self.extractNodeText(elements[i])
#                print('插入之前',text)
                text.insert(2*i + flag , e)
#                print('插入之后',text)
            for t in text:
                summary_text = summary_text + t
        else:
            if text != []:
                summary_text = text[0]
        summary_text = summary_text.replace('\n','').replace('\xa0','')
#        print('提取结束 返回',summary_text)
        return summary_text
    
    def parse(self, response):
        if response.url in self.start_urls[:5]:
            if 'express' in response.url:
                typePrefix = '圆通-速递-'
            elif 'internat' in response.url:
                typePrefix = '圆通-国际-'
            elif 'specialtraffic' in response.url:
                typePrefix = '圆通-特种物流-'
            typeNode =  response.xpath('//h4')
            links = typeNode.xpath('..//a/@href').extract()
            for link in links :
                print('link------------',link)
                new_full_url = urllib.parse.urljoin('http://www.yto.net.cn', link)
                self.newlinks.append(new_full_url)
                
                yield scrapy.Request(new_full_url, callback=self.parse)
            print(self.newlinks)    
                
            typeName = typePrefix + typeNode.xpath('./text()')[0].extract()
            print(typeName)
            typeItem = TypeItem()
            typeItem['name'] = typeName
            serviceNodes = response.xpath('//div[@class = "fl product-text"]')
            for serviceNode in serviceNodes:
                s = serviceNode.xpath('./*')[0]
                #服务名称  服务简介
                name = s.xpath('./span/text()').extract()[0]
                typeItem['itemName'] = name
                if typeItem['itemName'] == '仓配一体' :
                    typeItem['itemName'] = '仓配一体服务'
                if typeItem['itemName'] == '到付件':
                    typeItem['itemName'] = '到付件业务'
                if typeItem['itemName'] == '代取件':
                    typeItem['itemName'] = '代取件业务'
#                desc = s.xpath('./div/text()').extract()[0]
                yield typeItem
        else:
            print('#############item页面',response.url)
            item = ServiceItem()
            item['service_name']= response.xpath('.//h4/text()').extract()[0]
            print(item['service_name'])

            itemNodes = response.xpath('//div[@class = "service-item"]')
            for itemNode in itemNodes:
                titleNode = itemNode.xpath('./span/text()').extract()
                if titleNode == []:
                    continue
                else:
                    item['sub_item_title'] = titleNode[0]
            
                desnodes = itemNode.xpath('.//p')
                des = ''
                for p in desnodes:
                    des = des + self.extractNodeText(p)
                if '' == des:
                    continue
                item['sub_item_des'] = des.replace(' ','')
                yield item 
            