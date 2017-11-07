# import cx_Oracle
import numpy as np

# connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
# cursor = connection.cursor()

counter = 0
frThreshold = 1.08      # Facial Recognition Threshold
# grayRange = .3          # Range of Gray Zone [FR Threshold - range, FR Threshold + range]
lowerCI = .65            # Threshold for accepted observations      .41 first quartile      0.65 median
upperCI = 1.67           # Threshold for rejected observations      1.97 first quartile      1.67 median
magnitude = 1         # Weight of the original Facial recognition output

def dot(el):
    return np.dot(el, el)

def fillTheString(nbr, field = 11):
    strNbr = str(nbr)
    if len(strNbr) % 2 == 0: strNbr = " " + strNbr
    for i in range(0, (field - len(strNbr)) / 2):
        strNbr = " " + strNbr + " "
    return strNbr

def drawTable(tp, fn, tn, fp, ttp, ffn, ttn, ffp):
    print "                                       ==========================================================="
    print "                                      |           0           |           1           | Err. Rate |"
    print "                                      |=======================|=======================|===========|"
    print "                                      |" + fillTheString(fn, 23) + "|" + fillTheString(tp, 23) + "|           |"
    print "                                      |-----------------------|-----------------------|           |"
    if tp + fn == 0:
        errorRate = 0
    else:
        errorRate = float(fn) / float(tp + fn)
    print " True faces classification:" + fillTheString(tp + fn) + "|" + fillTheString("> " + str(upperCI)) + "|" + fillTheString("> " + str(frThreshold)) + "|" + fillTheString("<= " + str(frThreshold)) + "|" + fillTheString("<= " + str(lowerCI)) + "|" + fillTheString(str(round(errorRate * 100, 2)) + "%") + "|"
    print "                                      |-----------------------|-----------------------|           |"
    print "                                      |" + fillTheString(ffn) + "|" + fillTheString(fn - ffn) + "|" + fillTheString(tp - ttp) + "|" + fillTheString(ttp) + "|           |"
    print "                                      |=======================|=======================|===========|"
    print "                                      |" + fillTheString(tn, 23) + "|" + fillTheString(fp, 23) + "|           |"
    print "                                      |-----------------------|-----------------------|           |"
    if tn + fp == 0:
        errorRate = 0
    else:
        errorRate = float(fp) / float(tn + fp)
    print "False faces classification:" + fillTheString(tn + fp) + "|" + fillTheString("> " + str(upperCI)) + "|" + fillTheString("> " + str(frThreshold)) + "|" + fillTheString("<= " + str(frThreshold)) + "|" + fillTheString("<= " + str(lowerCI)) + "|" + fillTheString(str(round(errorRate * 100, 2)) + "%") + "|"
    print "                                      |-----------------------|-----------------------|           |"
    print "                                      |" + fillTheString(ttn) + "|" + fillTheString(tn - ttn) + "|" + fillTheString(fp - ffp) + "|" + fillTheString(ffp) + "|           |"
    print "                                       =======================|=======================|==========="
    if tp + tn + fn + fp == 0:
        errorRate = 0
        accuracy = 0
    else:
        errorRate = float(fn + fp) / float(tp + tn + fn + fp)
        accuracy = float(tp + tn) / float(tp + tn + fn + fp)
    print "\nMisclassification rate:", fn + fp, "/", tp + tn + fn + fp, "=", str(round(errorRate * 100, 2)) + "%"
    print "\nAccuracy:", tp + tn, "/", tp + tn + fn + fp, "=", str(round(accuracy * 100, 2)) + "%"
    return errorRate

def convToNumpy(input):
    return np.fromstring(input[0][1:-1], dtype=np.float64, sep=" ")

def reevaluateFR(row, accepted, discarded, frDiscarded):
    desc = convToNumpy(row)
    global counter
    counter += 1
    print "\r" + str(counter) + " faces treated",
    if len(accepted) == 0:
        averageAccepted = 0
        weightAccepted = 0
        averageRepelled = 0
        weightRepelled = 0
    else:
        toBeConfirmed = np.apply_along_axis(dot, 1, desc - accepted)
        weightAccepted = len(toBeConfirmed[toBeConfirmed <= lowerCI])
        averageAccepted = np.sum(toBeConfirmed[toBeConfirmed <= lowerCI]) * weightAccepted
        weightAccepted = pow(weightAccepted, 2)
        weightRepelled = len(toBeConfirmed[toBeConfirmed > upperCI])
        averageRepelled = np.sum(toBeConfirmed[toBeConfirmed > upperCI]) * weightRepelled
        weightRepelled = pow(weightRepelled, 2)
    if len(discarded) == 0:
        averageDiscarded = 0
        weightDiscarded = 0
    else:
        toBeDiscarded = np.apply_along_axis(dot, 1, desc - discarded)
        weightDiscarded = len(toBeDiscarded[toBeDiscarded <= lowerCI])
        averageDiscarded = np.sum(frDiscarded[toBeDiscarded <= lowerCI]) * weightDiscarded
        weightDiscarded = pow(weightDiscarded, 2)

    average = averageAccepted + averageRepelled + averageDiscarded
    weight = weightAccepted + weightRepelled + weightDiscarded
    # if weight > 0:
    #     newFR = (magnitude * float(row[2]) + average) / (magnitude + weight)
        # if (float(row[2]) <= frThreshold and newFR > frThreshold) or (float(row[2]) > frThreshold and newFR <= frThreshold):
        #     print "Face", counter, "[" + row[3] + "] labeled \"" + row[1] + "\" with FR=[" + row[2] + "]:", len(toBeConfirmed[toBeConfirmed <= lowerCI]), "-->", newFR, "<--", len(toBeConfirmed[toBeConfirmed > upperCI]) + len(toBeDiscarded[toBeDiscarded <= lowerCI])
    return (average, weight)

