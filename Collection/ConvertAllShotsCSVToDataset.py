import csv
import random

g = open("ScoreDetailDataset.txt", "wb")
h = open("ScoreDetailDatasetVSplit.txt", "wb")

f = open("ScoreDetailAllShots.csv", "r")

# figure out total number of data lines
lineCount = 0
reader = csv.reader(f)
next(f)
for line in reader:
    if len(line) != 0:
        lineCount += 1
        if not lineCount % 200000:
            print(lineCount)
# generate selection array. NOTE - this was originally for making a seperate verification set but I decided not to use it
selectionArray = [0] * lineCount
"""
for x in range(int(lineCount * .2)):
    while True:
        selec = random.randint(0, lineCount - 1)
        if selectionArray[selec] == 0:
            # found a zero value, make it one
            selectionArray[selec] = 1
            break
print("finished generating selection array")
assert(sum(selectionArray) == int(.2 * lineCount))
"""

f.close()
f = open("ScoreDetailAllShots.csv", "r")

reader = csv.reader(f)
next(f)
lineCounter = 0
for line in reader:
    if len(line) == 0:
        continue
    if len(line) != 201:
        print("incorrect length!", str(len(line)))
    lineCounter += 1
    if not lineCounter % 10000:
        print(f"finished writing {lineCounter} lines")
    #convert each of the bits into ASCII chars and write them to the file
    temp = b''
    for x in range(25):
        temp += int("".join(line[8*x:8*x+8]), 2).to_bytes(1, "little")
    # now we need two bytes to represent the final score
    temp += int(line[200]).to_bytes(2, "little")
    if selectionArray[lineCounter - 1]:
        h.write(temp)
    else:
        g.write(temp)

f.close()
g.close()
