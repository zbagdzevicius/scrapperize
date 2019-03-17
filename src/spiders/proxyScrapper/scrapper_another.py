import requests
import json
from time import sleep
import scrapy
from src.spiders import TextRefactorer
import os
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from pprint import pprint


class MySpider(scrapy.Spider):
    name = "scraper"

    def __init__(self):
        super().__init__()
        self.start_urls = ['http://spys.one/proxies/']

    def parse(self, response):
        proxies = response.css('table:nth-of-type(2) tr:nth-of-type(4) td table tr td:nth-of-type(1) .spy14::text').extract()[1:]

        ports = response.css("tbody tr td:nth-child(2)::text").extract()
        for proxy in range(10):
            yield {
                "proxy": proxy,
            }


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
