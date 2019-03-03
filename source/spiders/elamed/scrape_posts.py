import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
from translate import Translator
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
    name = 'elamed'
    start_urls = []
    for x in range(6):
        start_urls.append(f'https://elamed.com/dr/stati/?PAGEN_1={x+1}')
    print(start_urls)

    def __init__(self):
        super().__init__()
        self.domain = 'https://elamed.com'
        self.translator = Translator(to_lang='lt', from_lang='ru', provider='microsoft', secret_access_key='cf0e74ec363149678a101dc4dad90b5a')

    def parse(self, response):
        posts_links = response.css(
            '#content .entry-title a::attr("href")').extract()
        for post_link in posts_links:
            yield response.follow(self.domain + post_link, self.parse_post_page)

    def parse_post_page(self, response):
        try:
            category = 'Sveikata'
            title = response.css("h1.entry-title::text").extract_first()
            title = self.strip_braces(title)
            title = self.translated_data(title)
            post_slug = slugify(title)
            image_src = self.domain + \
                response.css('article img::attr("src")').extract_first()
            image_alt = response.css('article img::attr("alt")').extract_first()
            image_alt = self.translated_data(image_alt)
            if image_src == None:
                search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
                search_term = title.split()[:2]
                search_term = '+'.join(search_term)
                subscription_key = '9460cb1db1384336bfcd2ac4819d0d5d'
                headers = {"Ocp-Apim-Subscription-Key": subscription_key}
                params = {"q": search_term,
                        "license": "public", "imageType": "photo"}
                request_response = requests.get(
                    search_url, headers=headers, params=params)
                image_src = request_response.json()['value'][0]['contentUrl']
            content_strings = response.css("div#content article").extract_first()
            content = ''.join(content_strings)
            content = self.strip_before_translation(content)
            content = self.translated_data(content)
            # content_translations = self.translated_list_data(content.split('\n'))
            # content = []
            # for translation in content_translations:
            #     content.append(translation)
            # content = ''.join(content)
            post_content = self.strip_after_translation(content)
            post_excerpt = self.strip_excerpt(post_content)
        

            yield {
                'category': category,
                'title': title,
                'post_slug': post_slug,
                'image_src': image_src,
                'image_alt': image_alt,
                'post_content': post_content,
                'post_excerpt': post_excerpt
            }
        
        except Exception as e:
            print('***********************\n\n\n')
            print(e)
            print('\n***********************\n\n\n')
            

    def strip_anchors(self, data):
        p = re.compile(r'</?a.*?>')
        return p.sub('', data)

    def strip_braces(self, data):
        return data.replace('"', "'").replace('  ', ' ').replace('[', '').replace(']', '')

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
        p = re.compile(
            r"""<\s*?/?\s*?(?!(?:p|P|strong|Strong)\b)[a-zA-Z](?:[^>"']|"[^"]*"|'[^']*')*\s*?>""")
        return p.sub('', data)

    def remove_bad_content(self, data):
        return self.refactor_strong_tag(self.refactor_em_tag(self.refactor_p_tag(data)))

    def strip_after_translation(self, data):
        return self.strip_tags(self.refactor_span(self.strip_braces(self.remove_bad_content(data))))

    def strip_excerpt(self, data):
        p = re.compile(r'<[^>]*>')
        return p.sub('', data).replace('"', "'").replace('  ', ' ').replace('[', '').replace(']', '').strip()[0:300]+'...'

    def translated_data(self, data):
        return self.translator.translate(data)

    def translated_list_data(self, data_list):
        translated_data = []
        for data in data_list:
            translated_text = self.translator.translate(data)
            translated_data.append(translated_text)
        return translated_data



current_time = datetime.now().strftime("%Y-%m-%d")
fname = f"{current_time}_elamed_posts.csv"
settings = get_project_settings()
settings.update({'FEED_URI': fname})
if os.path.isfile(fname):
    os.remove(fname)
crawler = CrawlerProcess(settings)
crawler.crawl(MySpider)
crawler.start()
