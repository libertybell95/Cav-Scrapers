#!/usr/bin/env python3

import json
import re

import milpacScraper

def checkEIBCIB(ID, checkEligible=False):
    '''
    Audit a trooper's milpacs for EIB/CIB quality
    
    Input:
        ID (int): MilpacID

    Output:
        If there is an award that the trooper is eligible for but has not been awarded. Returns list of those awards.
        If the trooper has all the awards they are eligible for. Returns False
    '''
    trooper = milpacScraper.trooper(ID)
    opCount = len([a[1] for a in trooper.serviceRecord() if re.findall(r'Combat Mission', a[1])]) # Amount of Combat Missions attended
    awards = [a[1] for a in trooper.awards()] # List of all awards (name) that they received

    # Get operation count
    awards = {
        "EIB": {
            "awarded": True if "Expert Infantry Badge" in awards else False,
            "eligible": True if opCount >= 1 else False
        },
        "CIB": {
            "awarded": True if "Combat Infantry Badge" in awards else False,
            "eligible": True if opCount >= 5 else False
        },
        "CIB2": {
            "awarded": True if "Combat Infantry Badge 2nd Award" in awards else False,
            "eligible": True if opCount >= 10 else False
        },
        "CIB3": {
            "awarded": True if "Combat Infantry Badge 3rd Award" in awards else False,
            "eligible": True if opCount >= 15 else False
        },
        "CIB4": {
            "awarded": True if "Combat Infantry Badge 4th Award" in awards else False,
            "eligible": True if opCount >= 20 else False
        }
    }

    # Makes a list of awards the trooper is eligible for but has not yet received.
    eligibleNotAwarded = [a for a in awards if (awards[a]["eligible"] is True) and (awards[a]["awarded"] is not True)]

    return eligibleNotAwarded if len(eligibleNotAwarded) != 0 else False

def checkEIBCIBRoster(rosterID):
    milpacsIDs = [i[0] for i in milpacScraper.roster(rosterID).getInfo()]

    results = []
    for m in milpacsIDs: # Go through each milpac ID.
        check = checkEIBCIB(m) # Perform check.
        if check != False: # If check turns up anything.
            print(f"Error found for milpacID: {m} | {check}")
            results.append({ # Add it to the results list.
                "milpacID": m,
                "eligible": check
                })

    with open("EIBCIB.json", "w") as file:
        json.dump(results, file)
    
    return results

def ordinalIndicator(num):
    '''
    Get the ordinal indictor for a number

    Inputs:
        num (int): Number to process

    Output: Dictionary with the following key value pairs:
        stringNum (str): Number with ordinal indicator appended (Ex: 1st)
        indicator (str): Ordinal indicator used (Ex: for 1 the value would be "st")
    '''
    rawNum = str(num)
    strNum = rawNum if len(rawNum) == 1 else (0+rawNum)

    if strNum[-2:] in ("11", "12", "13", "14", "15", "16", "17", "18", "19"): # If in teens
        indicator = "th"
    elif strNum[-1] is "1": # Ends with 1
        indicator = "st"
    elif strNum[-1] is "2": # Ends with 2
        indicator = "nd"
    elif strNum[-1] is "3": # Ends with 3
        indicator = "rd"
    else: # Everything else
        indicator = "th"

    return {
        "stringNum": f"rawNum{indicator}",
        "indicator": indicator
    }

if __name__ == "__main__":
    checkEIBCIBRoster(1)