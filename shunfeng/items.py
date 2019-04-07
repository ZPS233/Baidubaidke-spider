# -*- coding: utf-8 -*-

import scrapy

class Kuaidi100Item(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()
    
class TypeItem(scrapy.Item):
    typeName = scrapy.Field()
    serviceName = scrapy.Field()   

class ServiceItem(scrapy.Item):
    serviceName = scrapy.Field()
    serviceItemName = scrapy.Field()
    serviceItemDesc = scrapy.Field()

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
    company_baike_description = scrapy.Field()


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