import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
from datetime import datetime
from scrapy.settings import Settings
import requests
import json
import urllib.request as urllib
from time import sleep
from textRefactorer.refactorer import TextRefactorer


class MySpider(scrapy.Spider):
    name = 'scraper'
    start_urls = ['https://ria.ru']

    def __init__(self):
        super().__init__()
        self.refactorer = TextRefactorer(
            source_language='ru',
            destination_language='en'
        )
        self.is_paging_exists = False
        self.css = {
            'category_links': ".footer__rubric-list-item a::attr('href')",
            'category_pages': "",
            'category_page_posts': ".rubric-list a::attr('href')",
            'post_title': "h1.article__title::text",
            'post_category': ".article__tags .article__tags-item::text",
            'post_image': ".article__announce media img::attr('src')",
            'post_content': "div.article__block[data-type='text']"
        }

    def parse(self, response):
        if len(self.start_urls) > 1:
            if self.is_paging_exists:
                yield self.follow_category_pages(response)
            else:
                yield self.follow_category_page(response)
        else:
            category_links = self.get_response_item_by_css(self.css['category_links'], response)
            for category_link in category_links:
                yield response.follow(category_link, self.follow_category_pages)

    async def follow_category_pages(self, response):
        if self.is_paging_exists:
            category_pages = self.get_response_item_by_css(self.css['category_pages'], response)
            for category_page in category_pages:
                yield response.follow(category_page, self.follow_category_page)
        else:
            yield self.follow_category_page(response)

    def follow_category_page(self, response):
        category_page_posts = self.get_response_item_by_css(self.css['category_page_posts'], response)
        for category_page_post in category_page_posts:
            yield response.follow(category_page_post, self.parse_category_page_post)

    def parse_category_page_post(self, response):
        title = self.get_response_first_item_by_css(self.css['post_title'], response)
        title = self.refactorer.translate_string(title)
        category_name = self.get_response_first_item_by_css(self.css['post_category'], response)
        category_name = self.refactorer.translate_string(category_name)
        post_slug = self.refactorer.string_to_slug(title)
        image_src = self.get_response_first_item_by_css(self.css['post_image'], response)
        if image_src == None:
            image_src = self.search_for_image_by_title(title)
        content = self.get_response_content_by_css(self.css['post_content'], response)

        yield {
            'category': category_name,
            'title': title,
            'post_slug': post_slug,
            'image_src': image_src,
            'image_alt': title,
            'post_content': content
        }

    def get_response_item_by_css(self, css, response):
        return response.css(css).extract()

    def get_response_first_item_by_css(self, css, response):
        return response.css(css).extract_first()

    def get_response_content_by_css(self, css, response):
        content_strings = response.css("css").extract()
        content_strings = content_strings[:-1]
        content = ''.join(content_strings)
        content = self.refactorer.translate_string(content)
        return content

    def search_for_image_by_title(self, title):
        search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
        search_term = title.split()[:3]
        search_term = '+'.join(search_term)
        subscription_key = '9460cb1db1384336bfcd2ac4819d0d5d'
        headers = {"Ocp-Apim-Subscription-Key": subscription_key}
        params = {"q": search_term,
                  "license": "public", "imageType": "photo"}
        request_response = requests.get(
            search_url, headers=headers, params=params)
        try:
            image_src = request_response.json()['value'][0]['contentUrl']
        except:
            image_src = ''
        return image_src


current_time = datetime.now().strftime("%Y-%m-%d")
fname = f"{current_time}_posts.csv"
settings = get_project_settings()
settings.update({'FEED_URI': fname})
if os.path.isfile(fname):
    os.remove(fname)
crawler = CrawlerProcess(settings)
crawler.crawl(MySpider)
crawler.start()