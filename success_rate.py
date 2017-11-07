"""
Generating histogram per threshold and per profile or over the entire registered profiles.
Pass in the profile name optionally.
"""
print(__doc__)

from time import time
import sys, cx_Oracle
import matplotlib.pyplot as plt
import numpy as np

start_time = time()

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()


def plotSuccessRate(profile):
    print("Generating Success Rate Histogram for " + profile)
    cursor.execute("SELECT label, face_recog FROM comparisons, profiles WHERE comparisons.profile = profile_id AND name = '" + profile + "' ORDER BY face_recog")
    response = np.asarray(cursor.fetchall())
    truth = response[:, 0]
    prediction = response[:, 1]
    prediction = prediction.astype(np.float64)
    xAxis = np.arange(0.0, 4.0, 0.01)
    corpusSize = len(truth)
    yAxisRatio = np.empty([0, 1], dtype=np.int16)
    yAxisTPR = np.empty([0, 1], dtype=np.int16)
    yAxisTNR = np.empty([0, 1], dtype=np.int16)
    totalPositive = len(np.where(truth == 1)[0])
    totalNegative = len(np.where(truth == 0)[0])
    for x in xAxis:
        TP = len(np.where((prediction <= x) & (truth == 1))[0])
        TN = len(np.where((prediction > x) & (truth == 0))[0])
        ratio = float(TP + TN) / corpusSize * 100
        tpr = float(TP) / totalPositive * 100
        tnr = float(TN) / totalNegative * 100
        yAxisRatio = np.append(yAxisRatio, ratio)
        yAxisTPR = np.append(yAxisTPR, tpr)
        yAxisTNR = np.append(yAxisTNR, tnr)

    plt.clf()
    plt.plot(xAxis, yAxisRatio, lw = 1, color = "blue", label="TP + TN / TOTAL")
    plt.plot(xAxis, yAxisTPR, lw = 1, color = "green", label="TP / TP + FN")
    plt.plot(xAxis, yAxisTNR, lw = 1, color = "magenta", label="TN / TN + FP")
    plt.xlim([0.0, 4.0])
    plt.ylim([0.0, 100.0])
    plt.title('Threshold impact on success for ' + profile)
    plt.legend(loc="upper right")

    yMaxRatio = np.argmax(yAxisRatio)
    plt.plot(xAxis[yMaxRatio], yAxisRatio[yMaxRatio], 'ro')
    plt.axvline(x=xAxis[yMaxRatio], ls='--', c='black')
    plt.axhline(y=yAxisRatio[yMaxRatio], ls='--', c='black')
    plt.text(xAxis[yMaxRatio] + 0.05, 2, '{0:0.2f}'.format(xAxis[yMaxRatio]))
    plt.text(0.05, yAxisRatio[yMaxRatio] - 4, '{0:0.2f}%'.format(yAxisRatio[yMaxRatio]))

    idx = np.argwhere(np.diff(np.sign(yAxisTPR - yAxisTNR)) != 0).reshape(-1) + 0
    plt.plot(xAxis[idx], yAxisRatio[idx], 'ro')
    plt.axvline(x=xAxis[idx], ls='--', c='red')
    plt.text(xAxis[idx] + 0.05, 2, '{0:0.2f}'.format(xAxis[idx][0]))

    plt.show()

if len(sys.argv) > 1:
    profile = sys.argv[1]
    cursor.execute("SELECT profile_id FROM profiles WHERE name = '" + profile + "'")
    if cursor.fetchone() == None:
        print("Profile not found!")
        exit()
    else:
        plotSuccessRate(profile)
else:
    print("Generating Success Rate Histograms for all profiles + Global Histogram")


    if sys.version_info[0] < 3:
        individual = raw_input("Plot individual histograms first? (Y/N): ").lower() in ["y", "yes"]
    else:
        individual = input("Plot individual histograms first? (Y/N): ").lower() in ["y", "yes"]

    if individual:
        cursor.execute("SELECT name FROM profiles ORDER BY name")
        profiles = cursor.fetchall()
        for prof in profiles:
            plotSuccessRate(prof[0])

    cursor.execute("SELECT face_recog FROM comparisons WHERE label = 1 ORDER BY face_recog")
    match = np.asarray(cursor.fetchall())
    match = match.astype(np.float64)

    cursor.execute("SELECT face_recog FROM comparisons WHERE label = 0 ORDER BY face_recog")
    nontmatch = np.asarray(cursor.fetchall())
    notmatch = nontmatch.astype(np.float64)

    xAxis = np.arange(0.0, 4.0, 0.01)
    corpusSize = len(match) + len(notmatch)
    yAxisRatio = np.empty([0, 1], dtype=np.int16)
    yAxisTPR = np.empty([0, 1], dtype=np.int16)
    yAxisTNR = np.empty([0, 1], dtype=np.int16)
    totalPositive = len(match)
    totalNegative = len(notmatch)
    for x in xAxis:
        TP = len(np.where(match <= x)[0])
        TN = len(np.where(notmatch > x)[0])
        ratio = float(TP + TN) / corpusSize * 100
        tpr = float(TP) / totalPositive * 100
        tnr = float(TN) / totalNegative * 100
        yAxisRatio = np.append(yAxisRatio, ratio)
        yAxisTPR = np.append(yAxisTPR, tpr)
        yAxisTNR = np.append(yAxisTNR, tnr)

    plt.clf()
    plt.plot(xAxis, yAxisRatio, lw = 1, color = "blue", label="TP + TN / TOTAL")
    plt.plot(xAxis, yAxisTPR, lw = 1, color = "green", label="TP / TP + FN")
    plt.plot(xAxis, yAxisTNR, lw = 1, color = "magenta", label="TN / TN + FP")
    plt.xlim([0.0, 4.0])
    plt.ylim([0.0, 100.0])
    plt.title('Global threshold impact across all profiles')
    plt.legend(loc="upper right")

    yMaxRatio = np.argmax(yAxisRatio)
    plt.plot(xAxis[yMaxRatio], yAxisRatio[yMaxRatio], 'ro')
    plt.axvline(x=xAxis[yMaxRatio], ls='--', c='black')
    plt.axhline(y=yAxisRatio[yMaxRatio], ls='--', c='black')
    plt.text(xAxis[yMaxRatio] + 0.05, 2, '{0:0.2f}'.format(xAxis[yMaxRatio]))
    plt.text(0.05, yAxisRatio[yMaxRatio] - 4, '{0:0.2f}%'.format(yAxisRatio[yMaxRatio]))

    idx = np.argwhere(np.diff(np.sign(yAxisTPR - yAxisTNR)) != 0).reshape(-1) + 0
    plt.plot(xAxis[idx], yAxisRatio[idx], 'ro')
    plt.axvline(x=xAxis[idx], ls='--', c='red')
    plt.text(xAxis[idx] + 0.05, 2, '{0:0.2f}'.format(xAxis[idx][0]))
    plt.show()


print("\n\nExecution Time: " + str(time() - start_time))
