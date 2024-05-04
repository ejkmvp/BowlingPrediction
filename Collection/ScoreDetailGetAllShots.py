import os
import json
import csv

tupleList = []

fields = []
for x in range(20):
    for y in range(10):
        fields.append("throw" + str(x) + "-" + str(y))
fields.append("finalScore")

g = open("ScoreDetailAllShots.csv", "w")
writer = csv.writer(g)
writer.writerow(fields)

for file in os.listdir("centerScoreDetails/"):
    try:
        print("attempting to load file " + file)
        f = open("centerScoreDetails/" + file)
        fileData = json.load(f)
        f.close()
    except Exception as e:
        print("Error loading file " + file)
        print(e)
        print("Going to next file")
        continue
    for game in fileData:
        #make sure necessary headers are present
        if not ("adjustedFrames" in game.keys() and "scores" in game.keys() and "pins" in game.keys()):
            print("found game in invalid keys, skipping")
            continue

        # check types
        try:
            adjustedFrameCount = int(game["adjustedFrames"])
            scoreList = list(game["scores"])
            pinList = list(game["pins"])
        except Exception as e:
            print("error extracting fields, skipping game")
            print(e)
            continue

        # make sure adjustedFrames is reasonable and that scoreList is complete and pinlist is complete
        if adjustedFrameCount > 0:
            print(f"Adjusted frame count is grater than 0 ({adjustedFrameCount}), skipping")
            continue
        if len(scoreList) != 10:
            print("incomplete game detected, skipping")
            continue
        finalScore = scoreList[9]
        if len(pinList) != 20 and len(pinList) != 21:
            print("invalid number of shots detected, skipping")
            continue
        if len(pinList) == 20:
            pinList.append(1023)
        frame = []
        for x in range(21):
            if not pinList[x]:
                pinList[x] = 0
            binaryData = format(pinList[x], '010b')
            for y in range(10):
                frame.append(int(binaryData[y]))
        frame.append(finalScore)

        # check that the game is valid (simulating game adds up to final score
        runningScore = 0
        nextShotMult = 1
        nextNextShotMult = 1
        line = frame
        invalidPinState = False
        for frameNum in range(9):
            firstShotPins = line[20 * frameNum: 20 * frameNum + 10]
            secondShotPins = line[20 * frameNum + 10: 20 * frameNum + 20]
            for h in range(10):
                if firstShotPins[h] == 0 and secondShotPins[h] == 1:
                    print("Invalid pin state detected")
                    invalidPinState = True
            firstShot = 10 - sum(firstShotPins)
            secondShot = 10 - sum(secondShotPins)

            if firstShot == 10:
                # strike
                runningScore += 10 * nextShotMult
                nextShotMult = nextNextShotMult + 1
                nextNextShotMult = 2
            else:
                runningScore += firstShot * nextShotMult + (secondShot - firstShot) * nextNextShotMult
                if secondShot == 10:
                    nextShotMult = 2
                else:
                    nextShotMult = 1
                nextNextShotMult = 1
        # handle tenth frame
        firstShotPins = line[180: 190]
        secondShotPins = line[190:200]
        thirdShotPins = line[200:210]
        firstShot = 10 - sum(firstShotPins)
        secondShot = 10 - sum(secondShotPins)
        thirdShot = 10 - sum(thirdShotPins)
        if firstShot == 10:
            runningScore += 10 * nextShotMult + secondShot * nextNextShotMult
            if secondShot == 10:
                runningScore += thirdShot
            else:
                for g in range(10):
                    if secondShotPins[g] == 0 and thirdShotPins[g] == 1:
                        print("Invalid 10th frame detected")
                        invalidPinState = True
                runningScore += thirdShot - secondShot
        else:
            runningScore += firstShot * nextShotMult + (secondShot - firstShot) * nextNextShotMult + thirdShot
            for g in range(10):
                if firstShotPins[g] == 0 and secondShotPins[g] == 1:
                    print("Invalid 10th frame detected")
                    invalidPinState = True

        if runningScore == line[210] and not invalidPinState:
            writer.writerow(frame)
        else:
            print(f"Invalid game. Expected score was {line[210]}, actual score was {runningScore}. InvalidPinState was {invalidPinState}")
g.close()