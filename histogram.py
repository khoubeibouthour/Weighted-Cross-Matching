"""
Generating histogram per threshold and per profile or over the entire registered profiles.
Pass in the threshold first then optionally the profile name.
"""

print(__doc__)

from time import time
import sys, cx_Oracle
import matplotlib.pyplot as plt
from scipy.interpolate import spline
import numpy as np

start_time = time()

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()

def plotHistogram(profile, normalize):
    print("\n-----------------------------------------------------------\nGenerating Histogram for " + profile)

    cursor.execute("SELECT face_recog FROM comparisons, profiles WHERE name = '" + profile + "' AND profile_id = comparisons.profile AND label = 1 order by face_recog")
    response = np.asarray(cursor.fetchall())
    response = response.astype(np.float64)
    yAxisP, xAxisP, _ = plt.hist(response, color='navy', label='True positive distribution', histtype='step', bins=20, normed=normalize)

    sumP = sum(yAxisP)
    areaP = 0
    counterP = 0
    while areaP < .5:
        counterP += 1
        areaP = sum(yAxisP[0:counterP]) / sumP
    LCL = xAxisP[counterP]

    cursor.execute("SELECT face_recog FROM comparisons, profiles WHERE name = '" + profile + "' AND profile_id = comparisons.profile AND label = 0 order by face_recog")
    response = np.asarray(cursor.fetchall())
    response = response.astype(np.float64)
    yAxisN, xAxisN, _ = plt.hist(response, color='navy', label='True positive distribution', histtype='step', bins=20, normed=normalize)

    sumN = sum(yAxisN)
    areaN = 0
    counterN = 0
    while areaN < .5:
        counterN += 1
        areaN = sum(yAxisN[0:counterN]) / sumN
    UCL = xAxisN[counterN]

    plt.clf()
    plt.axvline(LCL, lw=1, ls="--", c="brown")
    plt.text(LCL + 0.05, 0, 'LCL={0:0.2f}'.format(LCL), color="brown")

    plt.axvline(UCL, lw=1, ls="--", c="brown")
    plt.text(UCL + 0.05, 0, 'UCL={0:0.2f}'.format(UCL), color="brown")
    
    xAxisP = xAxisP[:-1]
    xAxisN = xAxisN[:-1]

    maxY = max(yAxisP.max(), yAxisN.max()) + 500

    newXAxisP = np.linspace(xAxisP.min(), xAxisP.max(), 1000)
    newXAxisN = np.linspace(xAxisN.min(), xAxisN.max(), 1000)

    newYAxisP = spline(xAxisP, yAxisP, newXAxisP)
    newYAxisN = spline(xAxisN, yAxisN, newXAxisN)

    xAxis = np.linspace(0, 4, 1000)
    YAxisP = spline(xAxisP, yAxisP, xAxis)
    YAxisN = spline(xAxisN, yAxisN, xAxis)
    i = np.argwhere(np.diff(np.sign(YAxisP - YAxisN)) != 0).reshape(-1)[1]

    plt.plot(newXAxisP, newYAxisP, lw=1, color="blue", label=profile + '\'s faces distribution')
    plt.plot(newXAxisN, newYAxisN, lw=1, color="red", label='Other faces distribution')
    plt.plot(xAxis[i], YAxisP[i], 'ro')
    plt.xlabel('Face Verification Output')
    plt.ylabel('Number Of Observations')
    plt.xlim([0.0, 4.0])
    if not normalize: plt.ylim([0.0, maxY])
    plt.title('Face Verification Output Distribution for ' + profile)
    plt.legend(loc="upper right")
    print(i, xAxis[i], YAxisP[i])
    plt.text(xAxis[i] + 0.2, YAxisP[i], 'Threshold={0:0.2f}'.format(xAxis[i]))
    print("Execution time: " + str(time() - start_time) + " seconds")
    plt.show()

if len(sys.argv) > 1:
    profile = sys.argv[1]
    cursor.execute("SELECT profile_id FROM profiles WHERE name = '" + profile + "'")
    if cursor.fetchone() == None:
        print("Profile not found!")
        exit()
    if sys.version_info[0] < 3:
        normalize = raw_input("Do you want the plots to be normalized? (Y/N): ").lower() in ["y", "yes"]
    else:
        normalize = input("Do you want the plots to be normalized? (Y/N): ").lower() in ["y", "yes"]
    plotHistogram(profile, normalize)

