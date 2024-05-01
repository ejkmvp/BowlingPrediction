from main import getGamesData
import os
import json
import time
MAX_GAME_IDS = 10000
REQUEST_INTERVAL_MINUTES = 5
# each request should hold 12500 game IDs
# we should try to maximize this always
# we should only have to execute 686 calls
# space out calls every ten mins
# make sure to prompt on start if you really want to continue
# theres about 8575000 games to grab
# at 10000 every 10 mins:
    #142 HOURS!!!!!
# at 12500 every 10 mins:
    #114 Hours

# General Steps
    # 1. Load in 12,500 game IDs
    # 2. Wait for time and then make request
    # 3. Store game Ids

# Load 12,500 game Ids
# get top game ID file
gameIds = []
centerScoreIndexMap = {} # maps center IDs to indexes in gameIds

# prompt user and make sure they want to continue
input("WARNING: A request is immediately sent on launch before the interval timer takes effect +"
      "\nCurrently, the program is set to request " + str(MAX_GAME_IDS) + " game ids every " + str(REQUEST_INTERVAL_MINUTES) + " minutes." +
      "\nPress any key to continue")
nextIteration = time.time()
while True:
    #wait for next iteration
    while nextIteration > time.time():
        time.sleep(30)

    # reset variables and set next iteration time
    gameIds = []
    centerScoreIndexMap = {}
    nextIteration = time.time() + (60 * REQUEST_INTERVAL_MINUTES)


    # populate gameIds
    print("Beginning grabbing GameIDS")
    while len(gameIds) < MAX_GAME_IDS:
        # open game id file and put into tempGameIds list
        if len(os.listdir("centerScores/")) == 0:
            print("out of files, exiting")
            break
        fileName = os.listdir("centerScores/")[0]
        print("Attempting to grab Ids from " + fileName)
        f = open("centerScores/" + fileName)
        tempGameIds = f.readlines()
        f.close()
        beforeLength = len(gameIds)
        for x in range(len(tempGameIds)):
            tempGameIds[x] = tempGameIds[x][:-1] # get rid of \n

        # set centerScoreIndexMap to indicate where this file starts in gameIds if there are entries
        if len(tempGameIds) > 0:
            centerScoreIndexMap[fileName[:-4]] = len(gameIds)

        #continuously add games until the gameIds list is full or the file list has no more Ids
        while len(gameIds) < MAX_GAME_IDS and len(tempGameIds) != 0:
            gameIds.append(tempGameIds.pop(0))

        # if the file is now empty, delete it
        if len(tempGameIds) == 0:
            print(fileName + " is empty, deleting")
            os.remove("centerScores/" + fileName)
        else:
        # if the file has scores let, restore it, removing the score Ids that have already been accounted for
            print(fileName + " still has entries, saving")
            f = open("centerScores/" + fileName, "w")
            for line in tempGameIds:
                f.write(str(line) + "\n")
            f.close()
        print("grabbed " + str(len(gameIds) - beforeLength) + " games from " + fileName)
    print("finished grabbing gameIds")
    print(len(gameIds))
    print(centerScoreIndexMap)


    # now that gameIds is populated, send the request
    retryCount = 4
    while not retryCount <= 0:
        try:
            responseData = getGamesData(gameIds)
            jsonData = json.loads(responseData)
            if len(jsonData['games']) != len(gameIds):
                print("Difference between number of games request and number of games received")
                print("Difference: expected - actual = " + str(len(gameIds) - len(jsonData['games'])))
            retryCount = 0
        except Exception as e:
            print("request failed")
            print(e)
            retryCount -= 1
            if retryCount != 0:
                print("trying again")
                time.sleep(10)
            else:
                print("outputting current gameIds and centerScoreIndexMap to tempfail.txt and tempfailmap.txt")
                f = open("tempfail.txt", "w")
                for line in gameIds:
                    f.write(str(line) + "\n")
                f.close()
                f = open('tempfailmap.txt', "w")
                for key in centerScoreIndexMap.keys():
                    f.write(str(key) + " - " + str(centerScoreIndexMap[key]))
                f.close()
                exit()

    gameData = jsonData['games']

    # finally, store game data to file
    outputDatas = {}
    for centerId in centerScoreIndexMap.keys():
        print("begin dumping data for bowling center id: " + centerId)
        # check if a file already exists
        if os.path.exists("centerScoreDetails/" + centerId + ".json"):
            print("center score details file already exists, opening for appends")
            f = open("centerScoreDetails/" + centerId + ".json", "r", encoding="utf-8")
            outputData = json.load(f)
            f.close()
        else:
            print("creating new center score details file")
            outputData = []
        outputDatas[centerId] = outputData
    for x in range(0, len(gameData)):
        # verify that all the attributes exist in gameData[x]
        currentGameKeys = gameData[x].keys()
        if not set(["bowlingCenterUuid", "lane", "playerName", "id", "scoreType", "game", "playerId", "adjustedFrames", "scores", "throws", "pins", "startTime", "endTime", "speed"]).issubset(set(currentGameKeys)):
            print("some attributes are missing for game")
            if "id" in currentGameKeys:
                print("id = " + str(gameData[x]["id"]))
            continue

        if gameData[x]["bowlingCenterUuid"] not in outputDatas.keys():
            print("Somehow got a game that has a bowling center uuid not sent to the server")
            print("game uuid: " + gameData[x]["bowlingCenterUuid"])
            print("our uuids: ", + str(centerScoreIndexMap.keys()))
            continue
        outputDatas[gameData[x]["bowlingCenterUuid"]].append({
            "id": gameData[x]["id"],
            "playerName": gameData[x]["playerName"],
            "scoreType": gameData[x]["scoreType"],
            "laneNumber": gameData[x]["lane"],
            "gameNumber": gameData[x]["game"],
            "playerId": gameData[x]["playerId"],
            "adjustedFrames": gameData[x]["adjustedFrames"],
            "scores": gameData[x]["scores"],
            "throws": gameData[x]["throws"],
            "pins": gameData[x]["pins"],
            "startTime": gameData[x]["startTime"],
            "endTime": gameData[x]["endTime"],
            "speed": gameData[x]["speed"]
        })
    for centerId in outputDatas.keys():
        f = open("centerScoreDetails/" + centerId + ".json", "w", encoding="utf-8")
        f.truncate(0)
        json.dump(outputDatas[centerId], f)
        f.close()
    print("finished writing to files, waiting for next iteration")



