# Scrape data off of forums. Will require credentials.json file to log into forums.

import requests
from lxml import html

def getThreads(ID,firstPageOnly=True):
    '''
    Get information for all the threads in a forum board.
    
    Inputs:
        ID (int): ID of the forum board to be searched.
        firstPageOnly (bool): [OPTIONAL] Whether the scraper should only search the first page of the board. Default is True.

    Output: List with each index containing the information following info on each forum post:
        0 (str): Thread name. (Ex: "2/A/1-7 PSG Assignment - S1 Completed")
        1 (int): Thread ID. (Ex: 58623)
        2 (str): Post author. (Ex: "Mackey.A")
    '''
    assert (type(ID) is int) # Ensure 'ID' is and integer.

    page = requests.get(f"https://7cav.us/forums/{ID}/")
    content = html.fromstring(page.content)

    titles = content.xpath("//div[@class='listBlock main']//a[@class='PreviewTooltip']")
    urls = content.xpath("//div[@class='listBlock main']//a[@class='PreviewTooltip']/@href")
    authors = content.xpath("//div[@class='listBlock main']//div[@class='secondRow']//a[@class='username']")


def getPosts(URL, pages=0):
    '''
    Gets information for all posts on a thread.

    Inputs:
        URL (str): URL of thread to be searched.
        pages (int): [OPTIONAL] Which pages to search, options are:
            0 [DEFAULT]: Search all pages
            1: Search first page only
            2: Search last page only

    Outputs: List with each index containing the following post information:
        0 (str): Contents, raw HTML.
        1 (str): Author (Ex: "Mackey.A")
        2 (str): Created Date (Ex: "Nov 14, 2019")
    '''
    pass

if __name__ == "__main__":
    getThreads(1)