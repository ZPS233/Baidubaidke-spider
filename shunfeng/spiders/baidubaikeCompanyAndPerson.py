# -*- coding: utf-8 -*-
import re
import scrapy
from shunfeng.items import CompanyBasicInfoItem
from shunfeng.items import PersonBasicInfoItem
import urllib
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class BaiduBaikeSpider(CrawlSpider):
    name = 'baidu'
    allowed_domains = ["baike.baidu.com"]
    start_urls = [
            'https://baike.baidu.com/item/%E5%9C%86%E9%80%9A%E9%80%9F%E9%80%92/7616682?fromtitle=%E5%9C%86%E9%80%9A&fromid=4117164',
                  'https://baike.baidu.com/item/%E7%94%B3%E9%80%9A%E5%BF%AB%E9%80%92?fromtitle=%E7%94%B3%E9%80%9A&fromid=1415565',
                  'https://baike.baidu.com/item/%E5%96%BB%E6%B8%AD%E8%9B%9F/4785341',
                  'https://baike.baidu.com/item/%E9%99%88%E5%BE%B7%E5%86%9B/2383014',    
        'https://baike.baidu.com/item/%E5%BF%AB%E9%80%92/249416']
    rules = (Rule(LinkExtractor(allow=r'https:\/\/baike.baidu.com\/item\/'), callback='parse_item', follow=True),)
    #删掉 [1] 这样的上标
    def deleteSupNormal(self,elements):
        new_elements = list(elements)
        num = 0
        for i in range(len(elements)):
            value = elements[i].xpath('./@class').extract()
            if value!=[] and value[0] == 'sup--normal' :
                del new_elements[i-num]
                num = num+1
        return new_elements
    
    
    def extractNodeText(self,node):
#        print('开始提取    node为:',node.extract())
        summary_text = ''
        text = node.xpath('./text()').extract()
#        print('纯文本',text)
        
        elements = self.deleteSupNormal(node.xpath('./*'))
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
        
    def extractBasicInfo(self,response):
        basicInfo_name = response.xpath('//dt[@class="basicInfo-item name"]/text()').extract()
        for i,name in enumerate(basicInfo_name):
            basicInfo_name[i] = name.replace('\xa0','')
        
        basicInfo_value = [] 
        basicInfo_value_nodes = response.xpath('//dd[@class="basicInfo-item value"]')
        for node in basicInfo_value_nodes:
            #判断出现的第一个是标签还是文本,否则组合起来顺序不对,flag = 0代表 先出现标签
            flag = 1
            tempstr = str(node.extract()).split('>',1)
            if tempstr[1][0]=='<' :
                flag = 0;
            #判断结束            
            elements  =  self.deleteSupNormal(node.xpath('./*'))
            #如果标签没有子标签直接提取文字            
            value = node.xpath('./text()').extract()
            #如果存在子标签
            if elements != []:
                for i in range(len(elements)):
                    elements[i] = elements[i].xpath('./text()').extract()
                    e = elements[i][0]
#                    print('后',e)
                    value.insert(2*i+flag,e)
            temp = ''
            for i in range(len(value)):
                temp = temp + value[i]
            basicInfo_value.append(temp.replace('\n','').replace('\xa0',''))
        return basicInfo_name,basicInfo_value
        
    def extractLinkAndSendRequest(self,response):
        links = response.xpath('//a/@href').extract()
        for link in links:
            new_full_url = urllib.parse.urljoin('https://baike.baidu.com/', link)
#            if 'baidu.com/item/' in new_full_url: 
#            print(new_full_url)
            yield scrapy.Request(new_full_url, callback=self.parse)
        
    def parse_item(self, response):
        print('#####################start###########################')
#        print('网页:',response.url)
        title = response.xpath('/html/head/title/text()').extract()
        if title == []:
            title.append('')
#        print('网页标题:',title)
        page_keywords = response.xpath('/html/head/meta[@name = "keywords"]/@content').extract()
        if page_keywords == []:
            page_keywords.append('')
#        print('网页关键字:',page_keywords)
        des_node = response.xpath('//div[@class = "lemma-summary"]')
        page_description = ''
        if des_node != []:
            page_description = self.extractNodeText(des_node)
