'''
Cross-validation using UCL and LCL as parameters for balancing
e.g. FVO(CIF, TCI) = 0.43 --> use 0.65 as input for the attraction average, etc.
'''

# import cx_Oracle
import numpy as np

# connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
# cursor = connection.cursor()

counter     = 0
frThreshold = 1.08      # Facial Recognition Threshold
# grayRange = .3          # Range of Gray Zone [FR Threshold - range, FR Threshold + range]
lowerCI     = .65            # Threshold for accepted observations      .41 first quartile      0.65 median
upperCI     = 1.67           # Threshold for rejected observations      1.97 first quartile      1.67 median
magnitude   = 1         # Weight of the original Facial recognition output

accepted    = None
discarded   = None
frDiscarded = None

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
        errorRate1 = 0
    else:
        errorRate1 = float(fn) / float(tp + fn)
    print " True faces classification:" + fillTheString(tp + fn) + "|" + fillTheString("> " + str(upperCI)) + "|" + fillTheString("> " + str(frThreshold)) + "|" + fillTheString("<= " + str(frThreshold)) + "|" + fillTheString("<= " + str(lowerCI)) + "|" + fillTheString(str(round(errorRate1 * 100, 2)) + "%") + "|"
    print "                                      |-----------------------|-----------------------|           |"
    print "                                      |" + fillTheString(ffn) + "|" + fillTheString(fn - ffn) + "|" + fillTheString(tp - ttp) + "|" + fillTheString(ttp) + "|           |"
    print "                                      |=======================|=======================|===========|"
    print "                                      |" + fillTheString(tn, 23) + "|" + fillTheString(fp, 23) + "|           |"
    print "                                      |-----------------------|-----------------------|           |"
    if tn + fp == 0:
        errorRate2 = 0
    else:
        errorRate2 = float(fp) / float(tn + fp)
    print "False faces classification:" + fillTheString(tn + fp) + "|" + fillTheString("> " + str(upperCI)) + "|" + fillTheString("> " + str(frThreshold)) + "|" + fillTheString("<= " + str(frThreshold)) + "|" + fillTheString("<= " + str(lowerCI)) + "|" + fillTheString(str(round(errorRate2 * 100, 2)) + "%") + "|"
    print "                                      |-----------------------|-----------------------|           |"
    print "                                      |" + fillTheString(ttn) + "|" + fillTheString(tn - ttn) + "|" + fillTheString(fp - ffp) + "|" + fillTheString(ffp) + "|           |"
    print "                                       =======================|=======================|==========="
    if tp + tn + fn + fp == 0:
        errorRate = 0
        accuracy = 0
        IBA = 0
    else:
        errorRate = float(fn + fp) / float(tp + tn + fn + fp)
        accuracy = float(tp + tn) / float(tp + tn + fn + fp)
        IBA = 1 - ((errorRate1 + errorRate2) / 2)
    print "\nMisclassification rate:", fn + fp, "/", tp + tn + fn + fp, "=", str(round(errorRate * 100, 2)) + "%"
    print "\nAccuracy:", tp + tn, "/", tp + tn + fn + fp, "=", str(round(accuracy * 100, 2)) + "%"
    print "\nBalanced Accuracy: AVG(" + str(round(errorRate1 * 100, 2)) + ", " + str(round(errorRate2 * 100, 2)) + ") = " + str(round(IBA * 100, 2)) + "%"
    return accuracy, IBA

def convToNumpy(input):
    return np.fromstring(input[0][1:-1], dtype=np.float64, sep=" ")

def reevaluateFR(row):
    global counter
    counter += 1
    print "\r" + str(counter) + " faces treated",

    desc = convToNumpy(row)

    countAccepted = 0
    countDiscarded = 0
    if len(accepted) > 0:
        toBeConfirmed = np.apply_along_axis(dot, 1, desc - accepted)

        countAccepted = len(toBeConfirmed[toBeConfirmed <= lowerCI])
        countDiscarded = len(toBeConfirmed[toBeConfirmed > upperCI])

    if len(discarded) > 0:
        toBeDiscarded = np.apply_along_axis(dot, 1, desc - discarded)

        countDiscarded += len(toBeDiscarded[toBeDiscarded <= lowerCI])
    return (countAccepted, countDiscarded)

