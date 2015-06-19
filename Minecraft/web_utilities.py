from git import Repo, GitCommandError
import urllib.request
import os

from Minecraft.file_utilities import resource_filter

import zipfile
# from scrapy import Spider, Item, Field

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
            resource_filter(target)


'''
# Going to wait on this until I get some sort of ok from Curse...
class Project(Item):
    url = Field()
    name = Field()

class CurseforgeSpider(Spider):
    home_url = r'http://minecraft.curseforge.com/mc-mods'

    def parse(self, response):
        for index in range(1, 16):

            return [Project(name=e.extract()) for e in response.css("h2 a::text")]


def curseforge_mod_scrape(page):

    # for
    pass
    # li.project-list-item:nth-child(1) > div:nth-child(2) > div:nth-child(2) > a:nth-child(1)
    # li.project-list-item:nth-child(2) > div:nth-child(2) > div:nth-child(2) > a:nth-child(1)
'''