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
import traceback

class MySpider(scrapy.Spider):
    name = 'bbc_scraper'
    # customs_settings = {
    #     'FEED_URI': '%(name)s_.xml'
    # }
    start_urls = [
        'https://okdiario.com/internacional', 'https://okdiario.com/okdinero', 'https://okdiario.com/okdeportes', 'https://okdiario.com/cultura', 'https://okdiario.com/sociedad', 'https://okdiario.com/opinion', 'https://look.okdiario.com/', 'https://okdiario.com/recetas','https://okdiario.com/tag/mundial-2018-rusia']

    def __init__(self):
        super().__init__()
        self.translator = Translator()

    def parse(self, response):
        category_links = response.css("ul.okdiario-secciones-menu-navegacion-ul li a::attr(href)").extract()
        for category in category_links:
            yield response.follow(category, self.parse_posts)

    def parse_posts(self, response):
        try:
            posts_links = response.css("section.content article header.article-header h2 a::attr('href')").extract()
            for post_link in posts_links:
                yield response.follow(post_link, self.parse_post_page)
        except Exception as e:
            print(e)

    def parse_post_page(self, response):
        try:
            print(response.url.split('/'))
            category = response.url.split('/')[3]
            category = self.translated_data(category)
            title = response.css("h1.entry-title::text").extract_first()
            title = self.translated_data(title)
            title = self.strip_braces(title)
            post_slug = slugify(title)
            image_src = response.css("section.content img::attr('src')").extract_first()
            if image_src == None:
                search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
                search_term = title.split()[:2]
                search_term = '+'.join(search_term)
                subscription_key = '9460cb1db1384336bfcd2ac4819d0d5d'
                headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
                params  = {"q": search_term, "license": "public", "imageType": "photo"}
                request_response = requests.get(search_url, headers=headers, params=params)
                image_src = request_response.json()['value'][0]['contentUrl']
            content_strings = response.css("div.entry-content p").extract()
            content = ''.join(content_strings)
            content = self.strip_before_translation(content)
            content = self.translated_data(content)
            post_content = self.strip_after_translation(content)
            post_excerpt = self.strip_excerpt(post_content)

            yield {
                'category': category,
                'title': title,
                'post_slug': post_slug,
                'image_src': image_src,
                'image_alt': title,
                'post_content': post_content,
                'post_excerpt': post_excerpt
            }

        except Exception:
            print(traceback.print_exc(), "**********************\n\n\n*****************************\n\n\n***************************\n\n\n************************")

    def strip_anchors(self, data):
        p = re.compile(r'</?a.*?>')
        return p.sub('', data)
    
    def strip_braces(self, data):
        return data.replace('"', "'").replace('  ',' ').replace('[','').replace(']','')

    def strip_before_translation(self, data):
        return self.strip_anchors(data)

    def refactor_p_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[pP]\s?>')
        return p.sub('</p>', data)

    def refactor_em_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[eE][mM]\s?>')
        return p.sub('</em>', data)

    def refactor_strong_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[sS][tT][rR][oO][nN][gG]\s?>')
        return p.sub('</strong>', data)
    
    def refactor_span(self, data):
        p = re.compile(r'<\s?\W?\s?span\s?\W?\s?>')
        return p.sub('', data)
    
    def strip_tags(self, data):
        p= re.compile(r"""<\s*?/?\s*?(?!(?:p|P|strong|Strong)\b)[a-zA-Z](?:[^>"']|"[^"]*"|'[^']*')*\s*?>""")
        return p.sub('',data)

    def remove_bad_content(self, data):
        return self.refactor_strong_tag(self.refactor_em_tag(self.refactor_p_tag(data)))
    
    def strip_after_translation(self, data):
        return self.strip_tags(self.refactor_span(self.strip_braces(self.remove_bad_content(data))))
        
    def strip_excerpt(self, data):
        p= re.compile(r'<[^>]*>')
        return p.sub('',data).replace('"', "'").replace('  ',' ').replace('[','').replace(']','').strip()[0:100]+'...'

    def translated_data(self, data):
        return self.translator.translate(data, src='es', dest='en').text
    
    def get_soup(self, url):
        return BeautifulSoup(urllib.urlopen(urllib.Request(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
            })), 'html.parser')



current_time = datetime.now().strftime("%Y-%m-%d")
fname = f"{current_time}_okidario_posts.csv"
settings = get_project_settings()
settings.update({'FEED_URI': fname})
if os.path.isfile(fname):
    os.remove(fname)
crawler = CrawlerProcess(settings)
crawler.crawl(MySpider)
crawler.start()