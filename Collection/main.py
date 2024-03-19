import requests
import brotli
import json
import time

useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
apiKey = "tSUvYHwwNrAHQnYKmn3SBOZWdzTTvsw3VhQZ"
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

#example gameID: 581268919
#example bowlingcenterid: 7e5d0391-eb8b-11ea-8c64-06dfc92871d6

def getBowlingCenters():
    theQuest = requests.get("https://api.lanetalk.com/v1/bowlingcenters/", headers=getHeaders)
    if(theQuest.status_code == 200):
        return theQuest.content

def getBowlingCenterInfo(bowlingCenterID):
    theQuest = requests.get("https://api.lanetalk.com/v1/bowlingcenters/" + bowlingCenterID, headers=getHeaders)
    if(theQuest.status_code == 200):
        return theQuest.content

def getBowlingCenterLeaderboard(bowlingCenterID):
    theQuest = requests.get("https://api.lanetalk.com/v1/bowlingcenters/" + bowlingCenterID + "/leaderboards", headers=getHeaders)
    if(theQuest.status_code == 200):
        return theQuest.content

def getBowlingCenterCompletedGames(bowlingCenterID, pageNum):
    #pageNum starts at 1
    theQuest = requests.get("https://api.lanetalk.com/v1/bowlingcenters/" + bowlingCenterID + "/completed/" + pageNum, headers=getHeaders)
    if(theQuest.status_code == 200):
        return theQuest.content

def getGameData(gameId):
    payload = {"games": [gameId]}
    theQuest = requests.post("https://api.lanetalk.com/v1/scorecards/details", json=payload, headers=postHeaders)
    if(theQuest.status_code == 200):
        return theQuest.content

def getGamesData(gameIds):
    payload = {"games": gameIds}
    theQuest = requests.post("https://api.lanetalk.com/v1/scorecards/details", json=payload, headers=postHeaders)
    if(theQuest.status_code == 200):
        return theQuest.content

def getUserInfo(userId):
    theQuest = requests.get("https://api.lanetalk.com/v1/users/" + userId, headers=getHeaders)
    if (theQuest.status_code == 200):
        return theQuest.content
    else:
        raise Exception(theQuest.status_code)


#match IDs are sequential !!! maybe we can grab every single matches games to make sure we get a subset of average league bowlers
#the number of users served per match seemes to be unlimited
def getMatchLeaderboard(matchId: str):
    theQuest = requests.get("https://api.lanetalk.com/v1/matches/" + str(matchId) + "/leaderboard", headers=getHeaders)
    if (theQuest.status_code == 200):
        return theQuest.content

def getMatchInfo(matchId: str):
    theQuest = requests.get("https://api.lanetalk.com/v1/matches/" + str(matchId), headers=getHeaders)
    if (theQuest.status_code == 200):
        return theQuest.content
    else:
        raise Exception(theQuest.status_code)
#https://api.lanetalk.com/v1/archives/users/11784/folders/472161/recursive
#this URL has a massive amount of data. each game in this dataset has directoryId = 472161, referred to as folderID in the source code
#it seems directoryIds are sequential
#each folderID is pulled for each qualification round
#idk what the users number is


#matchIDs cap around 6220

"""
gameplan:
    For now, the goal will be to just pull the shot made per-frame, excluding what pins are left
    we are going to try to use a forecasting model where each timeframe is a frame of the game, with the end goal being forecasting a score in the 10th frame
    
    #each game will be a set of 10 char sequences indicating frame output and then a final score
"""
#print(getMatchInfo(str(6005)))

def getAndStoreMatchInfo(matchId: str, matchList):
    time.sleep(.5)
    data = json.loads(getMatchInfo(matchId))

    #map fields over to json format
    matchInfo = {}
    matchInfo["id"] = data["id"]
    matchInfo["title"] = data["title"]
    matchInfo["players"] = []
    for player in data["players"]:
        playerInfo = {}
        playerInfo["id"] = player["id"]
        playerInfo["name"] = player["firstName"] + " " + player["lastName"]
        playerInfo["games"] = []
        for game in player["games"]:
            playerInfo["games"].append(game)
        matchInfo["players"].append(playerInfo)
    matchList.append(matchInfo)

matchList = []
errorList = {}
for matchId in range(6201, 6601):
    try:
        getAndStoreMatchInfo(matchId, matchList)
        print("finished with id:", str(matchId))
    except Exception as e:
        print("runtime error when match function for ID", str(matchId))
        print(e)
        errorList[str(matchId)] = str(e)
    if matchId % 100 == 0:
        #output to file
        counter = matchId - 100
        f = open("output" + str(counter) + ".json", "w")
        json.dump(matchList, f, indent=4)
        f.close()
        f = open("errorList" + str(counter) + ".json", "w")
        json.dump(errorList, f, indent=4)
        f.close()
        #clear lists
        matchList = []
        errorList = {}



