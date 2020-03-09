#!/usr/bin/env python3

# Scraper for milpacs data

import csv
import json
import re
import datetime

import requests


class roster:
    '''
    Functions meant to scrape data from a milpacs roster only.

    Input:
        ID (int): Roster ID to be scraped.
    '''

    def __init__(self, ID=1):
        self.ID = ID
        self.html = requests.get(f"https://7cav.us/rosters?id={ID}").text
    
    def getIDs(self):
        '''
        Get all milpac IDs in a roster.

        Output (list): All milpac IDs found in the roster.
        '''

        return re.findall(r"profile\?uniqueid=(\d*)", self.html)
            
    def getInfo(self, rosterID=False, removeSpecialCharacters=False, shaveRank=False):
        '''
        Get various info from milpacs roster.

        Inputs:
            rosterID (bool) [OPTIONAL]: Get info for a specific roster. Default: False
                If False, will use ID specified when class was initiated.
            removeSpecialCharacters (bool) [OPTIONAL]: Remove any special characters from troopers names, specifically aprostrophies.
                Default: False.
            shaveRanks (bool) [OPTIONAL]: Remove the rank from their name.
                Default: False

        Output (list): List of information on each trooper. Each index contains the following, in order:
            0 (int): Milpac ID
            1 (str): Rank picture URL
            2 (str): Rank w/ Full Name
            3 (str): Enlisted Date
            4 (str): Promotion Date
            5 (str): Position
        '''
        if rosterID != False: # If a rosterID is specified for this function, grab from that roster.
            self.html = requests.get(f"https://7cav.us/rosters?id={rosterID}").text

        match = re.findall(r"rosterListItem\"(.|\n\t)*src..(.*)\"(.|\n\t)*uniqueid=(\d*)..\n\t*(.*)\n(.|\t\n)*(.|\n\t)*rosterEnlisted..(.*)<(.|\n\t)*rosterPromo..(.*)<.*(.|\n\t)*rosterCustom...(.*)<", self.html)

        output = []
        for m in match:
            if removeSpecialCharacters == True:
                name = m[4].replace('&#039;','')
            else:
                name = m[4].replace('&#039;','\'')
        
            # Handle rank shaving. Also rank image URL.
            if shaveRank == True:
                stripper = stripRank(name, m[1])
                name = stripper["name"]
                rank = stripper["rank"]
            else:
                rank = m[1] # Rank image URL

            output.append([
                m[3], # Milpac ID
                rank, # Rank picture URL
                name, # Full Name
                m[7], # Enlisted Date
                m[9], # Promotion Date
                m[11], # Position
                self.ID # Roster ID
                ])

        return output

    def getRosters(self):
        '''
        Get list of all roster ID's, for further scraping.

        Output (list): List of all roster ID's, as found in URL.
        '''

        return re.findall(r'rosters\/\?id=(\d+)', self.html)

    def scrapeAllRosters(self, toCSV=False, removeSpecialCharacters=False):
        '''
        Compile a list of all troopers on all rosters.
        Inputs:
            toCSV (bool) [OPTIONAL]: Should roster list be saved to a .csv file

        Output (list): List of all troopers with each index being information found in roster().getInfo()
        '''
        IDs = self.getRosters()
        output = []
        for i in IDs:
            output += self.getInfo(i, removeSpecialCharacters=removeSpecialCharacters)

        if toCSV == True:
            with open("rosters.csv", "w", newline="") as file:
                wr = csv.writer(file)
                wr.writerows(output)
            print(f"Exported data for {len(output)} troopers.")
        return output


