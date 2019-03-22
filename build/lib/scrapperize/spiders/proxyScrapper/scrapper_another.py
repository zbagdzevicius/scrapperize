import requests
import json
from time import sleep
import scrapy
from scrapy_splash import SplashRequest
from scrapperize.spiders import TextRefactorer
import os
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class MySpider(scrapy.Spider):
    name = "scraper"

    def __init__(self):
        super().__init__()
        self.start_urls = ['http://spys.one/proxies/']
    
    def start_requests(self):
        for url in self.start_urls:
            print(10*"\nGG")
            yield SplashRequest(url, self.parse,
                endpoint='',
                args={'wait': 5.5},
            )

    def parse(self, response):
        proxies = response.css('.spy14::text').extract()
        yield {
            "ports": proxies,
        }

def crawl_other_proxies():
    current_time = datetime.now().strftime("%Y-%m-%d")
    FEED_URI = f"another_proxies.csv"
    settings = get_project_settings()
    settings.update({"FEED_URI": FEED_URI})
    if os.path.isfile(FEED_URI):
        os.remove(FEED_URI)
    crawler = CrawlerProcess(settings=settings)
    crawler.crawl(
        crawler_or_spidercls=MySpider,
    )
    crawler.start()
