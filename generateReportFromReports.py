import numpy as np

def Scores(row):
    err1 = float(row[1]) / float(row[0] + row[1])
    err2 = float(row[3]) / float(row[2] + row[3])
    accuracy = float(row[0] + row[2]) / float(row[0] + row[1] + row[2] + row[3])
    BIA = 1 - (err1 + err2) / 2.
    precision = float(row[0]) / float(row[0] + row[3])
    recall = float(row[0]) / float(row[0] + row[1])
    Fscore = 2 * precision * recall / (precision + recall)
    print str(row) + " = " + str(sum(row)) + "\nError rates: " + str(round(err1 * 100, 2)) + "% | " + str(round(err2 * 100, 2)) + "%\nF-score: " + str(round(Fscore, 5)) + "\nAccuracy: " + str(round(accuracy * 100, 2)) + "\nBIA: " + str(round(BIA * 100, 2)) + "\n\n--------------------------------------------------------------------------------\n"

profileRows = np.genfromtxt('results.csv', delimiter=",", dtype=np.int)
np.apply_along_axis(func1d=Scores, axis=1, arr=profileRows)
print "Global summary:"
row = []
for i in range(4):
    row.append(np.sum(profileRows[:, i]))
Scores(row)