def plotCurve(profile):
    # cursor.execute("SELECT description, comparisons.label, face_recog FROM comparisons, faces WHERE comparisons.face = faces.face_id AND comparisons.profile = '" + profile[0] + "'")
    # profileRow = np.asarray(cursor.fetchall())

    # Generate the CSV files by exporting the comman above for all profiles
    # 27115 rows per profile: description, label (0/1), FVO
    profileRow = np.genfromtxt('csv/' + profile + '.csv', delimiter=",", dtype="str")


    # profileRow = profileRow[:500, :]

    profileDesc   =  np.apply_along_axis(convToNumpy, 1, profileRow)
    profileLabels = profileRow[:, 1].astype(np.int8)
    profileFR     = profileRow[:, 2].astype(np.float64)

    print "Classifying", len(profileRow), "images of", profile
    print "Initial analysis:"
    accuracyBefore, IBAbefore = drawTable(
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
    global accepted, discarded
    accepted = profileDesc[profileFR <= lowerCI]
    discarded = profileDesc[upperCI < profileFR]
    reevaluated = np.apply_along_axis(func1d=reevaluateFR, axis=1, arr=profileRow[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)])
    # print reevaluated
    # print profileLabels[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)]
    countAccepted = pow(reevaluated[:, 0], 2)
    countDiscarded = pow(reevaluated[:, 1], 2)
    newFR = np.copy(profileFR)
    newFR[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)] = ((profileFR[np.logical_and(upperCI >= profileFR, profileFR > lowerCI)] * magnitude) + (countAccepted * lowerCI) + (countDiscarded * upperCI)) / (magnitude + countAccepted + countDiscarded)
    print "\nRefining using FR cross-validation:"
    accuracyAfter, IBAafter = drawTable(
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
    return (accuracyBefore, IBAbefore, accuracyAfter, IBAafter)



profiles = ["Sokhoi"]
# profiles = ["Abrha", "Astraat", "Bonji", "Heeda", "Hickam", "Hmouda", "Holu", "Khufu", "Laghbesh", "Mekah", "Mimyth", "Sakis", "Sierra", "Sokhoi", "Yakouza"]
feedback = []
for profile in profiles:
    counter = 0
    feedback.append([profile, plotCurve(profile)])

globalAccBefore = 0
globalAccAfter = 0
globalBIAbefore = 0
globalBIAafter = 0
for feed in feedback:
    print feed[0] + ":\n\t\t\taccuracy:\t" + str(round(feed[1][0] * 100, 2)) + "%     -->     " + str(round(feed[1][2] * 100, 2)) + "%\n\t\t\tIBA:\t\t" + str(round(feed[1][1] * 100, 2)) + "%     -->     " + str(round(feed[1][3] * 100, 2)) + "%"
    globalAccBefore += feed[1][0]
    globalAccAfter += feed[1][2]
    globalBIAbefore += feed[1][1]
    globalBIAafter += feed[1][3]


print "\n========================================================================\n"
print "Final report:"
print "\t\t\tAccuracy:", str(round(globalAccBefore / len(profiles) * 100, 2)) + "%     -->     " + str(round(globalAccAfter / len(profiles) * 100, 2)) + "%"
print "\t\t\tBalanced Inter-class Accuracy:", str(round(globalBIAbefore / len(profiles) * 100, 2)) + "%     -->     " + str(round(globalBIAafter / len(profiles) * 100, 2)) + "%"
# cursor.execute("SELECT profile_id, name FROM profiles ORDER BY name")
# profiles = cursor.fetchall()
# for profile in profiles:
#     plotCurve(profile)
#     break
#
# cursor.close()
# connection.close()