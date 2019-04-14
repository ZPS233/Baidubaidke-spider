#开selenium  6 15 75
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem
from shunfeng.util import Extract
import scrapy
import urllib

class ShentongSpider(scrapy.Spider):
    name = 'shentong'
    allowed_domains = ['www.sto.cn']
    start_urls = ['http://www.sto.cn/Product/Index?idx=0']
    links = []
    def parse(self, response):
        prefix = '申通快递-'
        if response.url == self.start_urls[0]:
            divNodes =  response.xpath('//div[@class = "main_part nav_product_service clearfix"]/div')
            for node in divNodes :
                typeItem = TypeItem()
                title = node.xpath('./label/text()').extract()[0]
                typeItem['typeName'] = prefix + title
                childAs = node.xpath('.//div/a')
                for childA in childAs:
                    self.links.append(childA.xpath('./@href').extract()[0])
                    typeItem['serviceName'] = prefix + childA.xpath('./text()').extract()[0]
                    if typeItem['serviceName'] == prefix + '开放平台':
                        continue
                    yield typeItem
                
            for link in self.links:  
                new_full_url = urllib.parse.urljoin('http://www.sto.cn', link)
                yield scrapy.Request(new_full_url, callback=self.parse)

        item = ServiceItem()
        
        contentNode = response.xpath('//div[@class = "product_send"]')
        temp = contentNode.xpath('./div[@class = "cont_title"]/text()').extract()[0]
        changetext =''
        if temp == '24小时':
            changetext = '次日达'
        elif temp == '48小时':
            changetext = '隔日达'
        elif temp == '72小时':
            changetext = '件'
        elif temp == '申通打印专家':
            temp = '打印专家'
        item['serviceName'] = prefix + temp + changetext    
        item['serviceItemName'] = contentNode.xpath('./h4/text()').extract()[0]
        item['serviceItemDesc'] = Extract.extractNodeText(contentNode.xpath('./p'))
        yield item
        
        itemNodes = contentNode.xpath('.//div')
        for itemNode in itemNodes:
            if itemNode == itemNodes[0]:
                continue
            titleNode = itemNode.xpath('./h4')
            if titleNode == []:
                continue
            else:
                item['serviceItemName'] = titleNode.xpath('./text()').extract()[0]
            desnodes = itemNode.xpath('.//p')
            des = ''
            for p in desnodes:
                des = des + Extract.extractNodeText(p)
            if '' == des:
                continue
            item['serviceItemDesc'] = des
            yield item