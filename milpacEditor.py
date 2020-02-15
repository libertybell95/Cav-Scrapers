#!/usr/bin/env python3

# Tools for editing milpac information.

import json
import csv
import os
import re

import requests

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
            date (str): Date of service record. Format is yyyy-mm-dd (Example: "2020-02-19").
            citationFile (str) [OPTIONAL]: Path to citation file, if needed.

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
            print(f"Service Record entry created for: https://7cav.us/rosters/profile?uniqueid={milpacID} ({date})")
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
            date (str): Date of service record. Format is yyyy-mm-dd (Example: "2020-02-19").
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
            print(f"Award created for: https://7cav.us/rosters/profile?uniqueid={milpacID} ({award} | {date})")
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
            print(f"Uniform uploaded for: https://7cav.us/rosters/profile?uniqueid={milpacID}")
            return True
        else:
            print(f"Uniform not submitted. HTTP Error {post.status_code}")
            return False
   
    def __del__(self):
        self.s.close()

class bulkAdd:
    def __init__(self):
        self.s = add()
    
    def serviceRecords(self, csvFile):
        '''
        Add a large amount of service record entries from a .csv file.

        Inputs:
            csvFile (str): Path to .csv file.

        Each row on the csv file must have the folling format:
            0 (int): Trooper's Milpac ID.
            1 (int): Trooper's roster ID.
            2 (str): Service record entry text.
            3 (str): Service record entry date. Must be following Format: yyyy-mm-dd (Ex: "2020-01-19")
            4 (str) [OPTIONAL]: Path to citation file. Not the folder, the actual file.
        '''

        with open(csvFile) as file:
            records = list(csv.reader(file))

        for r in records:
            assert (len(r) in (4,5)), f"Entry is wrong length, needs to be 4 or 5. Current length: {len(r)}. Row contents:\n{r}"
            if len(r) == 4:
                self.s.serviceRecord(r[0], r[1], r[2], r[3])
            else:
                self.s.serviceRecord(r[0], r[1], r[2], r[3], r[4])

    def awards(self, csvFile):
        '''
        Add a large amount of awards from a .csv file.

        Inputs:
            csvFile (str): Path to .csv file.

        Each row on the csv file must have the folling format:
            0 (int): Trooper's Milpac ID.
            1 (int): Trooper's roster ID.
            2 (str): Award name, as it appears in Milpacs. Case sensitive.
            3 (str): Service record entry date. Must be following Format: yyyy-mm-dd (Ex: "2020-01-19").
            4 (str): Path to citation file. Not the folder, the actual file.
                If not using a citation, put an empty string.
            5 (str) [OPTIONAL]: Award details.
        '''

        with open(csvFile) as file:
            awards = list(csv.reader(file))

        for a in awards:
            assert (len(a) in (5,6)), f"Entry is wrong length, needs to be 5 or 6. Current length: {len(a)}. Row contents:\n{a}"
            citation = False if bool(a[4]) == False else a[4]
            if len(a) == 5: # If award details not given.
                self.s.award(a[0], a[1], a[2], a[3], citation)
            else: # if award details is given.
                self.s.award(a[0], a[1], a[2], a[3], citation, a[5])
    
    def uniforms(self, csvFile):
        '''
        Add a large amount of uniforms from a .csv file.

        Inputs:
            csvFile (str): Path to .csv file.

        Each row on the csv file must have the folling format:
            0 (int): Trooper's Milpac ID.
            1 (int): Trooper's roster ID.
            2 (str): Path to uniform file. The file, not the folder.
        '''

        with open(csvFile) as file:
            uniforms = list(csv.reader(file))

        for u in uniforms:
            assert (len(u) == 3), f"Entry is wrong length, needs to be 3. Current length {len(u)}. Row contents:\n{u}" # If the length of the row is too long, throw error.
            self.s.uniform(u[0], u[1], u[2])

if __name__ == "__main__":
    choice = int(input("What type of bulk addition would you like to execute:\n1 - Service Records\n2 - Awards\n3 - Uniforms\nEnter a number: "))

    if choice == 1:
        print("You chose Service Records.")
        path = input("Enter full path to .csv file: ")
        bulkAdd().serviceRecords(path)
    elif choice == 2:
        print("You chose Awards.")
        path = input("Enter full path to .csv file: ")
        bulkAdd().awards(path)
    elif choice == 3:
        print("You chose Uniforms")
        path = input("Enter full path to .csv file: ")
        bulkAdd().uniforms(path)
    else:
        print("That is not a choice")