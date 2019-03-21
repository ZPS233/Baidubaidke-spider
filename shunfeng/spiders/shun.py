# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from shunfeng.items import ShunfengItem
#scrapy crawl shun --nolog
class ShunSpider(CrawlSpider):
    name = 'shun'
    start_urls = ['http://www.sf-express.com/cn/sc/express/express_service/mainland_area/cargo_express/']
    rules = (
        Rule(LinkExtractor(allow=r'http:\/\/www.sf-express.com\/cn\/sc\/express'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        print(response.url)
        item = ShunfengItem()
        item['head'] = response.xpath('//*[@id="express_service_list"]/div/div[1]/h1/text()').extract()
        contents = response.xpath('//div[@class="content-editor"]')
        for c in contents:
            item['title'] = c.xpath('./h2/text()').extract()   
            item['des'] = c.xpath('./p[2]/text()|./p[2]/span/text()').extract()     
            yield item 
            
