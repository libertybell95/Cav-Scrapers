#!/usr/bin/env python3

import json
import os
import re
import html

import requests
from bs4 import BeautifulSoup


class forum:
    def __init__(self, credentialsJSON=False):
        self.s = requests.Session()  # Requests session.

        try:
            if credentialsJSON == False:
                # Get current working directory at file execution.
                initDir = os.getcwd()
                dname = os.path.dirname(os.path.abspath(__file__))
                # Change current working directory to this file's location
                os.chdir(dname)
                # External credentials file.
                with open("credentials.json") as file:
                    c = json.load(file)
                os.chdir(initDir)  # Change working directory back to initDir.
            else:
                with open(credentialsJSON) as file:
                    c = json.load(file)
        except IOError:  # File cannot be opened.
            assert False, f"credentials.json file not found in {credentialsJSON or os.getcwd()}"
        except ValueError:  # File cannot be parsed.
            assert False, "Error with formatting of credentials.json file."

        auth = {
            "login": c["user"],
            "register": 0,
            "password": c["pass"],
            "remember": 1
        }

        self.s.post("https://7cav.us/login/login",
                    data=auth, allow_redirects=False)

    def threads(self, forumID, pages=1):
        '''
        Gets list of threads in a forum.

        Inputs:
            forumID (int): ID number of forum to parse.
            pages (int): What pages to parse.
                If value is 0, will parse all available pages.
                If value > 0, will parse all pages up to that value.

        Output: List with each index being a thread with the following info:
            ID (str): ID number of thread.
            Author (str): Author of thread (forum username).
            Title (str): Title of thread.
            Replies (str): Number of replies.
        '''
        HTML = self.s.get(f"https://7cav.us/forums/{forumID}/").text
        try:
            totalPages = int(re.findall(r"Page \d+ of (\d+)", HTML)[0])
        except:
            totalPages = 1

        def threadList(HTML):
            soup = BeautifulSoup(HTML, features="lxml")
            rawThreads = soup.find_all("li", class_="discussionListItem")

            threads = []
            for t in rawThreads:
                info = re.findall(
                    r"data-author=\"(.*?)\".*id=\"thread-(\d+)\"", str(t))[0]
                threads.append({
                    "ID": info[1],
                    "Author": info[0],
                    "Title": t.find("a", {"class": "PreviewTooltip"}).text,
                    "Replies": re.findall(r"Replies.*(\d+?)", str(t))[0]
                })

            return threads

        output = []
        if pages == 0:  # Get all pages
            print(f"Parsing {totalPages} pages")
            for p in range(1, totalPages+1):
                HTML = self.s.get(
                    f"https://7cav.us/forums/{forumID}/page-{p}").text
                output += threadList(HTML)
                print(f"Parsed page {p}")
        elif pages == 1:  # If getting only 1 page
            HTML = self.s.get(f"https://7cav.us/forums/{forumID}/").text
            output = threadList(HTML)
        else:  # If getting more then 1 page
            if pages > totalPages:
                print(
                    f"There aren't this many pages in the forum. Actual total: {totalPages}\nExiting.")
                return None
            else:
                for p in range(1, pages+1):
                    HTML = self.s.get(
                        f"https://7cav.us/forums/{forumID}/page-{p}").text
                    output += threadList(HTML)
                    print(f"Parsed page {p}")

        return output

    def posts(self, threadID, pages=1):
        '''
        Gets list of posts in a thread.

        Inputs:
            threadID (int): ID number of thread to parse.
            pages (int): What pages to parse.
                If value is 0, will parse all available pages.
                If value > 0, will parse all pages up to that value.
                If value < 0, will parse __ last pages. Ex: -2 gets last 2 pages on thread.
                    Also orders posts from newest to oldest.

        Output: List with each index being a post (dict) with the following info:
            ID (str): ID number of post.
            Author (str): Author of post (forum username).
            RawContent (str): Raw post content, with HTML tags.
            Content (str): Post content, HTML tags removed.
            MilpacIDs (list): List of all milpac IDs found in the post content.
        '''

        HTML = self.s.get(f"https://7cav.us/threads/{threadID}/").text
        try:
            totalPages = int(re.findall(r"Page \d+ of (\d+)", HTML)[0])
        except:
            totalPages = 1
        
        def postList(HTML):
            soup = BeautifulSoup(HTML, features="lxml")
            rawPosts = soup.find_all("li", class_="message")

            posts = []
            for p in rawPosts:
                info = re.findall(r"data-author=\"(.*?)\".id=\"post-(\d+)\"", str(p))[0]
                content = p.find("blockquote")

                posts.append({
                    "ID": info[1],
                    "Author": info[0],
                    "Content": content.text.replace("\n\n", "\n").replace("\t", ""),
                    "RawContent": str(content),
                    "MilpacIDs": [re.findall(r"uniqueid=(\d+)", i.get("href"))[0] for i in content.find_all("a") if "uniqueid" in i.get("href")]
                })

            return posts

        output = []
        if pages == 0:  # Get all pages
            print(f"Parsing {totalPages} pages.")
            output += postList(HTML)
            print("Parsed page 1")
            for p in range(2, totalPages+1):
                HTML = self.s.get(f"https://7cav.us/threads/{threadID}/page-{p}").text
                output += postList(HTML)
                print(f"Parsed page {p}")
        elif pages > 0:  # If getting more then 1 page
            if pages > totalPages:
                print(
                    f"There aren't this many pages in the forum. Actual total: {totalPages}\nExiting.")
                return None
            else:
                print(f"Parsing {pages} pages.")
                output += postList(HTML)
                print("Parsed page 1")
                for p in range(2, pages+1):
                    HTML = self.s.get(f"https://7cav.us/threads/{threadID}/page-{p}").text
                    output += postList(HTML)
                    print(f"Parsed page {p}")
        elif pages < 0:
            print(f"Parsing last {abs(pages)} pages.")
            for p in range(1, totalPages+1)[::-1][:pages]:
                HTML = self.s.get(f"https://7cav.us/threads/{threadID}/page-{p}").text
                output += postList(HTML)[::-1]
                print(f"Parsed page {p}")

        return output

