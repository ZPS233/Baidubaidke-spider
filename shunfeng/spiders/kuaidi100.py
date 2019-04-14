# -*- coding: utf-8-*-
# 616个公司
import scrapy
from shunfeng.items import Kuaidi100Item

class Kuaidi100Spider(scrapy.Spider):
    name = 'kuaidi100'
    start_urls = ['https://www.kuaidi100.com/all/','https://www.kuaidi100.com/all/xiaohongmao.shtml']
    links =[]
    links_name = []
    names = []
    def parse(self, response):
        if(response.url == 'https://www.kuaidi100.com/all/'):
            links = response.xpath('/html/body/div[3]/div[4]//a/@href').extract()
            links_title = response.xpath('/html/body/div[3]/div[4]//a/text()').extract()
            links2 = response.xpath('/html/body/div[3]/div[5]//a/@href').extract()
            links2_title = response.xpath('/html/body/div[3]/div[5]//a/text()').extract()
            links = links + links2
            self.links = links
            links_title = links_title + links2_title
            self.links_name = links_title
            print(len(links))
            for link in links:
                yield scrapy.Request(link, callback=self.parse,dont_filter=True)
        else:
            item = Kuaidi100Item()
            
            tel = response.xpath('//div[@class="ex-title"]/font/text()').extract()
            if tel != []:
                item['tel'] = tel[0]
            else:
                item['tel'] = None
            web = response.xpath('//div[@class="ex-title"]/a[1]/@href').extract()
            if web != [] and web[0] !='':
                item['web'] = web[0]
            else:
                item['web'] = None
            
            name = response.xpath('//h3/text()').extract()
            if len(name)!=1:
                index = self.links.index(response.url)
                item['name'] = self.links_name[index]
            else:
                item['name'] = name[0]
            
            if item['name'] not in self.names:
                self.names.append(item['name'])
                item['description'] = ''
                des_nodes = response.xpath('//div[@class = "ex-txt"]/*')
                for i,node in enumerate(des_nodes):
                    if(i>0):
                        nnn = node.xpath('./strong/text()').extract()
                        if nnn == []:
                            item['description'] = item['description'] + node.xpath('./text()').extract()[0]
                        else:
                            item['description'] = item['description'] + nnn[0]
                item['description'] = item['description'].replace(' ','')
                yield (item)