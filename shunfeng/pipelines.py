# -*- coding: utf-8 -*-
import codecs
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from pymysql import connections
from shunfeng import settings
from shunfeng.items import ShunfengItem
from shunfeng.items import CompanyBasicInfoItem
from shunfeng.items import PersonBasicInfoItem
from shunfeng.items import Kuaidi100Item
class ShunfengPipeline(object):
    def __init__(self):
#        self.f = open('companyNameAndDescription.txt', 'w')
        self.conn = pymysql.connect(
            host=settings.HOST_IP,
#            port=settings.PORT,
            user=settings.USER,
            passwd=settings.PASSWD,
            db=settings.DB_NAME,
            charset='utf8mb4',
            use_unicode=True
            )   
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
#        movie_foreName = str(item['movie_foreName']).decode('utf-8')
        if isinstance(item, Kuaidi100Item):
            self.f.write(item['name']+'\t'+item['description']+'\n')
        elif isinstance(item, ShunfengItem):
            temp = str(item['head'])+'\t'+str(item['title']) + '\t'+ str(item['des'])+'\n'
            print(temp)
            self.file.write(temp)
            return item
        elif isinstance(item, CompanyBasicInfoItem):
            self.cursor.execute("SELECT company_chName FROM company;")
            companyList = self.cursor.fetchall()
#            print('名字列表',companyList)
            if (item['company_chName'],) not in companyList :
                # get the id in table company
                self.cursor.execute("SELECT MAX(company_id) FROM company")
                result = self.cursor.fetchall()[0]
                if None in result:
                    company_id = 1
                else:
                    company_id = result[0] + 1
                
                sql = """
                INSERT INTO company(company_id ,company_chName ,company_enName ,
                                    company_headQuarterPlace , company_incorporationTime ,company_businessScope ,  company_type , company_slogan ,  company_annualTurnover ,company_chairMan , company_description ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (company_id, 
                                          item['company_chName'],item['company_enName'],item['company_headQuarterPlace'],item['company_incorporationTime'],item['company_businessScope'],item['company_type'],item['company_slogan'],item['company_annualTurnover'],item['company_chairMan'],item['company_description'] ))
                self.conn.commit()
            else:
                print("#" * 20, "Got a duplict company!!", item['company_chName'])
        elif isinstance(item, PersonBasicInfoItem):
            self.cursor.execute("SELECT person_chName FROM person;")
            personList = self.cursor.fetchall()
#            print('名字列表',personList)
            if (item['person_chName'],) not in personList :
                # get the id in table company
                self.cursor.execute("SELECT MAX(person_id) FROM person")
                result = self.cursor.fetchall()[0]
                if None in result:
                    person_id = 1
                else:
                    person_id = result[0] + 1
                
                sql = """
                INSERT INTO person(person_id ,person_chName ,person_nationality ,person_nation,person_birthPlace,person_birthDay,person_achiem,person_description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (person_id, item['person_chName'],item['person_nationality'],item['person_nation'],item['person_birthPlace'],item['person_birthDay'],item['person_achiem'],item['person_description'] ))
                self.conn.commit()
            else:
                print("#" * 20, "Got a duplict person!!", item['person_chName'])
        else:
            print("Skip this page because wrong category!! ")
        return item
    
    def close_spider(self, spider):
        if spider.name == 'wuliu':
            self.conn.close()
#        elif spider.name == 'kuaidi100':
#            self.f.close()