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
        self.start_urls = ['https://www.sslproxies.org/']

    def parse(self, response):
        ip_adresses = response.css("tbody tr td:nth-child(1)::text").extract()
        ports = response.css("tbody tr td:nth-child(2)::text").extract()
        print(ip_adresses, ports)
        for count in range(len(ip_adresses)):
            https = f"{ip_adresses[count]}:{ports[count]}"
            yield {
                "https": https,
            }


current_time = datetime.now().strftime("%Y-%m-%d")
FEED_URI = f"ssl_posts.csv"
settings = get_project_settings()
settings.update({"FEED_URI": FEED_URI})
if os.path.isfile(FEED_URI):
    os.remove(FEED_URI)
crawler = CrawlerProcess(settings=settings)
crawler.crawl(
    crawler_or_spidercls=MySpider,
)
crawler.start()