#        print('网页简介:',page_description)
        page_Info = [title[0],page_keywords[0],page_description]
        for info in page_Info:
            if re.search('((企业|公司).*(总裁|董事长))|((总裁|董事长).*(企业|公司))',info) and re.search('速运|速递|快递',info):
#                print('get a person page from:\n',page_Info)
                item = PersonBasicInfoItem()
                
                for sub_item in [ 
                        'person_chName','person_nationality','person_nation','person_birthPlace','person_birthDay','person_achiem']:
                    item[sub_item] = ''
                
                item['person_description'] = page_description
                basicInfo_name ,basicInfo_value = self.extractBasicInfo(response)
#                print(basicInfo_name)               
#                print(basicInfo_value)
                for i, info_name in enumerate(basicInfo_name):
                    if info_name == '中文名':
                        item['person_chName'] = basicInfo_value[i]
                    elif info_name == '国籍':
                        item['person_nationality'] = basicInfo_value[i]
                    elif info_name == '民族':
                        item['person_nation'] = basicInfo_value[i]
                    elif info_name == '出生地':
                        item['person_birthPlace'] = basicInfo_value[i]
                    elif info_name == '出生日期':
                        item['person_birthDay'] = basicInfo_value[i]
                    elif info_name == '主要成就':
                        item['person_achiem'] = basicInfo_value[i]
                    elif info_name == '简介':
                        item['person_description'] = basicInfo_value[i]
                if item['person_chName']!='' :
                    yield( item)
                    
#                links = response.xpath('//a/@href').extract()
#                for link in links:
#                    new_full_url = urllib.parse.urljoin('https://baike.baidu.com/', link)
#                    if 'baidu.com/item/' in new_full_url: 
#                        yield scrapy.Request(new_full_url, callback=self.parse)
#                break 
            
            elif re.search('(速运|速递|快递).*(企业|公司)',info):
#                print('get a company page from:\n',page_Info)
                item = CompanyBasicInfoItem()
                for sub_item in [ 
                        'company_chName','company_enName','company_headQuarterPlace','company_incorporationTime','company_businessScope','company_type','company_slogan','company_annualTurnover','company_chairMan']:
                    item[sub_item] = ''
                
                item['company_baike_description'] = page_description
                basicInfo_name ,basicInfo_value = self.extractBasicInfo(response)
#                print(basicInfo_name)               
#                print(basicInfo_value)
                for i, info_name in enumerate(basicInfo_name):
                    if info_name == '公司名称':
                        item['company_chName'] = basicInfo_value[i]
                    elif info_name == '外文名称':
                        item['company_enName'] = basicInfo_value[i]
                    elif (info_name == '总部地点') or  (info_name == '总部地址'):
                        item['company_headQuarterPlace'] = basicInfo_value[i]
                    elif info_name == '成立时间':
                        item['company_incorporationTime'] = basicInfo_value[i]
                    elif info_name == '经营范围':
                        item['company_businessScope'] = basicInfo_value[i]
                    elif info_name == '公司类型':
                        item['company_type'] = basicInfo_value[i]
                    elif info_name == '公司口号':
                        item['company_slogan'] = basicInfo_value[i]
                    elif info_name == '年营业额':
                        item['company_annualTurnover'] = basicInfo_value[i]
                    elif info_name == '董事长':
                        item['company_chairMan'] = basicInfo_value[i]
                if item['company_chName']!='' and item['company_baike_description']!= '' :
                    yield(item)
                    
#                links = response.xpath('//a/@href').extract()
#                for link in links:
#                    new_full_url = urllib.parse.urljoin('https://baike.baidu.com/', link)
#                    if 'baidu.com/item/' in new_full_url: 
#                        yield scrapy.Request(new_full_url, callback=self.parse)
                #不再循环关键字判断网页类型  
                break 
#        links = response.xpath('//a/@href').extract()
#        for link in links:
#            new_full_url = urllib.parse.urljoin('https://baike.baidu.com/', link)
#            if 'baidu.com/item/' in new_full_url: 
#                yield scrapy.Request(new_full_url, callback=self.parse)
        print('####################end############################')