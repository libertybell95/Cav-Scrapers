# Scraper for old Milpacs (https://milpacs.treck.ninja/index.php?roster=master)

import re
import requests

from lxml import html


class roster:
    '''
    Get info from roster.

    Inputs:
        ID (str): [OPTIONAL] roster ID to query, if none provided uses 'master'
    '''

    def __init__(self, ID="master"):
        page = requests.get(f"https://milpacs.treck.ninja/index.php?roster={ID}")

        with open("forumEx.html", "rb") as file:
            stuff = file.readlines()

        self.html = html.parse("forumEx.html")

    def getIDs(self):
        pass

    def getInfo(self):
        '''
        UID, Rank, User, Position
        '''
        # for i in self.html.xpath('//tr'):
        #     print(i.xpath('//td/text()'))

        print(self.html.xpath('//div[@class="listBlock main"]//a[@class="PreviewTooltip"]/@href'))

if __name__ == "__main__":
    print(roster().getInfo())
