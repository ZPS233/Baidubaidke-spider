# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Kuaidi100Item(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()

class ShunfengItem(scrapy.Item):
    head = scrapy.Field()
    title = scrapy.Field()
    des = scrapy.Field()
    
    
class CompanyBasicInfoItem(scrapy.Item):
    company_id = scrapy.Field()
    company_chName = scrapy.Field()
    company_enName = scrapy.Field()
    company_headQuarterPlace = scrapy.Field()
    company_incorporationTime = scrapy.Field()
    company_businessScope = scrapy.Field()
    company_type = scrapy.Field()
    company_slogan = scrapy.Field()
    company_annualTurnover = scrapy.Field()
    company_chairMan = scrapy.Field()
    company_description = scrapy.Field()


class PersonBasicInfoItem(scrapy.Item):
    person_id = scrapy.Field()
    person_chName = scrapy.Field()
    person_nationality = scrapy.Field()
    #民族
    person_nation = scrapy.Field()
    person_birthPlace = scrapy.Field()
    person_birthDay = scrapy.Field()
    person_achiem = scrapy.Field()
    person_description = scrapy.Field()
    