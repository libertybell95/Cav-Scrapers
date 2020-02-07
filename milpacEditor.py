
#!/usr/bin/env python3

# Tools for editing milpac information.

import requests
import os
import json

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
    def __init__(self, credentialJSON=False):
        '''
        Add entries to a user's milpacs. Class authenticates into forums in instance constructor. 
        If doing bulk processing, use the same class instance for all additions.

        Inputs:
            credentialJSON (str) [OPTIONAL]: Location of credentials.json file if not in current working directory.
        '''

        pass
    
    def serviceRecord(self, milpacID, text, date, citationFile=False):
        '''
        Create a service record entry.

        Inputs:
            milpacID (int): Milpac ID of trooper.
            text (str): Service record entry.
            date (int): Date of service record. Format is YYMMDD (Example: 7 February 2020 would be 200207).
            citationFile (str) [OPTIONAL]: Path to citation file, if needed.
        '''

        pass

    def award(self, milpacID, award, date, citationFile, details=False):
        pass
        '''
        Create award entry.

        Inputs:
            milpacID (int): Milpac ID of trooper.
            award (str): Full name of award, as it appears on a trooper's milpacs.
            date (int): Date of award. FOrmat is YYMMDD (Example: 7 February 2020 would be 200207).
            citationFile (str): Path to citation file.
            details (str) [OPTIONAL]: Details text, if needed.
        '''

    def uniform(self, milpacID, uniformfile, deleteCurrent=True):
        '''
        Upload a new uniform.

        Inputs:
            milpacID (int): Milpac ID of trooper.
            uniformFile (str): Path to uniform file.
            deleteCurrent (bool) [OPTIONAL]: Delete trooper's old uniform.
        '''
        
        pass