def plotCurve(profile):
    # cursor.execute("SELECT description, comparisons.label, face_recog FROM comparisons, faces WHERE comparisons.face = faces.face_id AND comparisons.profile = '" + profile[0] + "'")
    # profileRow = np.asarray(cursor.fetchall())

    # Generate the CSV files by exporting the comman above for all profiles
    # 27115 rows per profile: description, label (0/1), FVO
    profileRow = np.genfromtxt('csv/' + profile + '.csv', delimiter=",", dtype="str")


    # profileRow = profileRow[:5000, :]
    profileDesc   =  np.apply_along_axis(convToNumpy, 1, profileRow)
    profileLabels = profileRow[:, 1].astype(np.int8)
    profileFR     = profileRow[:, 2].astype(np.float64)

    print "Classifying", len(profileRow), "images of", profile
    print "Initial analysis:"
    errorRateBefore = drawTable(
        len(profileFR[np.logical_and(profileFR <= frThreshold, profileLabels == 1)]),
        len(profileFR[np.logical_and(profileFR > frThreshold, profileLabels == 1)]),
        len(profileFR[np.logical_and(profileFR > frThreshold, profileLabels == 0)]),
        len(profileFR[np.logical_and(profileFR <= frThreshold, profileLabels == 0)]),
        len(profileFR[np.logical_and(profileFR <= lowerCI, profileLabels == 1)]),
        len(profileFR[np.logical_and(profileFR > upperCI, profileLabels == 1)]),
        len(profileFR[np.logical_and(profileFR > upperCI, profileLabels == 0)]),
        len(profileFR[np.logical_and(profileFR <= lowerCI, profileLabels == 0)])
    )
    print "\nStarting triage of gray zone:", len(profileFR[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)]), "=", len(profileFR[np.logical_and(np.logical_and(upperCI >= profileFR, profileFR > lowerCI), profileLabels == 1)]), "[1] +", len(profileFR[np.logical_and(np.logical_and(upperCI >= profileFR, profileFR > lowerCI), profileLabels == 0)]), "[0]"
    # reevaluated = np.apply_along_axis(func1d=reevaluateFR, axis=1, arr=profileDesc[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)], accepted=profileDesc[profileFR <= lowerCI], discarded=profileDesc[upperCI < profileFR], frDiscarded=profileFR[upperCI < profileFR])
    reevaluated = np.apply_along_axis(func1d=reevaluateFR, axis=1, arr=profileRow[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)], accepted=profileDesc[profileFR <= lowerCI], discarded=profileDesc[upperCI < profileFR], frDiscarded=profileFR[upperCI < profileFR])
    average = reevaluated[:, 0]
    weight = reevaluated[:, 1]
    newFR = np.copy(profileFR)
    newFR[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)] = (profileFR[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)] * magnitude + average) / (magnitude + weight)
    print "\nRefining using FR cross-validation:"
    errorRateAfter = drawTable(
        len(newFR[np.logical_and(newFR <= frThreshold, profileLabels == 1)]),
        len(newFR[np.logical_and(newFR > frThreshold, profileLabels == 1)]),
        len(newFR[np.logical_and(newFR > frThreshold, profileLabels == 0)]),
        len(newFR[np.logical_and(newFR <= frThreshold, profileLabels == 0)]),
        len(newFR[np.logical_and(newFR <= lowerCI, profileLabels == 1)]),
        len(newFR[np.logical_and(newFR > upperCI, profileLabels == 1)]),
        len(newFR[np.logical_and(newFR > upperCI, profileLabels == 0)]),
        len(newFR[np.logical_and(newFR <= lowerCI, profileLabels == 0)])
    )
    print "\n=====================================================================================================\n"
    print "\n                         Completed processing data for " + profile + "\n"
    print "\n=====================================================================================================\n"
    return (errorRateBefore, errorRateAfter)



profiles = ["Abrha", "Astraat", "Bonji", "Heeda", "Hickam", "Hmouda", "Holu", "Khufu", "Laghbesh", "Mekah", "Mimyth", "Sakis", "Sierra", "Sokhoi", "Yakouza"]
feedback = []
for profile in profiles:
    counter = 0
    feedback.append([profile, plotCurve(profile)])

globalBefore = 0
globalAfter = 0
for feed in feedback:
    print feed[0] + ":      ", str(round(feed[1][0] * 100, 2)) + "% --> " + str(round(feed[1][1] * 100, 2)) + "%        ", str(round((1 - feed[1][0]) * 100, 2)) + "% --> " + str((1 - round(feed[1][1]) * 100, 2)) + "%"
    globalBefore += feed[1][0]
    globalAfter += feed[1][1]

print "\n========================================================================\n"
print "Final report:"
print "Misclassification rate change:", str(round(globalBefore / len(profiles) * 100, 2)) + "% --> " + str(round(globalAfter / len(profiles) * 100, 2)) + "%"
print "Sucess rate change:", str(round(100 - (globalBefore / len(profiles)) * 100, 2)) + "% --> " + str(round(100 - (globalAfter / len(profiles)) * 100, 2)) + "%"
# cursor.execute("SELECT profile_id, name FROM profiles ORDER BY name")
# profiles = cursor.fetchall()
# for profile in profiles:
#     plotCurve(profile)
#     break
#
# cursor.close()
# connection.close()