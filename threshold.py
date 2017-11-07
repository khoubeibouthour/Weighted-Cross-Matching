"""
Generating the characteristics of a given threshold.
"""

print(__doc__)

import sys, cx_Oracle
import numpy as np
from time import time

start_time = time()

# host = 'Dell-PC'
# port = 1521
# SID = 'XE'
# dsn_tns = cx_Oracle.makedsn(host, port, SID)
#connection = cx_Oracle.connect('python', 'python', dsn_tns)

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()

if len(sys.argv) == 1:
    print("Must provide the threshold [0.0 .. 4.0]")
    print("Threshold default value set to 1.08")
    threshold = 1.08
    # exit()
else:
    try:
        threshold = float(sys.argv[1])
    except:
        print("The threshold must be a valid value between [0.0 .. 4.0]")
        exit()

    if not (0 <= threshold <= 4):
        print("The threshold must be a valid value between [0.0 .. 4.0]")
        exit()

print("Threshold: " + str(threshold))

Truths = np.empty([0, 1], dtype=np.int16)
Predictions = np.empty([0, 1], dtype=np.float64)

cursor.execute("SELECT name FROM profiles ORDER BY name")
profiles = cursor.fetchall()
for prof in profiles:
    profile = prof[0]
    print('\n\n' + profile + ': ')
    relative_time = time()
    cursor.execute("SELECT label, face_recog FROM comparisons, profiles WHERE comparisons.profile = profile_id AND name = '" + profile + "' ORDER BY face_recog")
    print("Extraction from database took " + str(time() - relative_time) + ' seconds')
    relative_time = time()
    response = np.asarray(cursor.fetchall())
    print("Fetching data took " + str(time() - relative_time) + ' seconds')

    truth = response[:, 0]
    truth = truth.astype(int)

    Truths = np.append(Truths, truth)

    prediction = response[:, 1]
    prediction = prediction.astype(np.float64)

    Predictions = np.append(Predictions, prediction)

    corpusSize = len(truth)
    totalPositive = len(np.where(truth == 1)[0])
    totalNegative = corpusSize - totalPositive
    TP = len(np.where((prediction <= threshold) & (truth == 1))[0])
    TN = len(np.where((prediction > threshold) & (truth == 0))[0])
    print("Numpy calculation took " + str(time() - relative_time) + ' seconds')
    ratio = float(TP + TN) / corpusSize * 100
    tpr = float(TP) / totalPositive * 100
    tnr = float(TN) / totalNegative * 100

    print('\tTotal faces   : ' + str(totalPositive) + ' / ' + str(corpusSize))
    print( '\tTrue Positives: ' + str(TP) + ' / ' + str(totalPositive) + ' = {0:0.2f}%'.format(tpr))
    print('\tTrue Negatives: ' + str(TN) + ' / ' + str(totalNegative) + ' = {0:0.2f}%'.format(tnr))
    print('\tSuccess Ration: ' + str(TP) + ' + ' + str(TN) + ' / ' + str(corpusSize) + ' = {0:0.2f}%'.format(ratio))


print('\n===============================================================================\nGlobally: ')
corpusSize = len(Truths)
totalPositive = len(np.where(Truths == 1)[0])
totalNegative = corpusSize - totalPositive
TP = len(np.where((Predictions <= threshold) & (Truths == 1))[0])
TN = len(np.where((Predictions > threshold) & (Truths == 0))[0])
ratio = float(TP + TN) / corpusSize * 100
tpr = float(TP) / totalPositive * 100
tnr = float(TN) / totalNegative * 100

print('\tTotal faces   : ' + str(totalPositive) + ' / ' + str(corpusSize))
print('\tTrue Positives: ' + str(TP) + ' / ' + str(totalPositive) + ' = {0:0.2f}%'.format(tpr))
print('\tTrue Negatives: ' + str(TN) + ' / ' + str(totalNegative) + ' = {0:0.2f}%'.format(tnr))
print('\tSuccess Ratio: ' + str(TP) + ' + ' + str(TN) + ' / ' + str(corpusSize) + ' = {0:0.2f}%'.format(ratio))

print("\n\nExecution Time: " + str(time() - start_time))