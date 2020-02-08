#!/usr/bin/env python3

# Tools for editing milpac information.

import json
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
        Create a service record entry.

        Inputs:
            milpacID (int): Milpac ID of trooper.
            roster (int): Roster number trooper is in (Check URL. Combat Roster is 1)
            text (str): Service record entry.
            date (str): Date of service record. Format is yyyy-mm-dd (Example: 7 February 2020 would be 2020-02-07).
            citationFile (str) [OPTIONAL]: Path to citation file, if needed. (CITATION FILE CURRENTLY NOT SUPPORTED)
        
        TODO: Add citation file support
        '''
        assert (len(date) == 10) # Check for date to be formatted correctly.
        assert (type(milpacID) != 'int') # Check for proper Milpac ID.
        assert (type(roster) != 'int') # Check for proper roster ID.

        # Get, and set hidden token.
        hiddenToken = re.findall(
            r'_xfToken.*value..(.*)\"',
            self.s.get(f"https://7cav.us/rosters/combat-roster.{roster}/service-record/add?uniqueid={milpacID}").text
        )[0]

        # Multipart form data
        formData = {
            "details_html": (None, f"<p>{text}</p>"),
            "record_date":  (None, date),
            "citation":     (None),
            "roster_id":    (None, 1),
            "relation_id":  (None, 2519),
            "record_id":    (None, 0),
            "_xfConfirm":   (None, 1),
            "_xfToken":     (None, hiddenToken)
        }

        post = self.s.post("https://7cav.us/rosters/service-record/save", files=formData, allow_redirects=False)
        print(post.status_code)
        print("Service record entry created.")

    def award(self, milpacID, roster, award, date, citationFile, details=False):
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
        pass

    def uniform(self, milpacID, roster, uniformfile, deleteCurrent=True):
        '''
        Upload a new uniform.

        Inputs:
            milpacID (int): Milpac ID of trooper.
            uniformFile (str): Path to uniform file.
            deleteCurrent (bool) [OPTIONAL]: Delete trooper's old uniform.
        '''
        
        pass

    def __del__(self):
        self.s.close()


if __name__ == "__main__":
    add().serviceRecord(2519,1,"The bot is testing - 1", "2020-01-10")