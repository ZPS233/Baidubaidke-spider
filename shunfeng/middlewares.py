# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import time
from scrapy import http
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#print('中间件初始化')
#chrome_options = Options()
## 使用无头谷歌浏览器模式
#chrome_options.add_argument('--headless')  
#chrome_options.add_argument('--disable-gpu')
#chrome_options.add_argument('--no-sandbox')
##禁止加载图片
#prefs = {'profile.default_content_setting_values' : {'images' : 2} }
#chrome_options.add_experimental_option('prefs',prefs)
## 指定谷歌浏览器路径
#driver = webdriver.Chrome(chrome_options=chrome_options,executable_path='D:\Anaconda3\Scripts\chromedriver')
        
class RandomUserAgent(object):
    """Randomly rotate user agents based on a list of predefined ones"""
    def __init__(self, agents):
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getlist('USER_AGENTS'))

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', random.choice(self.agents))


class YuantongDownloaderMiddleware(object):
    def process_request(self, request, spider):
        driver.get(request.url)
        time.sleep(1)
        html = driver.page_source
        return http.HtmlResponse(url=request.url, body=html.encode('utf-8'), encoding='utf-8',request=request)

class ShunfengSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

