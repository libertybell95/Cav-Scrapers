#!/usr/bin/env python3

# Tools for editing milpac information.

import json
import csv
import os
import re

import requests

'''
Structure
    class add():
        def serviceRecord(text, date, citation=False)
        def award(award, date, citation, details=False)
        def uniform(file, deleteCurrent=True)
    class edit()
        def user(rank=False, position=False, secondaryPositions=False, enlistmentDate=False, promotionDate=False) # All others should not be changed via script
        def serviceRecord(text=False, date=False, citation=False)
        def award(award=False, date=False, citation=False, details=False)
'''

class add:
    def __init__(self, credentialsJSON=False):
        '''
        Add entries to a user's milpacs. Class authenticates into forums in instance constructor. 
        If doing bulk processing, use the same class instance for all additions.

        Inputs:
            credentialJSON (str) [OPTIONAL]: Location of credentials.json file if not in current working directory. TODO: Implement.
        '''
        self.s = requests.Session() # Requests session.

        with open("credentials.json") as file: # External credentials file.
            c = json.load(file)

        auth = {
            "login": c["user"],
            "register": 0,
            "password": c["pass"],
            "remember": 1
        }

        self.s.post("https://7cav.us/login/login", data=auth, allow_redirects=False)
        self.hiddenToken = False
    
    def serviceRecord(self, milpacID, roster, text, date, citationFile=False):
        '''
        Create a service record entry. TODO: Add citation file support

        Inputs:
            milpacID (int): Milpac ID of trooper.
            roster (int): Roster number trooper is in (Check URL. Combat Roster is 1)
            text (str): Service record entry.
            date (str): Date of service record. Format is yyyy-mm-dd (Example: 7 February 2020 would be 2020-02-07).
            citationFile (str) [OPTIONAL]: Path to citation file, if needed. (CITATION FILE CURRENTLY NOT SUPPORTED)

        Output (bool): Returns True if record created successfully, False if unsuccessful.
        '''
        assert (len(date) == 10) # Check for date to be formatted correctly.

        # Get, and set hidden token.
        hiddenToken = re.findall(
            r'_xfToken.*value..(.*)\"',
            self.s.get(f"https://7cav.us/rosters/combat-roster.{roster}/service-record/add?uniqueid={milpacID}").text
        )[0]

        # Handle citation file
        if citationFile == False:
            citationTuple = (None)
        else:
            citationTuple = (citationFile.split('/')[-1], open(citationFile, "rb"))

        # Multipart form data
        formData = {
            "details_html": (None, f"<p>{text}</p>"),
            "record_date":  (None, date),
            "citation":     citationTuple,
            "roster_id":    (None, int(roster)),
            "relation_id":  (None, int(milpacID)),
            "record_id":    (None, 0),
            "_xfConfirm":   (None, 1),
            "_xfToken":     (None, hiddenToken)
        }

        # Create service record entry.
        post = self.s.post("https://7cav.us/rosters/service-record/save", files=formData, allow_redirects=False)
        
        # Handle function return.
        if post.status_code == 303:
            print(f"Entry successfully created for MilpacID: {milpacID} | Code: {post.status_code}")
            return True
        else:
            print(f"Entry not submitted. HTTP Error {post.status_code}")
            return False

    def award(self, milpacID, roster, award, date, citationFile=False, details=False):
        '''
        Create award entry.

        Inputs:
            milpacID (int): Milpac ID of trooper.
            roster (int): Roster number trooper is in (Check URL. Combat Roster is 1)
            award (str): Full name of award, as it appears on a trooper's milpacs.
            date (str): Date of service record. Format is yyyy-mm-dd (Example: 7 February 2020 would be 2020-02-07).
            citationFile (str): Path to citation file.
            details (str) [OPTIONAL]: Details text, if needed.
        '''
        assert (len(date) == 10) # Check for date to be formatted correctly.

        awardForm = self.s.get(f"https://7cav.us/rosters/combat-roster.{roster}/awards/add?uniqueid={milpacID}").text
        
        awardChecker = False
        for a in re.findall(r'option value="(\d+).*?>(.*?)<', awardForm): # For each possible award choice.
            if award == a[1]: # If the award is an award choice.
                awardChecker = True # Set award checker to true.
                awardID = int(a[0])
                print(f"The award is: {a[1]}. The ID is: {a[0]}")
                break # Break for loop.
        if awardChecker == False:
            assert False,"Award not found."

        # Multipart form data
        formData = {
            "award_id":     (None, awardID),
            "details_html": (None, f"<p>{details}</p>" if details != False else None),
            "award_date":   (None, date),
            "citation":     (None) if citationFile == False else (citationFile.split('/')[-1], open(citationFile, "rb")),
            "roster_id":    (None, int(roster)),
            "relation_id":  (None, int(milpacID)),
            "record_id":    (None, 0),
            "_xfConfirm":   (None, 1),
            "_xfToken":     (None, re.findall(r'_xfToken.*value..(.*)\"',awardForm)[0])
        }

        # Create service record entry.
        post = self.s.post("https://7cav.us/rosters/awards/save", files=formData, allow_redirects=False)

        # Handle function return.
        if post.status_code == 303:
            print(f"Award successfully created for MilpacID: {milpacID} | Code: {post.status_code}")
            return True
        else:
            print(f"Award not submitted. HTTP Error {post.status_code}")
            return False

    def uniform(self, milpacID, roster, uniformfile, deleteCurrent=True):
        '''
        Upload a new uniform.

        Inputs:
            milpacID (int): Milpac ID of trooper.
            uniformFile (str): Path to uniform file.
            deleteCurrent (bool) [OPTIONAL]: Delete trooper's old uniform.
        '''

        formData = {
            "uniform": (uniformfile.split('/')[-1], open(uniformfile, "rb")),
            "delete": (None, 1 if deleteCurrent == True else 0),
            "_xfConfirm": (None, 1),
            "_xfToken": (None, re.findall(r'_xfToken.*value..(.*)\"',self.s.get(f"https://7cav.us/rosters/uniform?uniqueid={milpacID}").text)[0])
        }

        # Create service record entry.
        post = self.s.post(f"https://7cav.us/rosters/uniform?uniqueid={milpacID}", files=formData, allow_redirects=False)

        # Handle function return.
        if post.status_code == 303:
            print(f"Uniform successfully created for MilpacID: {milpacID} | Code: {post.status_code}")
            return True
        else:
            print(f"Uniform not submitted. HTTP Error {post.status_code}")
            return False

    def dumpAwardIDs(self):
        '''
        Gets milpacs Award IDs and outputs them to a JSON file.
        '''
        HTML = self.s.get("https://7cav.us/rosters/combat-roster.1/awards/add?uniqueid=446").text
        regex = re.findall(r'option value="(\d+).*?>(.*?)<', HTML)

        with open("awards.json", "w") as file:
            json.dump(regex, file, indent=4)

    def __del__(self):
        self.s.close()


if __name__ == "__main__":
    print("This functionality only supports adding bulk service records. If this is not your intention press CTRL+C now.")
    path = input("Enter absolute path to .csv file: ")

    with open(path) as file:
        items = list(csv.reader(file))

    for i in items:
        # print(i)
        assert (len(i) == 4) # Check for proper input length.
        instance = add()
        instance.serviceRecord(int(i[0]), int(i[1]), str(i[2]), str(i[3]))