class trooper:
    '''
        Set of functions for parsing trooper data.

        Input:
            ID (int): Milpac ID of trooper.
    '''
    def __init__(self, ID):
        
        self.html = requests.get(f"https://7cav.us/rosters/profile?uniqueid={ID}").text

    def information(self, removeSpecialCharacters=False, shaveRanks=False, dateTime=False):
        '''
        Get data listed in 'Information' block of the milpac roster.

        Inputs:
            removeSpecialCharacters (bool) [OPTIONAL]: Remove any special characters from troopers names, specifically aprostrophies.
                Default: False
            shaveRank (bool): TODO: Figure out why this is here, and remove if not nessecary.
            dateTime (bool) [OPTIONAL]:
                If True, convert enlisted & promoted to datetime object.
                If False [DEFAULT], enlisted & promoted are date string (Ex, Nov 11, 2020).

        Output (dict): Trooper information with the following keys:
            name (str): Full name. (Ex: John Doe)
            primary (str): Primary position. (Ex: Reservist IC)
            secondary (list|bool): Secondary position, Value is 'False' bool if none found.
            enlisted (str|date): Date of enlsitment. See dateTime input for further help.
            promoted (str|date): Date of last promotion. See dateTime input for further help.
            rank (str): Full spelling of rank. (Ex: First Lieutenant)
            forumID (int): Forum account ID.

        '''
        # Handle secondaries, if present.
        sec = re.findall(r'"username">(.*)<', self.html)
        if bool(sec):
            secondaries = list(sec)
        else:
            secondaries = False

        # Handle special characters in name
        name = re.findall(r'Full Name.*\n\t*.*?>(.*)<', self.html)[0]
        if removeSpecialCharacters == True:
            name = name.replace('&#039;','')
        else:
            name = name.replace('&#039;','\'')

        enlisted = re.findall(r'Enlisted.*\n\t*.*?>(.*)<', self.html)[0]
        promoted = re.findall(r'Promotion.*\n\t*.*?>(.*)<', self.html)[0]

        return {
            "name": name,
            "primary": re.findall(r'Primary Position.*\n\t*.*?>(.*)<', self.html)[0],
            "secondary": secondaries,
            "enlisted": enlisted if dateTime == False else datetime.datetime.strptime(enlisted, "%b %d, %Y").date(),
            "promoted": promoted if dateTime == False else datetime.datetime.strptime(promoted, "%b %d, %Y").date(),
            "rank": re.findall(r'Rank.*\n\t*.*?>(.*)<', self.html)[0],
            "forumID": int(re.findall(r'Forum Account.{6}\n\t{1,}.*\.(\d{1,})', self.html)[0])
        }

    def serviceRecord(self, dateTime=False):
        '''
        Get all service record entries.

        Inputs:
            dateTime (bool) [OPTIONAL]:
                If True, will Entry Date on output will be a dateTime object.
                If False (DEFAULT), Entry Date on output will be string (Ex: Nov 11, 2019)

        Output (list): List containing service record entries. Each index is a tuple with the following:
            0 (str|date): Entry Date. See dateTime input for further help.
            1 (str): Record Entry
        '''
        reg = re.findall(r'recordDate..(.*)<.*\n\t*.*recordDetails..(.*)<', self.html)
        if reg[0][0] == "width=\"10%\">Date":
            del reg[0]

        if dateTime != False:
            return [(datetime.datetime.strptime(i[0], "%b %d, %Y").date(), i[1]) for i in reg]
        else:
            return reg

    def awards(self, dateTime=False):
        '''
        Get all awards.

        Inputs:
            dateTime (bool) [OPTIONAL]:
                If True, will Entry Date on output will be a dateTime object.
                If False (DEFAULT), Entry Date on output will be string (Ex: Nov 11, 2019)

        Output (list): List contatining record entries. Each index is a tuple with the following:
            0 (str|date): Entry Date. see dateTime input for further help.
            1 (str): Award Name (Ex: "Purple Heart")
            2 (str): Award Details
        '''
        reg = re.findall(r'awardDate..(.*)<.*\n.*awardTitle..(.*)<.*\n.*\n.*awardDetails..(.*)<', self.html)

        if dateTime != False:
            return [(datetime.datetime.strptime(i[0], "%b %d, %Y").date(), i[1], i[2]) for i in reg]
        else:
            return reg

def stripRank(name, rankImage):
    '''
    Strip rank from trooper's name. Requires 'ranks.json' to be present in same folder as this script.

    Inputs:
        name (str): Trooper's full name w/ rank.
        rankImage (str): Image for trooper's rank.

    Output (dict): Troopers name and rank. Dict structure:
        name (str): Trooper's full name. (Ex: John Doe)
        rank (str): Full spelling of rank (Ex: Specialist)
    '''
    with open("ranks.json") as file:
        rConfig = json.load(file)

    for c in rConfig:
        if c["milpacImage"] == rankImage:
            l = len(c["long"])
            return {"name":name[l+1:], "rank":c["long"]}
