#!/usr/bin/env python3

import csv
import datetime
import json
import os
import re

import milpacScraper


class EIBCIB:
    def checkTrooper(self, ID, checkEligible=False):
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

    def checkRoster(self, rosterID):
        milpacsIDs = [i[0] for i in milpacScraper.roster(rosterID).getInfo()]

        results = []
        for m in milpacsIDs: # Go through each milpac ID.
            check = self.checkTrooper(m) # Perform check.
            if check != False: # If check turns up anything.
                print(f"Error found for milpacID: {m} | {check}")
                results.append({ # Add it to the results list.
                    "milpacID": m,
                    "eligible": check
                    })

        with open("EIBCIB.txt", "w", newline="") as file:
            [file.write(f"MilpacID: {i}\n") for i in results]

        print(f"{len(results)} Milpacs found in error.")
        print(f"Output saved to {os.getcwd()}/EIBCIB.txt")
        
        return results

class GCM:
    '''
    Checks to see if trooper is missing any GCMs (i.e. Has 1st, 3rd, and 4th. Therefore, missing 2nd)
    '''

    def compileELOA(self, milpacID):
        '''
        Get a list of all days that trooper was on ELOA.
        '''
        records = milpacScraper.trooper(milpacID).serviceRecord()[::-1] # Service record, in chronological order
        
        startTerms = [
            "eloa",
            "discharge",
            "discharged",
            "retire",
            "retired"
        ]

        endTerms = [
            "re-en-stated",
            "reenlisted",
            "returned",
            "retirement",
            "boot",
            "reinstated"
        ]

        eloaHistory = []
        termType = "findStart"

        getDate = lambda x: datetime.datetime.strptime(x, "%b %d, %Y").date()
        for r in records:
            rec = r[1].lower() # Get service record entry, convert to all lowercase.
            if termType == "findStart": # Search for any of the startTerms in the record.
                if any(x in rec for x in startTerms):
                    start = r
                    termType = "findEnd"
            elif termType == "findEnd": # Search for any of the endTerms in the record.
                if any(x in rec for x in endTerms): # If an end term is found
                    eloaHistory.append({
                        "startDate": start[0],
                        "startEntry": start[1],
                        "endDate": r[0],
                        "endEntry": r[1],
                        "dateLen": "" #(getDate(r[0]) - getDate(start[0])).days()
                    })
                    termType = "findStart"

        with open("GCAudit.json", "w") as file:
            json.dump(eloaHistory, file, indent=4)
                

    def checkTrooper(self, milpacID):
        pass

    def checkRoster(self, rosterID=1):
        pass

class rankHistory():
    '''
    Give a history of the trooper's rank, from boot camp to current day.
    '''

    def checkTrooper(self, milpacID):
        '''
        Inputs:
            milpacID (int): Milpac ID of trooper to check.

        Output: List with each index being a dict containing the following:
            date (str): Date of rank change service record entry. Format: YYMMDD.
            entry (str): Service record entry of rank change.
            paygrade (str): Paygrade resulting from rank change.
            changeType (str): What type of rank change. Possible values:
                Boot Camp
                Current Rank
                Promotion
                Reduction
        '''

        # Get paygrades.
        with open("ranks.json") as file:
            paygrades = [i["paygrade"] for i in json.load(file)]

        # Get trooper's service record.
        serviceRecord = milpacScraper.trooper(milpacID).serviceRecord()[::-1]

        with open("SRReverse.json", "w") as file:
            json.dump(serviceRecord, file, indent=4)

        promos = []

        previousPay = "E-0"
        for r in serviceRecord:
            entry = r[1]
            date = r[0]

            srRank = re.findall(r"((E|W|O)-\d+)", entry)
            if len(srRank) == 0: # If paygrade not found
                continue

            previousIndex = paygrades.index(previousPay)
            currentIndex = paygrades.index(srRank[0][0])

            if srRank == "": # If a SPC or CPL, 
                pass
            elif previousPay == "E-0": # Boot Camp
                changeType = "Boot Camp"
            elif previousIndex < currentIndex: # Promotion
                changeType = "Promotion"
            elif previousIndex > currentIndex: # Reduction
                changeType = "Reduction"
            else: # All others
                if entry.lower().find("specialist") != -1: # If the record is a specialist.
                    changeType = "Reduction"
                elif entry.lower().find("corporal") != -1: # If the record is a corporal. 
                    changeType = "Promotion"
                else:
                    print(f"Huh, something's weird\n{r}")
                # return 0

            promos.append({
                "date": date,
                "entry": entry,
                "paygrade": srRank[0][0],
                "changeType": changeType
            })

            previousPay = srRank[0][0]
            # previousRecord = entry

        return promos

class NCOA():
    def checkGraduating(self, milpacID):
        # Check for Milpac entry of "Graduated NCOA Warrior Leadership Course" then check if it's the old system, phase 1, or phase 2.
        serviceRecord = milpacScraper.trooper(milpacID).serviceRecord()

        p2, p1, old = False, False, False
        for s in serviceRecord:
            date = s[0]
            entry = s[1].lower()
            if any(e in entry for e in ["ncoa warrior leadership course", "ncoa-wlc"]): # Check for any NCOA graduation.
                if "phase ii" in entry: # Check for phase 2.
                    p2 = {
                        "date": date,
                        "entry": s[1]
                    }
                elif "phase i" in entry: # Check for phase 1.
                    p1 = {
                        "date": date,
                        "entry": s[1]
                    }
                else: # If phase 1 and 2 not found. Assume old system.
                    old = {
                        "date": date,
                        "entry": s[1]
                    }

        print(f"Checked Milpac ID: {milpacID}")

        return {
            "Old": old,
            "Phase I": p1,
            "Phase II": p2
        }

    def checkRoster(self, rosterID):
        # Check an entire roster for NCOA completion.
        milpacIDs = [i[0] for i in milpacScraper.roster(rosterID).getInfo()]    

        output = {}
        for m in milpacIDs:
            output[m] = self.checkGraduating(m)

        return output

    def pushCSV(self, rosterID):
        j = self.checkRoster(rosterID)

        troopers = [[i[0], i[1], i[2]] for i in milpacScraper.roster(rosterID).getInfo(shaveRank=True)]

        for t in troopers:
            NCOA = j[t[0]]

            t.append(False if NCOA["Old"] == False else True)
            t.append(False if NCOA["Phase I"] == False else True)
            t.append(False if NCOA["Phase II"] == False else True)

        with open("NCOACheck.csv", "w") as file:
            wr = csv.writer(file, quoting=csv.QUOTE_ALL)
            wr.writerows(troopers)

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
    NCOA().pushCSV(1)
