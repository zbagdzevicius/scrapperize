import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
from slugify import slugify
import re
from datetime import datetime
from scrapy.settings import Settings
from bs4 import BeautifulSoup
import requests
import json
import urllib.request as urllib


class MySpider(scrapy.Spider):
    name = 'fanpage_scraper'
    start_urls = ['http://fanpage.lt/populiariausi/?page13726=%s' % page for page in range(24,200)]

    def __init__(self):
        super().__init__()

    def parse(self, response):
        links = response.css(".list-post .grid-title a::attr('href')").extract()
        for link in links:
            yield {'url': link
            }

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
fname = f"{current_time}_pages_from_24_to_100.csv"
settings = get_project_settings()
settings.update({'FEED_URI': fname})
if os.path.isfile(fname):
    os.remove(fname)
crawler = CrawlerProcess(settings)
crawler.crawl(MySpider)
crawler.start()