else:
    print("Generating Histograms for all profiles + Global Histogram")
    if sys.version_info[0] < 3:
        normalize = raw_input("Do you want the plots to be normalized? (Y/N): ").lower() in ["y", "yes"]
        individual = raw_input("Plot individual histograms first? (Y/N): ").lower() in ["y", "yes"]
    else:
        normalize = input("Do you want the plots to be normalized? (Y/N): ").lower() in ["y", "yes"]
        individual = input("Plot individual histograms first? (Y/N): ").lower() in ["y", "yes"]

    if individual:
        cursor.execute("SELECT name FROM profiles ORDER BY name")
        profiles = cursor.fetchall()
        for prof in profiles:
            plotHistogram(prof[0], normalize)

    cursor.execute("SELECT face_recog FROM comparisons WHERE label = 1 ORDER BY face_recog")
    responseP = np.asarray(cursor.fetchall())
    cursor.execute("SELECT face_recog FROM comparisons WHERE label = 0 ORDER BY face_recog")
    responseN = np.asarray(cursor.fetchall())

    yAxisP, xAxisP, _ = plt.hist(responseP, color = 'navy', label='True positive distribution', histtype='step', bins=20, normed=normalize)
    yAxisN, xAxisN, _ = plt.hist(responseN, color = 'navy', label='True positive distribution', histtype='step', bins=20, normed=normalize)

    sumP = sum(yAxisP)
    areaP = 0
    counterP = 0
    while areaP < .5:
        counterP += 1
        areaP = sum(yAxisP[0:counterP]) / sumP
    LCL = xAxisP[counterP]

    sumN = sum(yAxisN)
    areaN = 0
    counterN = 0
    while areaN < .5:
        counterN += 1
        areaN = sum(yAxisN[0:counterN]) / sumN
    UCL = xAxisN[counterN]

    plt.clf()
    plt.axvline(LCL, lw=1, ls="--", c="brown")
    plt.text(LCL + 0.05, 0, 'LCL={0:0.2f}'.format(LCL), color="brown")

    plt.axvline(UCL, lw=1, ls="--", c="brown")
    plt.text(UCL + 0.05, 0, 'UCL={0:0.2f}'.format(UCL), color="brown")

    xAxisP = xAxisP[:-1]
    xAxisN = xAxisN[:-1]

    maxY = max(yAxisP.max(), yAxisN.max()) + 500

    newXAxisP = np.linspace(xAxisP.min(), xAxisP.max(), 1000)
    newXAxisN = np.linspace(xAxisN.min(), xAxisN.max(), 1000)

    newYAxisP = spline(xAxisP, yAxisP, newXAxisP)
    newYAxisN = spline(xAxisN, yAxisN, newXAxisN)


    plt.plot(newXAxisP, newYAxisP, lw = 1, color = "blue", label='Subjects\' faces distribution')
    plt.plot(newXAxisN, newYAxisN, lw = 1, color = "red", label='Other faces distribution')

    plt.xlabel('Face Verification Output')
    plt.ylabel('Number Of Observations')
    plt.xlim([0.0, 4.0])
    if not normalize: plt.ylim([0.0, maxY])
    plt.title('Face verification output distribution across all profiles')
    plt.legend(loc="upper right")

    xAxis = np.linspace(0, 4, 1000)
    YAxisP = spline(xAxisP, yAxisP, xAxis)
    YAxisN = spline(xAxisN, yAxisN, xAxis)
    i = np.argwhere(np.diff(np.sign(YAxisP - YAxisN)) != 0).reshape(-1) + 0
    i = i[1:-1]
    if len(i) > 0:
        plt.plot(xAxis[i][0], YAxisP[i][0], 'ro')
        plt.text(xAxis[i][0] + 0.2, YAxisP[i][0], 'Threshold={0:0.2f}'.format(xAxis[i][0]))
    plt.show()