class conversations:
    # TODO: Document class methods
    def __init__(self, credentialsJSON=False):
        self.s = requests.Session()  # Requests session.

        try:
            if credentialsJSON == False:
                # Get current working directory at file execution.
                initDir = os.getcwd()
                dname = os.path.dirname(os.path.abspath(__file__))
                # Change current working directory to this file's location
                os.chdir(dname)
                # External credentials file.
                with open("credentials.json") as file:
                    c = json.load(file)
                os.chdir(initDir)  # Change working directory back to initDir.
            else:
                with open(credentialsJSON) as file:
                    c = json.load(file)
        except IOError:  # File cannot be opened.
            assert False, f"credentials.json file not found in {credentialsJSON or os.getcwd()}"
        except ValueError:  # File cannot be parsed.
            assert False, "Error with formatting of credentials.json file."

        auth = {
            "login": c["user"],
            "register": 0,
            "password": c["pass"],
            "remember": 1
        }

        self.s.post("https://7cav.us/login/login",
                    data=auth, allow_redirects=False)

    def parse(self, ID, pages=1):
        '''
        Gets list of messages in a conversation.

        Inputs:
            ID (int): ID number of conversation to parse.
            pages (int): What pages to parse.
                If value is 0, will parse all available pages.
                If value > 0, will parse all pages up to that value.
                If value < 0, will parse __ last pages. Ex: -2 gets last 2 pages on conversation.
                    Also orders messages from newest to oldest.

        Output: List with each index being a post (dict) with the following info:
            ID (str): ID number of message.
            Author (str): Author of message (forum username).
            RawContent (str): Raw message content, with HTML tags.
            Content (str): Message content, HTML tags removed.
            MilpacIDs (list): List of all milpac IDs found in the message content.
        '''

        HTML = self.s.get(f"https://7cav.us/conversations/{ID}/").text
        
        try:
            totalPages = int(re.findall(r"Page \d+ of (\d+)", HTML)[0])
        except:
            totalPages = 1

        
        # Get info on all messages in a conversation.
        def messageList(HTML):
            soup = BeautifulSoup(HTML, features="lxml")
            rawPosts = soup.find_all("li", class_="message")

            posts = []
            for p in rawPosts:
                info = re.findall(r"data-author=\"(.*?)\" id=\"message-(\d+)\"", HTML)[0]
                posts.append({
                    "ID": info[1],
                    "Author": info[0],
                    "Content": p.text.replace("\n\n", "\n").replace("\t", ""),
                    "RawContent": str(p),
                    "MilpacIDs": [re.findall(r"uniqueid=(\d+)", i.get("href"))[0] for i in p.find_all("a") if "uniqueid" in i.get("href")]
                })

            return rawPosts[0]

        output = []
        if pages == 0:  # Get all pages
            print(f"Parsing {totalPages} pages.")
            output += messageList(HTML)
            print("Parsed page 1")
            for p in range(2, totalPages+1):
                HTML = self.s.get(f"https://7cav.us/conversations/{ID}/page-{p}").text
                output += messageList(HTML)
                print(f"Parsed page {p}")
        elif pages > 0:  # If getting more then 1 page
            if pages > totalPages:
                print(
                    f"There aren't this many pages in the forum. Actual total: {totalPages}\nExiting.")
                return None
            else:
                print(f"Parsing {pages} pages.")
                output += messageList(HTML)
                print("Parsed page 1")
                for p in range(2, pages+1):
                    HTML = self.s.get(f"https://7cav.us/conversations/{ID}/page-{p}").text
                    output += messageList(HTML)
                    print(f"Parsed page {p}")
        elif pages < 0:
            print(f"Parsing last {abs(pages)} pages.")
            for p in range(1, totalPages+1)[::-1][:pages]:
                HTML = self.s.get(f"https://7cav.us/conversations/{ID}/page-{p}").text
                output += messageList(HTML)[::-1]
                print(f"Parsed page {p}")

    def start(self, members, title, body, allowInvite=True, lockConvo=False, stickyConvo=False, leave=False):
        # TODO: Add convo leave functionality.
        # Start a conversation.

        # Handle convo attirbutes
        allowInvite = 0 if allowInvite == False else 1 # Allow anyone in convo to invite others.
        lockConvo = 0 if lockConvo == False else 1 # Lock conversation.
        stickyConvo = 0 if stickyConvo == False else 1 # Sticky conversation.
        
        # Get, and set hidden token.
        hiddenToken = re.findall(
            r'_xfToken.*value..(.*)\"',
            self.s.get(f"https://7cav.us/conversations/add").text
        )[0]

        payload = {
            "recipients": members,
            "title": title,
            "message_html": f"<p>{body}</p>",
            "_xfToken": hiddenToken
        }

        self.s.post("https://7cav.us/conversations/insert", data=payload)

    def reply(self, ID, body):
        # Reply to a conversation.
        hiddenToken = re.findall(
            r'_xfToken.*value..(.*)\"', 
            self.s.get(f"https://7cav.us/conversations/{ID}/").text
        )[0]

        payload = {
            "message_html": f"<p>{body}</p>",
            "_xfToken": hiddenToken
        }

        self.s.post(f"https://7cav.us/conversations/{ID}/insert-reply", data=payload)

    def leave(self, ID, ignoreMessages=False):
        # Leave a conversation
        hiddenToken = re.findall(
            r'_xfToken.*value..(.*)\"', 
            self.s.get(f"https://7cav.us/conversations/{ID}/leave").text
        )[0]

        payload = {
            "delete_type": "delete_ignore" if ignoreMessages == True else "delete",
            "_xfConfirm": 1,
            "_xfToken": hiddenToken
        }

        self.s.post(f"https://7cav.us/conversations/{ID}/leave", data=payload)