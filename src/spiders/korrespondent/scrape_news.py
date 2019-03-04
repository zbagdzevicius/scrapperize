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
    for x in range(1,40):
        # start_urls.append(f'https://korrespondent.net/tag/1472/p{x}')
        start_urls.append(f'https://korrespondent.net/Default.aspx?page_id=60&lang=ru&stx=%D1%84%D0%B8%D1%82%D0%BD%D0%B5%D1%81&roi=0&st=1&p={x}')

    def __init__(self):
        super().__init__()
        self.translator = Translator()

    def parse(self, response):
        posts_links = response.css("div.article__title h3 a::attr('href')").extract()
        for post_link in posts_links:
            yield response.follow(post_link, self.parse_post_page)

    def parse_post_page(self, response):
        print(' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n\n\n', response.url, ' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n\n\n')
        title = response.css("h1.post-item__title::text").extract_first()
        title = self.translated_data(title)
        title = self.strip_braces(title)
        post_slug = slugify(title)
        try:
            image_src = response.css("img.post-item__big-photo-img::attr('src')").extract_first()
        except:
            image_src = response.css("div.post-item__photo.clearfix img::attr('src')").extract_first()
        if image_src == None:
            search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
            search_term = title.split()[:3]
            search_term = '+'.join(search_term)
            subscription_key = '9460cb1db1384336bfcd2ac4819d0d5d'
            headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
            params  = {"q": search_term, "license": "public", "imageType": "photo"}
            request_response = requests.get(search_url, headers=headers, params=params)
            try:
                image_src = request_response.json()['value'][0]['contentUrl']
            except:
                image_src = None
        content_strings = response.css("div.post-item__text p").extract()
        content_strings = content_strings[:-1]
        content = ''.join(content_strings)
        content = self.strip_before_translation(content)
        content = self.translated_data(content)
        post_content = self.strip_after_translation(content)
        post_excerpt = self.strip_excerpt(post_content)

        yield {
            'category': 'Socialiniai tinklai',
            'title': title,
            'post_slug': post_slug,
            'image_src': image_src,
            'image_alt': title,
            'post_content': post_content,
            'post_excerpt': post_excerpt
        }

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
        return self.translator.translate(data, src='ru', dest='lt').text
    
    def get_soup(self, url):
        return BeautifulSoup(urllib.urlopen(urllib.Request(url, headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
            })), 'html.parser')


current_time = datetime.now().strftime("%Y-%m-%d")
fname = f"{current_time}_korrespondent_posts.csv"
settings = get_project_settings()
settings.update({'FEED_URI': fname})
if os.path.isfile(fname):
    os.remove(fname)
crawler = CrawlerProcess(settings)
crawler.crawl(MySpider)
crawler.start()