# -*- coding: utf-8 -*-
# 7servicetype           34service[更改35toll..14 15.]           173serviceitem 
#为什么自定义函数抽不了有些node的字? 像国际的一些
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
import scrapy
import urllib
import re
class ZhongTongSpider(scrapy.Spider):
    name = 'zhongtong'
    allowed_domains = ['www.zto.com']
    home_page = 'https://www.zto.com/index.html'
    link = 'https://www.zto.com/js/morrow.js?v=ed4a55d041'
    cloudChamberurls = ['https://www.zto.com/business/cloudChamber.html',
                        'https://www.zto.com/business/serviceProducts.html',
                        'https://www.zto.com/business/serviceScope.html',
                        'https://www.zto.com/business/cooperativePartner.html']
    start_urls = [home_page]
#    start_urls = cloudChamberurls
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
#        print('提取结束 返回',summary_text)
        summary_text = re.sub(' +', '', summary_text)
        return summary_text.replace('\n','').replace('\xa0','').replace('\t','').replace('\r','').replace('\u3000','')
    
    def parse(self, response):
        prefix = '中通快递-'
        #首页 找Type
        if response.url == self.home_page:
            typeitem = TypeItem()
            #4个 总业务   div box-1 2 3 4
            typeNodes = response.xpath('//li[@class = "business"]/div/div')
            for typeNode in typeNodes:
#                prefix = prefix + typeNode.xpath('./span/text()').extract()[0] +'-'
                service_nodes = typeNode.xpath('./div/div')
                for service_node in service_nodes:
                    temp = service_node.xpath('./em/text()').extract()[0]
                    if  temp == '\xa0\xa0':
                        typeitem['typeName'] = prefix + '国际件'
                    elif temp == '仓储业务':
                        typeitem['typeName'] = prefix + temp
                        typeitem['serviceName'] = prefix + '中通云仓'
                        yield typeitem
                        break
                    else:
                        typeitem['typeName'] = prefix + temp
                        
                    herfs = service_node.xpath('.//a')
                    for h in herfs:
                        temp = h.xpath('./text()').extract()[0].strip()
                        if temp[:2] == 'To':
                            typeitem['serviceName'] = prefix + 'Toll Global Express(DPEX)'
                        elif temp == "开放平台" or temp == "快递管家":
                            break
                        else:
                            typeitem['serviceName'] = prefix + temp
                        yield typeitem
#                        print(typeitem['name'], typeitem['itemName'])
            yield scrapy.Request(self.link, callback=self.parse)
        elif response.url == self.link:
            body = str(response.body,'utf-8')
            regex = re.compile('\/business\/.*?html')
            links = regex.findall(body)
            for link in links:
                new_full_url = urllib.parse.urljoin('https://www.zto.com', link)
                yield scrapy.Request(new_full_url, callback=self.parse)
        elif response.url in self.cloudChamberurls:
            print('提取信息:',response.url)
            serviceItem = ServiceItem()
            if response.url == self.cloudChamberurls[0]:
                serviceItem['serviceName'] = prefix + '中通云仓'
                pnodes = response.xpath('//div[@class = "business-content"]//p')
                text = ''
                for p in pnodes:
                    if p.xpath('./@class').extract() == 'phone-number':
                        serviceItem['serviceItemName'] = '咨询热线'
                        serviceItem['serviceItemDesc'] = p.xpath('./em/text()').extract()[0]
                        yield serviceItem
                    elif p.xpath('./@class').extract() == 'address':
                        serviceItem['serviceItemName'] = '云仓地址'
                        serviceItem['serviceItemDesc'] = p.xpath('./span/text()').extract()[0]
                        yield serviceItem
                    else:
                        text = text + p.xpath('./text()').extract()[0]
                serviceItem['serviceItemName'] = '云仓介绍'
                serviceItem['serviceItemDesc'] = text
                yield serviceItem
            elif response.url == self.cloudChamberurls[1]:
                serviceItem['serviceName'] = prefix + '中通云仓'
                div1 = response.xpath('//div[@class ="business-box-detail"]')[0]
                div2 = response.xpath('//div[@class ="our-service-value"]')[0]
                for node in div1.xpath('.//dd'):
                    serviceItem['serviceItemName'] = node.xpath('./strong/text()').extract()[0]
                    serviceItem['serviceItemDesc'] = node.xpath('./p/text()').extract()[0]
                    yield serviceItem
                for node in div2.xpath('.//dd'):
                    serviceItem['serviceItemName'] = '服务价值-'+ node.xpath('./strong/text()').extract()[0]
                    serviceItem['serviceItemDesc'] = node.xpath('./p/text()').extract()[0]
                    yield serviceItem 
            elif response.url == self.cloudChamberurls[2]:
                serviceItem['serviceName'] = prefix + '中通云仓'
                serviceItem['serviceItemName'] = '服务范围'
                serviceItem['serviceItemDesc'] = response.xpath('//*[@id="content"]/div/div[2]/div/div/div/div[1]/p/text()').extract()[0]
                yield serviceItem
            else:
                serviceItem['serviceName'] = prefix + '中通云仓'
                serviceItem['serviceItemName'] = '退仓保障'
                serviceItem['serviceItemDesc'] = response.xpath('//*[@id="content"]/div/div[2]/div/div[1]/div[2]/div/p/text()').extract()[0]
                yield serviceItem
                nodes = response.xpath('.//dd')
                for node in nodes:
                    serviceItem['serviceItemName'] = '优势-' + node.xpath('./strong/text()').extract()[0]
                    serviceItem['serviceItemDesc'] = node.xpath('./p/text()').extract()[0]
                    yield serviceItem
        else :
            print('提取信息:',response.url)
            serviceItem = ServiceItem()
            serviceItem['serviceName'] = prefix + response.xpath('//h2[@class = "business-title"]/span/text()').extract()[0]
            serviceItemNodes = response.xpath('//div[@class = "business-box"]')
            for s in serviceItemNodes:
                #服务名称
                serviceItem['serviceItemName'] = s.xpath('./strong/text()').extract()[0]
                textNodes = s.xpath('.//div[@class="business-box-text"]/*')
                summary_text = ''
                for node in textNodes:
                    text = self.extractNodeText(node)
                    if text != '':
                        summary_text = summary_text + text + ' '
                if summary_text!= '':
                    serviceItem['serviceItemDesc'] = summary_text
                    yield serviceItem