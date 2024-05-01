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
        if adjustedFrameCount > 2:
            print(f"Adjusted frame count is grater than 2 ({adjustedFrameCount}), skipping")
            continue
        if len(scoreList) != 10:
            print("incomplete game detected, skipping")
            continue
        finalScore = scoreList[9]
        if len(pinList) != 20 and len(pinList) != 21:
            print("invalid number of shots detected, skipping")
            continue

        frame = []
        for x in range(20):
            if not pinList[x]:
                pinList[x] = 0
            binaryData = format(pinList[x], '010b')
            for y in range(10):
                frame.append(int(binaryData[y]))
        frame.append(finalScore)
        writer.writerow(frame)

g.close()