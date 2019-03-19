import json
import scrapy
from scrapperize.spiders import TextRefactorer
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class MySpider(scrapy.Spider):
    name = "scraper"

    def __init__(self):
        super().__init__()
        self.start_urls = ['https://techblog.willshouse.com/2012/01/03/most-common-user-agents/']

    def parse(self, response):
        user_agents = response.css("td.useragent::text").extract()
        for user_agent in user_agents:
            yield {
                "user_agent": user_agent,
            }


def crawl_user_agents():
    FEED_URI = f"user_agents.csv"
    settings = get_project_settings()
    settings.update({"FEED_URI": FEED_URI})
    if os.path.isfile(FEED_URI):
        os.remove(FEED_URI)
    crawler = CrawlerProcess(settings=settings)
    crawler.crawl(
        crawler_or_spidercls=MySpider,
    )
    crawler.start()