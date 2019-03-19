import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
from googletrans import Translator
from slugify import slugify
import re
from datetime import datetime
from scrapy.settings import Settings
from bs4 import BeautifulSoup
import requests
import json
import urllib.request as urllib


class MySpider(scrapy.Spider):
    name = 'bbc_scraper'
    start_urls = []
    for x in range(1, 200):
        start_urls.append(
            f'http://www.anekdotaijums.lt/geriausi-anekdotai?page={x}')
        break

    def __init__(self):
        super().__init__()
        self.translator = Translator()

    def parse(self, response):
        jokes = response.css(".joke-link::text").extract()
        for joke in jokes:
            break
            yield {'joke': joke,
            'category': 'anekdotai',
            'title': joke.split(' ')[:5]}

def crawl_jokes():
    fname = f"jokes_posts.csv"
    settings = get_project_settings()
    settings.update({'FEED_URI': fname})
    if os.path.isfile(fname):
        os.remove(fname)
    crawler = CrawlerProcess(settings)
    crawler.crawl(MySpider)
    crawler.start()
