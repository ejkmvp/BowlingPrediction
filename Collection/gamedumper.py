#notes on scorecard output

#there is one entry in "throws" per throw
#there is one entry in "pins" per throw, which represents the pins left after a throw
    #this appears to be a binary number where the LSB represents the 1 pin and the 10th bit represents the 10 pin
    #there is an extra 11th bit set to one if its the first shot
    #the value is zero if no pins are left and null if the shot is skipped (ie by striking or not marking in the 10th)
    #so there is always 21 shots

import requests
import brotli
import json
import time

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
apiKey = "YM4Xav5bzOO4mAsFJEtoZyZTHLbIJcKLq928"
getHeaders = {"Accept": "application/json, text/plain, */*",
           "Accept-Encoding": "gzip, deflate, br, zstd",
           "Apikey": apiKey,
           "Content-Type": "application/json",
           "User-Agent": useragent}

postHeaders = {"Accept": "application/json, text/plain, */*",
           "Accept-Encoding": "gzip, deflate, br, zstd",
           "Apikey": apiKey,
           "Content-Type": "text/plain;charset=UTF-8",
           "User-Agent": useragent}

def getGamesData(gameIds):
    payload = {"games": gameIds}
    theQuest = requests.post("https://api.lanetalk.com/v1/scorecards/details", json=payload, headers=postHeaders)
    if(theQuest.status_code == 200):
        return theQuest.content
    else:
        raise Exception(theQuest.status_code)

for counter in range(4300, 4400, 100):
    #read in json data
    f = open("output" + str(counter) + ".json", "r")
    matchData = json.load(f)
    f.close()
    gameData = []
    errorList = {}
    for match in matchData:
        if len(match["players"]) == 0:
            continue

        for player in match["players"]:
            try:
                if len(player["games"]) == 0:
                    continue
                scoreCard = json.loads(getGamesData(player["games"]))
                for game in scoreCard["games"]:
                    temp = {}
                    temp["id"] = game["id"]
                    temp["throws"] = game["throws"]
                    temp["pins"] = game["pins"]
                    temp["total"] = game["scores"][-1]
                    gameData.append(temp)
            except Exception as e:
                print("error with user ID:", player["id"])
                errorList[player["id"]] = str(e)
        print("finished match", match["id"])

    f = open("scoreCard" + str(counter) + ".json", "w")
    json.dump(gameData, f, indent=4)
    f.close()
    f = open("errorCard" + str(counter) + ".json", "w")
    json.dump(errorList, f, indent=4)
    f.close()
    print("finished file with counter", str(counter))

