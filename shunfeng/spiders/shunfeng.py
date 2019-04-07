# -*- coding: utf-8 -*-
#网页中的&nbsp;  抓过来会变成\xa0
#注意 因为pipeline里没有service判重 所以每运行一次 service都会多存储一次 type不会
#7个type  57个service 51
#[其中'大件入户' '' 跟后面item抓取的不一样,代码中修改]
#没有办法解决两个标签连续出现的顺序问题
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem

class ShunFengSpider(CrawlSpider):
    name = 'shun'
    start_urls = ['http://www.sf-express.com/cn/sc/express/cold_service/medical_service/temperature_control/']
    rules = (
        Rule(LinkExtractor(allow=r'http:\/\/www.sf-express.com\/cn\/sc\/express'), callback='parse_item', follow=True),
    )
    
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

    def parse_item(self, response):
        print(response.url)
        '''------------------------------------爬取顺丰type 及其对应service name-------------------------------------- '''
        if response.url == self.start_urls[0]:
            typeItem =  TypeItem()
            print(typeItem)
            #爬取type//*[@id="header"]/div/ul[1]/li[2]/div/div/div[1]/table[1]/tbody
            tableNodes = response.xpath('//*[@id="header"]/div/ul[1]/li[2]/div/div/div[1]/table')
            print('#################################')
            for tbody in tableNodes:
                prefix = '顺丰速运'+ '-'
                trs = tbody.xpath('./tr')
                for i,tr in enumerate(trs):
                    if i == 0:
                        #typename的第二个词 
                        prefix = prefix + (tr.xpath('./td/text()').extract()[0]) + '-'
                    else:
                        tds = tr.xpath('.//td')
                        for td in tds:
                            name = td.xpath('./p/text()').extract()[0]
                            if name == '\xa0':
                                typeItem['name'] = prefix  + '增值服务'
                            else:
                                typeItem['name'] = prefix  + name
                            servicenames = td.xpath('./ul//li/a/text()').extract()
                            for s in servicenames:
                                typeItem['itemName'] = s.replace('\n','').replace('\xa0','').replace(' ','').replace('\t','')
                                typeItem['name'] = typeItem['name'].replace('\n','').replace('\xa0','').replace(' ','').replace('\t','')
                                if typeItem['itemName'] == '大件入戶':
                                    typeItem['itemName'] = '大件入户'
                                if typeItem['itemName'] == '派件地址变更':
                                    typeItem['itemName'] = '派件地址变更服务'
                                print(typeItem)
                                yield typeItem
            '''------------------------------------爬取顺丰type 及其对应service name  end-------------------------------------- '''
            '''下面的代码因为带了else 所以是原用于和上面一起运行的 但是因为前期单独实验也需要单独运行,copy到了第三块--------------- '''                            
        else:
            item = ServiceItem()
            item['service_name'] = response.xpath('//*[@id="express_service_list"]/div/div[1]/h1/text()').extract()[0]
            contents = response.xpath('//div[@class="content-editor"]')
            for c in contents:
                item['sub_item_title'] = c.xpath('./h2/text()').extract()[0]
                ctext = ''
                pnodes = c.xpath('.//p')
                for pnode in pnodes:
                    cc = self.extractNodeText(pnode)
                    ctext = ctext + cc
                item['sub_item_des'] = ctext
                yield item 
        '''上面的代码因为带了else 所以是原用于和上面一起运行的 但是因为前期单独实验也需要单独运行,copy到了第三块--------------- ''' 
        '''------第三块------------------------------爬取顺丰service item  start-------------------------------------- '''
#        item = ServiceItem()
#        item['service_name'] = response.xpath('//*[@id="express_service_list"]/div/div[1]/h1/text()').extract()[0]
#        contents = response.xpath('//div[@class="content-editor"]')
#        for c in contents:
#            item['sub_item_title'] = c.xpath('./h2/text()').extract()[0]
#            ctext = ''
#            pnodes = c.xpath('.//p')
#            for pnode in pnodes:
#                cc = self.extractNodeText(pnode)
#                ctext = ctext + cc
#            item['sub_item_des'] = ctext
#            yield item 
        '''-----------------------------------------爬取顺丰service item  end-------------------------------------- '''