import os
from datetime import datetime
from scrapperize.spiders import MySpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# TESTAVIMO REŽIMAS True/False
is_test_mode = False

pages = []
for x in range(7):
    pages.append(f'https://elamed.com/dr/stati/?PAGEN_1={x+1}')
# source_language='ru'      -jeigu rusų kalba
# source_language='es'      -jeigu ispanų kalba
source_language = "ru"
# destination_language neliečiam
destination_language = "lt"
#  self.is_paging_exists = False    -jeigu nėra puslapiavimo
#  self.is_paging_exists = True     -jeigu yra
is_paging_exists = False

#  jeigu img                - img::attr('src')
#  jeigu                    - a::attr('href')
#  jeigu kitoks atributas   - div[atributas='reikšmė']
# kategorijos nuoroda a::attr('href')
category_links = ""
# kategorijos puslapio puslapiavimo nuoroda, jeigu nėra puslapiavimo - praleisti
category_pages = ""
# kategorijų puslapių straipsnio nnuoroda
category_page_posts = '#content .entry-title a::attr("href")'
# straipsnio pavadinimas
post_title = "h1.entry-title::text"
# straipsnio kategorija
post_category = ".b-cnt.breadcrumb::text"
# straipsnio nuotrauka img::attr('src')
post_image = "article img::attr('src')"
# straipsnio turinio blokas, galimai div[atributas='reikšmė']
post_content = "div#content article"

def crawl_wp15():
    current_time = datetime.now().strftime("%Y-%m-%d")
    FEED_URI = f"elamed_{current_time}_{destination_language}.csv"
    settings = get_project_settings()
    settings.update({"FEED_URI": FEED_URI})
    if os.path.isfile(FEED_URI):
        os.remove(FEED_URI)
    crawler = CrawlerProcess(settings=settings)
    crawler.crawl(
        crawler_or_spidercls = MySpider,
        pages=pages,
        is_test_mode=is_test_mode,
        is_paging_exists=is_paging_exists,
        source_language=source_language,
        destination_language=destination_language,
        category_links=category_links,
        category_pages=category_pages,
        category_page_posts=category_page_posts,
        post_title=post_title,
        post_category=post_category,
        post_image=post_image,
        post_content=post_content,
    )
    crawler.start()
