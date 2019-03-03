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
    start_urls = ['https://memebase.cheezburger.com/page/%s' % page for page in range(1,2000)]

    def __init__(self):
        super().__init__()
        self.translator = Translator()

    def parse(self, response):
        links = response.css(
            ".title-sharing-buttons a::attr('href')").extract()
        for link in links:
            yield response.follow(link, self.parse_post_page)

    def parse_post_page(self, response):
        title = response.css(
            ".nw-post-title.post-header h1 span::text").extract_first()
        imgs_meta = response.css(".nw-post-content img.resp-media::attr('src')").extract()
        images = imgs_meta[1::2]
        featured_image = images[0]
        featured_image = f'{featured_image[:-1]}.jpg'
        content = ''
        if len(images) > 1:
            for image in images[1:]:
                content += f'<img src="{image[:-1]}.jpg"><br>'
        
        yield {'title': title,
               'featured_image': featured_image,
               'content': content
               }


current_time = datetime.now().strftime("%Y-%m-%d")
fname = f"{current_time}_memes.csv"
settings = get_project_settings()
settings.update({'FEED_URI': fname})
if os.path.isfile(fname):
    os.remove(fname)
crawler = CrawlerProcess(settings)
crawler.crawl(MySpider)
crawler.start()
