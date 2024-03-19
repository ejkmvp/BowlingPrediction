import json
import csv

#import keras
#from keras import tensorflow
#keras.Model(

f = open("scoreCardAll.json", "r")
jsonData = json.load(f)
f.close()

print("loaded JSON data")

fields = []
for x in range(20):
    for y in range(10):
        fields.append("throw" + str(x) + "-" + str(y))
fields.append("finalScore")
#this needs to be manually written
#for now, we will only look at the first 6 frames (12 shots)
f = open("scoreCardAll.csv", "w")
writer = csv.writer(f)

writer.writerow(fields)
gameCounter = 0
wrongCounter = 0
for game in jsonData:
    temp = []   
    if (len(game["pins"]) != 21 and len(game["pins"]) != 20) or ("total" not in game.keys()):
        print(len(game["pins"]))
        print("found wrong game")
        wrongCounter += 1
        continue
    for x in range(20):

        if not game["pins"][x]:
            game["pins"][x] = 0
        binaryData = format(game["pins"][x], '010b')
        for y in range(10):
            temp.append(int(binaryData[y]))
    temp.append(game["total"])
    writer.writerow(temp)
    gameCounter += 1
f.close()

print("Total of", str(gameCounter), "games saved")
print("Total of", str(wrongCounter), "games discarded")
