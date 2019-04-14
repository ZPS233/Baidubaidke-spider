# -*- coding: utf-8 -*-
import re
class Extract():
    #用于从网页的某节点中提取文字(从每个子节点中取到文字并组装在一起),但是针对两个标签接连出现且标签内都包含文字的情况 会出现组合顺序错误
    @staticmethod
    def extractNodeText(node):
        summary_text = ''
        text = node.xpath('./text()').extract()
        elements = node.xpath('./*')
        if len(elements) != 0:
            #判断出现的第一个是标签还是文本,否则组合起来顺序不对,flag = 0代表 先出现标签
            flag = 1
            tempstr = str(node.extract()).split('>',1)
            if tempstr[1][0]=='<' :
                flag = 0;
            #判断结束                                    
            for i in range(len(elements)):
                e = Extract.extractNodeText(elements[i])
#                print('插入之前',text)
                text.insert(2*i + flag , e)
#                print('插入之后',text)
            for t in text:
                summary_text = summary_text + t
        else:
            if text != []:
                summary_text = text[0]
        summary_text = re.sub(' +', '', summary_text)
        summary_text = summary_text.strip()
        return summary_text.replace('\n','').replace('\xa0','').replace('\t','').replace('\r','').replace('\u3000','')