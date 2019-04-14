# -*- coding: utf-8 -*-
#网页中的&nbsp;  抓过来会变成\xa0
#7个type  55个service 271item   两遍
#没有办法解决两个标签连续出现的顺序问题  不见了?
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
from shunfeng.util import Extract

class ShunFengSpider(CrawlSpider):
    name = 'shun'
    start_urls = ['http://www.sf-express.com/cn/sc/express/cold_service/medical_service/temperature_control/']
    rules = (
        Rule(LinkExtractor(allow=r'http:\/\/www.sf-express.com\/cn\/sc\/express'), callback='parse_item', follow=True),
    )
    
    def parse_item(self, response):
        prefix = '顺丰速运'+ '-'
        print(response.url)
        '''------------------------------------爬取顺丰type 及其对应service name-------------------------------------- '''
        if response.url == self.start_urls[0]:
            typeItem =  TypeItem()
            tableNodes = response.xpath('//*[@id="header"]/div/ul[1]/li[2]/div/div/div[1]/table')
            for tbody in tableNodes:
                trs = tbody.xpath('./tr')
                for tr in trs[1:]:
                    tds = tr.xpath('.//td')
                    for td in tds:
                        name = td.xpath('./p/text()').extract()[0]
                        if name == '\xa0':
                            typeItem['typeName'] = prefix  + '增值服务'
                        else:
                            typeItem['typeName'] = prefix  + name.replace('\n','').replace('\xa0','').replace(' ','').replace('\t','')
                        servicenames = td.xpath('./ul//li/a/text()').extract()
                        for s in servicenames:
                            s = s.replace('\n','').replace('\xa0','').replace(' ','').replace('\t','')
                            if s == '大件入戶':
                                s = '大件入户'
                            elif s == '前往国际网站' or s == '垫付货款':
                                continue
                            elif s == '派件地址变更':
                                s = '派件地址变更服务'                                
                            typeItem['serviceName'] = prefix + s
                            print(typeItem)
                            yield typeItem
        
        item = ServiceItem()
        item['serviceName'] = prefix + response.xpath('//*[@id="express_service_list"]/div/div[1]/h1/text()').extract()[0]
        contents = response.xpath('//div[@class="content-editor"]')
        for c in contents:
            item['serviceItemName'] = c.xpath('./h2/text()').extract()[0]
            ctext = ''
            pnodes = c.xpath('.//*')
            for pnode in pnodes[3:]:
                cc = Extract.extractNodeText(pnode)
                ctext = ctext + cc
            item['serviceItemDesc'] = ctext
            yield item 