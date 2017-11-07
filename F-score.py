import numpy as np

def fScore(row):
    precision = float(row[0]) / float(row[0] + row[3])
    recall = float(row[0]) / float(row[0] + row[1])
    Fscore = 2 * precision * recall / (precision + recall)
    print "\nF-score: " + str(round(Fscore * 100, 2))

profileRow = np.genfromtxt('F-scores.csv', delimiter=",", dtype=np.int)
Fscores = np.apply_along_axis(func1d=fScore, axis=1, arr=profileRow)