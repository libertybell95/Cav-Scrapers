# Scraper for milpacs data

import re
import requests

class roster:
    '''
    Functions meant to scrape data from a milpacs roster only

    Input:
        ID (int): Roster ID to be scraped.
    '''

    def __init__(self, ID):
        self.ID = ID
        self.html = requests.get(f"https://7cav.us/rosters?id={ID}").text
    
    def getIDs(self):
        '''
        Get all milpac IDs in a roster.

        Output (list): All milpac IDs found in the roster.
        '''

        return re.findall(r"profile\?uniqueid=(\d*)", self.html)
            
    def getInfo(self):
        '''
        Get various info from milpacs roster.

        Output (list): List of information on each trooper. Each index contains the following, in order:
            0 (int): Milpac ID
            1 (str): Rank picture URL
            2 (str): Rank w/ Full Name
            3 (str): Enlisted Date
            4 (str): Promotion Date
            5 (str): Position
        '''
        match = re.findall(r"rosterListItem\"(.|\n\t)*src..(.*)\"(.|\n\t)*uniqueid=(\d*)..\n\t*(.*)\n(.|\t\n)*(.|\n\t)*rosterEnlisted..(.*)<(.|\n\t)*rosterPromo..(.*)<.*(.|\n\t)*rosterCustom...(.*)<", self.html)

        output = []
        for m in match:
            output.append([
                m[3], # Milpac ID
                m[1], # Rank picture URL
                m[4], # Rank w/ Full Name
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

class trooper:
    '''
        Set of functions for parsing trooper data.

        Input:
            ID (int): Milpac ID of trooper.
    '''
    def __init__(self, ID):
        
        self.html = requests.get(f"https://7cav.us/rosters/profile?uniqueid={ID}").text

    def information(self):
        '''
        Get data listed in 'Information' block of the milpac roster.

        Output (dict): Trooper information with the following keys:
            name (str): Full name (Ex: John Doe)
            primary (str): Primary position (Ex: Reservist IC)
            secondary (list|bool): Secondary position, value is 'False' bool if none found.
            enlisted (str): Date of enlsitment (Ex: Jan 20, 2018)
            promoted (str): Date of last promotion (Ex: Nov 11, 2019)
            rank (str): Full spelling of rank (Ex: First Lieutenant)
            forumID (int): Forum account ID

        '''
        sec = re.findall(r'"username">(.*)<', self.html)
        if bool(sec):
            secondaries = list(sec)
        else:
            secondaries = False

        return {
            "name": re.findall(r'Full Name.*\n\t*.*?>(.*)<', self.html)[0],
            "primary": re.findall(r'Primary Position.*\n\t*.*?>(.*)<', self.html)[0],
            "secondary": secondaries,
            "enlisted": re.findall(r'Enlisted.*\n\t*.*?>(.*)<', self.html)[0],
            "promoted": re.findall(r'Promotion.*\n\t*.*?>(.*)<', self.html)[0],
            "rank": re.findall(r'Rank.*\n\t*.*?>(.*)<', self.html)[0],
            "forumID": int(re.findall(r'Forum Account.{6}\n\t{1,}.*\.(\d{1,})', self.html)[0])
        }

    def serviceRecord(self):
        '''
        Get all service record entries.

        Output (list): List containing service record entries. Each index is a list with the following:
            0 (str): Entry Date (Ex: Nov 11, 2019)
            1 (str): Record Entry
        '''
        return re.findall(r'recordDate..(.*)<.*\n\t*.*recordDetails..(.*)<', self.html)

    def awards(self):
        '''
        Get all awards.

        Output (list): List contatining record entries. Each index is a list with the following:
            0 (str): Entry Date (Ex: Feb 23, 2015)
            1 (str): Award Name (Ex: "Purple Heart")
            2 (str): Award Details
        '''
        return re.findall(r'awardDate..(.*)<.*\n.*awardTitle..(.*)<.*\n.*\n.*awardDetails..(.*)<', self.html)