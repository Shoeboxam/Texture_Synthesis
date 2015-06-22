from git import Repo, GitCommandError
import urllib.request
import os

from Minecraft.file_utilities import resource_filter

import zipfile
from scrapy import Spider, Item, Field, Selector, Request
import scrapy

def clone_repo(url, target):
    try:
        Repo.clone_from(url, target)
    except GitCommandError:
        print("Repository already exists, skipping clone")


def download_minecraft(version, target):
    if not os.path.exists(target):
        os.makedirs(target)

        url = "https://s3.amazonaws.com/Minecraft.Download/versions/" + str(version) + '/' + str(version) + '.jar'
        urllib.request.urlretrieve(url, target + '\\minecraft.jar')

    if not os.path.exists(target + '\\assets'):
        with zipfile.ZipFile(target + '\\minecraft.jar') as file_zip:
            file_zip.extractall(target)
            file_zip.close()
            resource_filter(target)


class Project(Item):
    url = Field()
    name = Field()


class CurseforgeSpider(Spider):
    name = 'Curseforge'
    allowed_domains = ['minecraft.curseforge.com']
    start_urls = [r'http://minecraft.curseforge.com/mc-mods']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        names = Selector(response).xpath('//x:div[2]/x:div[2]/x:a').extract()
        links = Selector(response).xpath('//x:div[2]/x:div[2]/x:a/@href').extract()
        auths = Selector(response).xpath('//x:div[2]/x:div[2]/x:span/x:a').extract()
        self.logger.info('%s responded', response.url)

        for name, link, auth in zip(names, links, auths):
            mod = Project()
            mod['name'] = name
            mod['author'] = auth
            mod['mod_page'] = link

            yield mod

# scrapy api imports
from scrapy import signals
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings


# list of crawlers
TO_CRAWL = [CurseforgeSpider]

# crawlers that are running
RUNNING_CRAWLERS = []

def spider_closing(spider):
    """
    Activates on spider closed signal
    """
    RUNNING_CRAWLERS.remove(spider)
    if not RUNNING_CRAWLERS:
        reactor.stop()

# set up the crawler and start to crawl one spider at a time
for spider in TO_CRAWL:
    settings = Settings()

    # crawl responsibly
    settings.set("USER_AGENT", "Shoeboxam")
    crawler = Crawler(settings)
    crawler_obj = spider()
    RUNNING_CRAWLERS.append(crawler_obj)

    # stop reactor when spider closes
    crawler.signals.connect(spider_closing, signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(crawler_obj)
    crawler.start()

# blocks process; so always keep as the last statement
reactor.run()