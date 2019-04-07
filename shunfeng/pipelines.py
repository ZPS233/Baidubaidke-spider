# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from shunfeng import settings
from shunfeng.items import CompanyBasicInfoItem
from shunfeng.items import PersonBasicInfoItem
from shunfeng.items import Kuaidi100Item
from shunfeng.items import ServiceItem
from shunfeng.items import TypeItem

class ShunfengPipeline(object):
    def __init__(self):
#        self.f = open('baike.txt', 'w')        
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
        if isinstance(item, Kuaidi100Item):
            #如果存在数据,判断是否重复,但是好像判断还是有问题
#            self.cursor.execute("SELECT company_chName,company_description FROM company;")
#            companyinfo = self.cursor.fetchall()
#            flag = 0
#            for info in companyinfo:
#                if (item['name'] in info[0]) or (item['name'] in info[1]):
#                    print('已经存在',info[0],'------',item['name'],'无法插入')
#                    item['description'] = item['description'] + info[1]
#                    sql = "UPDATE company SET company_description = '"+item['description']+"'where company_chName ='"+info[0]+"';"
#                    self.cursor.execute(sql)
#                    flag = 1
#            if flag == 0:
            #如果数据库里没有数据 则把快递100爬到的信息全部直接插入
            self.cursor.execute("SELECT MAX(company_id) FROM company")
            result = self.cursor.fetchall()[0]
            if None in result:
                company_id = 1
            else:
                company_id = result[0] + 1
            sql = """
                INSERT INTO company(company_id ,company_chName , company_description ) VALUES (%s, %s, %s)
                """
            self.cursor.execute(sql, (company_id, item['name'],item['description'] ))
        elif isinstance(item,TypeItem):
            #先判断在type表中该类型是否已经存在
            self.cursor.execute("SELECT type_id FROM type where type_name = '"+item['name']+"' ;")
            result_id = self.cursor.fetchone() 
            if None == result_id:
                #不存在,则存储
                #根据item['name']的prefix 找到 公司ID
                self.cursor.execute("SELECT company_id FROM company where company_chName like '%"+item['name'][0:2]+"%' ;")
                #假定该company一定存在,取[0]
                companyId = self.cursor.fetchone()[0]
                print('不存在该serviceType,存储,属于的companyID为:',companyId)
                #存储type
                sql = "INSERT INTO type(type_name,type_company_id) VALUES (%s, %s) "
                self.cursor.execute(sql, (item['name'],companyId))
                #ID自增,获得新存储的type的ID
                self.cursor.execute("SELECT MAX(type_id) FROM type")
                result_id = self.cursor.fetchone()
            else:
                print('重复的service-type')
            #存储对应service,先判断该service是否存在
            self.cursor.execute("SELECT * FROM service where service_name = '"+item['itemName']+"' and service_type_id = '"+ str(result_id[0]) +"' ;")
            result = self.cursor.fetchone() 
            if None == result:
                sql = "INSERT INTO service(service_name,service_type_id) VALUES (%s, %s) "
                self.cursor.execute(sql, (item['itemName'],result_id))
            else:
                print('重复的service')
            
        elif isinstance(item,ServiceItem):
            #service_name      sub_item_title    sub_item_des 
            #存储serviceitem,首先判断service是否存在
            #在service表中找到service_name与 item['service_name']一致的service_id
            self.cursor.execute("SELECT service_id FROM service where service_name = '"+item['service_name']+"' ;")
            result_id = self.cursor.fetchone() 
            if None == result_id:
                print('错误:缺少该service',item['service_name'])
            else:
                s = "SELECT * FROM service_item where service_item_name = %s and service_id = %s "
                self.cursor.execute(s,(item['sub_item_title'],result_id[0]))
                result = self.cursor.fetchone() 
                if None == result:
                    sql = """
                             INSERT INTO service_item(service_item_name,service_item_desc,service_id) VALUES (%s, %s, %s)
                          """
                    self.cursor.execute(sql, (item['sub_item_title'],item['sub_item_des'],result_id[0])) 
                else:
                    print('重复的service-item')

        elif isinstance(item, CompanyBasicInfoItem):
#            self.f.write(str(item))
#            self.f.write('\n\n')
#            self.cursor.execute("SELECT company_id,company_baike_description FROM company where company_chName like '% " + item['company_chName'][0:4] + " %' or company_description like '% " + item['company_chName'] + " %' ;")
            
            info = self.cursor.fetchone()
            print("#"*30,item['company_chName'],info)
            if None == info:
                print('发现了新公司!:',item['company_chName'])
                sql = """
                INSERT INTO company(company_chName ,company_enName ,
                                    company_headQuarterPlace , company_incorporationTime ,company_businessScope ,  company_type , company_slogan ,  company_annualTurnover ,company_chairMan , company_baike_description ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.cursor.execute(sql, (item['company_chName'],item['company_enName'],item['company_headQuarterPlace'],item['company_incorporationTime'],item['company_businessScope'],item['company_type'],item['company_slogan'],item['company_annualTurnover'],item['company_chairMan'],item['company_baike_description'] ))
            elif None == info[1]:
                print('更新公司数据:',companyId)
                sql = """
                        UPDATE company SET company_enName= %s , company_headQuarterPlace = %s , company_incorporationTime = %s ,
                        company_businessScope = %s , company_type = %s , company_slogan = %s, company_annualTurnover = %s, company_chairMan= %s, 
                        company_baike_description = %s WHERE company_id = %s 
                        """
                self.cursor.execute(sql, (item['company_enName'],item['company_headQuarterPlace'],item['company_incorporationTime'],item['company_businessScope'],item['company_type'],item['company_slogan'],item['company_annualTurnover'],item['company_chairMan'],item['company_baike_description'],companyId))
            else:
                print("#" * 20, "Got a duplict company!!", item['company_chName'])                
        elif isinstance(item, PersonBasicInfoItem):
#            self.f.write(str(item))
#            self.f.write('\n\n')
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
                
            else:
                print("#" * 20, "Got a duplict person!!", item['person_chName'])
        self.conn.commit()   
        return item
    
    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
        self.cursor.close()
#        self.f.close()