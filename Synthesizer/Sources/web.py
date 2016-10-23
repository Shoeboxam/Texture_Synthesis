from git import Repo, GitCommandError
import urllib.request
import os

from Synthesizer.sources.files import resource_filter

import zipfile
# from scrapy import Spider, Item, Field, Selector, Request
import scrapy

def clone_repo(url, target):
    repo_name = os.path.split(url)
    try:
        print("Cloning " + repo_name[1])
        Repo.clone_from(url, target)
    except GitCommandError:
        print("Repository " + repo_name[1] + " already cloned")


def download_minecraft(version, target):
    if not os.path.exists(target):
        os.makedirs(target)

        url = "https://s3.amazonaws.com/Minecraft.Download/versions/" + str(version) + '/' + str(version) + '.jar'
        urllib.request.urlretrieve(url, target + '\\minecraft.jar')
    else:
        print('Minecraft ' + str(version) + ' already installed, skipping download')

    if not os.path.exists(target + '\\assets'):
        with zipfile.ZipFile(target + '\\minecraft.jar') as file_zip:
            file_zip.extractall(target)
        resource_filter(target)


def key_repository_download(url, key_repository_path):
    if not os.path.exists(key_repository_path):
        urllib.request.urlretrieve(url, key_repository_path + '\\master.zip')
    with zipfile.ZipFile(key_repository_path + '\\master.zip') as file_zip:
        file_zip.extractall(key_repository_path)
        file_zip.close()

#     url = Field()
#     name = Field()


# class CurseforgeSpider(Spider):
#     name = 'Curseforge'
#     allowed_domains = ['minecraft.curseforge.com']
#     start_urls = [r'http://minecraft.curseforge.com/mc-mods']
#
#     def start_requests(self):
#         for url in self.start_urls:
#             yield Request(url, callback=self.parse)
#
#     def parse(self, response):
#         names = Selector(response).xpath('//x:div[2]/x:div[2]/x:a').extract()
#         links = Selector(response).xpath('//x:div[2]/x:div[2]/x:a/@href').extract()
#         auths = Selector(response).xpath('//x:div[2]/x:div[2]/x:span/x:a').extract()
#         self.logger.info('%s responded', response.url)
#
#         for name, link, auth in zip(names, links, auths):
#             mod = Project()
#             mod['name'] = name
#             mod['author'] = auth
#             mod['mod_page'] = link
#
#             yield mod
