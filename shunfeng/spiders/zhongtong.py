# -*- coding: utf-8   39service -*-
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
        summary_text = summary_text.replace('\n','').replace('\xa0','')
#        print('提取结束 返回',summary_text)
        return summary_text
    
    def parse(self, response):
        #首页 找Type
        if response.url == self.home_page:
            typeitem = TypeItem()
            #4个 总业务   div box-1 2 3 4
            typeNodes = response.xpath('//li[@class = "business"]/div/div')
            for typeNode in typeNodes:
                prefix = '中通快递-'
                prefix = prefix + typeNode.xpath('./span/text()').extract()[0] +'-'
                service_nodes = typeNode.xpath('./div/div')
                for service_node in service_nodes:
                    if service_node.xpath('./em/text()').extract()[0] == '\xa0\xa0':
                        typeitem['name'] = prefix + '国际件'
                    else:
                        typeitem['name'] = prefix + service_node.xpath('./em/text()').extract()[0]
                    herfs = service_node.xpath('.//a')
                    for h in herfs:
                        typeitem['itemName'] = h.xpath('./text()').extract()[0]
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
                serviceItem['service_name'] = '关于云仓'
                serviceItem['sub_item_title'] = '云仓介绍'#response.xpath('//h2[@class = "business-title"]/span/text()').extract()[0]
                pnodes = response.xpath('//div[@class = "business-content"]/p')
                text = ''
                for p in pnodes:
                    if p.xpath('./@class').extract() == 'phone-number':
                        serviceItem['sub_item_title'] = '咨询热线'
                        serviceItem['sub_item_des'] = p.xpath('./em/text()').extract()[0]
                        yield serviceItem
                    elif p.xpath('./@class').extract() == 'address':
                        serviceItem['sub_item_title'] = '云仓地址'
                        serviceItem['sub_item_des'] = p.xpath('./span/text()').extract()[0]
                        yield serviceItem
                    else:
                        text = text + p.xpath('./text()').extract()[0]
            elif response.url == self.cloudChamberurls[1]:
                serviceItem['service_name'] = '产品服务'
                nodes = response.xpath('.//dd')
                for node in nodes:
                    serviceItem['sub_item_title'] = node.xpath('./strong/text()').extract()[0]
                    serviceItem['sub_item_des'] = node.xpath('./p/text()').extract()[0]
                    yield serviceItem
            elif response.url == self.cloudChamberurls[2]:
                serviceItem['service_name'] = '服务范围'
                serviceItem['sub_item_title'] = '范围介绍'
                serviceItem['sub_item_des'] = response.xpath('//*[@id="content"]/div/div[2]/div/div/div/div[1]/p/text()').extract()[0]
                yield serviceItem
            else:
                serviceItem['service_name'] = '合作伙伴'
                serviceItem['sub_item_title'] = '退仓保障'
                serviceItem['sub_item_des'] = response.xpath('//*[@id="content"]/div/div[2]/div/div[1]/div[2]/div/p/text()').extract()[0]
                yield serviceItem
                nodes = response.xpath('.//dd')
                for node in nodes:
                    serviceItem['sub_item_title'] = node.xpath('./strong/text()').extract()[0]
                    serviceItem['sub_item_des'] = node.xpath('./p/text()').extract()[0]
                    yield serviceItem
        else :
            print('提取信息:',response.url)
            serviceItem = ServiceItem()
            serviceItem['service_name'] = response.xpath('//h2[@class = "business-title"]/span/text()').extract()[0]
            serviceItemNodes = response.xpath('//div[@class = "business-box"]')
            for s in serviceItemNodes:
                #服务名称
                serviceItem['sub_item_title'] = s.xpath('./strong/text()').extract()[0]
                textNodes = s.xpath('.//div[@class="business-box-text"]/p')
                summary_text = ''
                for node in textNodes:
                    
                    summary_text = summary_text + self.extractNodeText(node)
                        
                serviceItem['sub_item_des'] = summary_text.replace('\n','').replace('\xa0','').replace(' ','').replace('\t','').replace('\r','').replace('\u3000','')
                yield serviceItem