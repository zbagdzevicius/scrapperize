import json
import scrapy
from scrapy_splash import SplashRequest
from scrapperize.spiders import TextRefactorer
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class MySpider(scrapy.Spider):
    name = "scraper"

    def __init__(self):
        super().__init__()
        self.start_urls = []
        for x in range(10):
            self.start_urls.append(f"http://www.freeproxylists.net/?u=90&page={x+1}")
            break

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 5.5},
            )

    def parse(self, response):
        ip_adresses = response.css("table.DataGrid tr td").extract()
        yield {
            "proxy": ip_adresses,
        }
        # for count in range(len(ip_adresses)):
        #     proxy = f"{ip_adresses[count]}:{ports[count]}"
        #     yield {
        #         "proxy": proxy,
        #     }


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