import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
from googletrans import Translator
from slugify import slugify
import re
from datetime import datetime


class MySpider(scrapy.Spider):
    name = 'bbc_scraper'
    customs_settings = {
        'FEED_URI': '%(name)s_.xml'
    }
    start_urls = [
        'https://www.nytimes.com/']

    def __init__(self):
        super().__init__()
        self.translator = Translator()

    def parse(self, response):
        category_links = response.css(
            "div.split-6-layout.layout div.column")[0].css("ul.menu li a::attr('href')").extract()
        for category in category_links:
            yield response.follow(category, self.parse_posts)
            break

    def parse_posts(self, response):
        try:
            ten_latest_posts_links = response.css(
                "div.stream a.story-link::attr('href')").extract()
            for post_link in ten_latest_posts_links:
                yield response.follow(post_link, self.parse_post_page)
        except Exception as e:
            print(e)

    def parse_post_page(self, response):
        try:
            category = response.url.split('/')[6]
            category = self.translated_data(category)
            title = response.css("h1 span::text").extract_first()
            title = self.translated_data(title)
            title = self.strip_braces(title)
            post_slug = slugify(title)
            image_src = response.css(
                "figure.toneNews img::attr('src')").extract_first()
            content_strings = response.css(
                "div.StoryBodyCompanionColumn div p").extract()
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

        except Exception as e:
            print(e)

    def strip_anchors(self, data):
        p = re.compile(r'</?a.*?>')
        return p.sub('', data)

    def strip_classes(self, data):
        p = re.compile(r' class.{2}css\D.{7}\s.{9}')
        return p.sub('', data)
    
    def strip_tags(self, data):
        p= re.compile(r'<[^>]*>')
        return p.sub('',data)
    
    def strip_braces(self, data):
        return data.replace('"', "'").replace('  ',' ').replace('[','').replace(']','')

    def strip_before_translation(self, data):
        return self.strip_anchors(self.strip_classes(data))

    def refactor_p_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[pP]\s?>')
        return p.sub('</p>', data)

    def refactor_em_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[eE][mM]>')
        return p.sub('</em>', data)

    def refactor_strong_tag(self, data):
        p = re.compile(r'<\s*?\D\s*[sS][tT][rR][oO][nN][gG]>')
        return p.sub('</strong>', data)

    def refactor_classes(self, data):
        p = re.compile(r'\sclass\s?=\s?\Dcss.{7}\s.{9}')
        return p.sub('', data)
    
    def refactor_span(self, data):
        p = re.compile(r'<(\s?\W?\s?span\s?\W?\s?)>')
        return p.sub('', data)

    def remove_bad_content(self, data):
        return self.refactor_strong_tag(self.refactor_classes(self.refactor_em_tag(self.refactor_p_tag(data))))
    
    def strip_after_translation(self, data):
        return self.refactor_span(self.strip_braces(self.remove_bad_content(data)))
        
    def strip_excerpt(self, data):
        p= re.compile(r'<[^>]*>')
        return p.sub('',data).replace('"', "'").replace('  ',' ').replace('[','').replace(']','').strip()[0:100]+'...'

    def translated_data(self, data):
        return self.translator.translate(data, src='en', dest='lt').text


current_time = datetime.now().strftime("%Y-%m-%d")
fname = f"{current_time}_posts.json"
Settings = get_project_settings()
Settings.update({'FEED_URI': fname})
if os.path.isfile(fname):
    os.remove(fname)
crawler = CrawlerProcess(Settings)
crawler.crawl(MySpider)
crawler.start()