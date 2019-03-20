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
        self.start_urls = ['https://www.us-proxy.org/','https://www.socks-proxy.net/','https://www.sslproxies.org/']

    def parse(self, response):
        ip_adresses = response.css("tbody tr td:nth-child(1)::text").extract()
        ports = response.css("tbody tr td:nth-child(2)::text").extract()
        for count in range(len(ip_adresses)):
            proxy = f"{ip_adresses[count]}:{ports[count]}"
            yield {
                "proxy": proxy,
            }


def crawl_proxies():
    FEED_URI = f"proxies.csv"
    settings = get_project_settings()
    settings.update({"FEED_URI": FEED_URI})
    if os.path.isfile(FEED_URI):
        os.remove(FEED_URI)
    crawler = CrawlerProcess(settings=settings)
    crawler.crawl(
        crawler_or_spidercls=MySpider,
    )
    crawler.start()

crawl_proxies()