import json
import scrapy
from scrapperize.spiders import TextRefactorer
import os
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from requests import get

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


def crawl_proxies_from_urls():
    links = ['https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all', 'https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=10000&country=all', 'https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&timeout=10000&country=all']
    responses = []
    for link in links:
        responses.append(str(get(link).text))
    proxies = '\n'.join(responses)
    return proxies


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
    crawled_proxies_from_urls = crawl_proxies_from_urls()
    with open(FEED_URI, 'a+') as file:
        file.write('\n'+crawled_proxies_from_urls)
