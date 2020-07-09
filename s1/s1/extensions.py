import scrapy
import os
import threading
import logging
from scrapy.statscollectors import StatsCollector
from scrapy.crawler import Crawler
from scrapy import signals

class CrawlTimeOut(object):

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        timer = cls()
        crawler.signals.connect(timer.scarpe_started, signals.spider_opened)
        return timer


    def scarpe_started(self, spider: scrapy.Spider):
        timeout = spider.settings.get("CRAWL_TIMEOUT", 5)
        logging.info("Crawl Timeout Started! Timeout: " + str(timeout))
        thread = threading.Timer(timeout, lambda: spider.crawler.engine.close_spider(spider, "Timeout"))
        thread.daemon = True
        thread.start()

