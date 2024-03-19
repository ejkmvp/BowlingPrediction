import json

allScores = []
totalGames = 0
for counter in range(2000, 6600, 100):
    f = open("scoreCard" + str(counter) + ".json", "r")
    tempScoreCard = json.load(f)
    for game in tempScoreCard:
        totalGames += 1
        allScores.append(game)
    f.close()
    print("finished file " + "scoreCard" + str(counter) + ".json")

f = open("scoreCardAll.json", "w")
json.dump(allScores, f, indent=4)
f.close()
