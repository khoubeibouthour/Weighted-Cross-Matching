'''
Cross-validation using UCL and LCL as parameters for balancing
e.g. FVO(CIF, TCI) = 0.43 --> use 0.65 as input for the attraction average, etc.
'''

import numpy as np
import datetime
import gpxpy.geo

counter     = 0
frThreshold = 1.08      # Facial Recognition Threshold
# grayRange = .3          # Range of Gray Zone [FR Threshold - range, FR Threshold + range]
lowerCI     = .65            # Threshold for accepted observations      .41 first quartile      0.65 median
upperCI     = 1.67           # Threshold for rejected observations      1.97 first quartile      1.67 median
magnitude   = 1         # Weight of the original Facial recognition output

accepted    = None
discarded   = None

weightFactor = 6. # number of predictors: path, nbr_faces, filesize, timeframe, location, camera (resolution + orientation  are correlated with other predictors)

CIF = None

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
    precision = float(tp) / float(tp + fp)
    recall    = float(tp) / float(tp + fn)
    Fscore    = 2 * precision * recall / (precision + recall)
    print "\nMisclassification rate:", fn + fp, "/", tp + tn + fn + fp, "=", str(round(errorRate * 100, 2)) + "%"
    print "\nAccuracy:", tp + tn, "/", tp + tn + fn + fp, "=", str(round(accuracy * 100, 2)) + "%"
    print "\nBalanced Accuracy: AVG(" + str(round(errorRate1 * 100, 2)) + ", " + str(round(errorRate2 * 100, 2)) + ") = " + str(round(IBA * 100, 2)) + "%"
    print "\nF-score: " + str(round(Fscore * 100, 2))
    return accuracy, IBA

def convToNumpy(input):
    return np.fromstring(input[11][1:-1], dtype=np.float64, sep=" ")

def checkWeights(TCI):
    descCIF = np.fromstring(CIF[11][1:-1], dtype=np.float64, sep=" ")
    descTCI = np.fromstring(TCI[11][1:-1], dtype=np.float64, sep=" ")
    d = descCIF - descTCI
    FVO = np.dot(d, d)
    if FVO <= lowerCI:     return weightFactor, 0.
    if FVO >  upperCI:     return 0., 1.
    if FVO >  frThreshold: return 0., 0.

    weight = 0.
    if TCI[2]  == CIF[2]:  weight += 1                                              # same path ?
    if TCI[3]  == CIF[3]:  weight += 1                                              # same number of faces ?
    if abs(TCI[4].astype(np.int) - CIF[4].astype(np.int)) <= 200000:  weight += 1   # same file size (within a reasonable margin: 200KB) ?
    # if TCI[5]  == CIF[5]:  weight += 1                                              # same resolution ?
    if TCI[6] != '' and CIF[6] != '':                                               # same timeframe (5 minutes) ?
        t1 = datetime.datetime.strptime(TCI[6], "%d-%b-%Y %H:%M:%S")
        t2 = datetime.datetime.strptime(CIF[6], "%d-%b-%Y %H:%M:%S")
        if abs(t1 - t2) <= datetime.timedelta(minutes=5): weight += 1
    if TCI[7] != '' and CIF[7] != '' and TCI[8] != '' and CIF[8] != '':             # same location (150 meters) ?
        if gpxpy.geo.haversine_distance(TCI[8].astype(np.float64), TCI[7].astype(np.float64), CIF[8].astype(np.float64), CIF[7].astype(np.float64)) < 150: weight += 1
    # if TCI[9]  == CIF[9]:  weight += 1                                              # same orientation ?
    if TCI[10] == CIF[10]: weight += 1                                              # same camera ?
    return 1 / weightFactor + weight, 0.

def reevaluateFR(row):
    global counter
    counter += 1
    print "\r" + str(counter) + " faces treated",

    global CIF
    CIF = row

    alpha = 0
    beta = 0

    if len(accepted) > 0:
        toBeConfirmed = np.apply_along_axis(checkWeights, 1, accepted)
        alpha = pow(np.sum(toBeConfirmed[:, 0]), 2)
        beta = np.sum(toBeConfirmed[:, 1])

    if len(discarded) > 0:
        toBeDiscarded = np.apply_along_axis(checkWeights, 1, discarded)
        beta  = pow(beta + np.sum(toBeDiscarded[:, 0]), 2)

    # print 'Alpha=', alpha, ', Beta=', beta, row[1].astype(np.float64), '-->', (alpha * lowerCI + magnitude * row[1].astype(np.float64) + beta * upperCI) / (alpha + magnitude + beta), '[' + row[0] + ']'

    return (alpha * lowerCI + magnitude * row[1].astype(np.float64) + beta * upperCI) / (alpha + magnitude + beta)

def plotCurve(profile):
    # Generate the CSV files by exporting the comman above for all profiles
    # 27115 rows per profile: label (0/1), FVO, path, nbrFaces, filesize, resolution, date, longitude, latitude, orientation, model, description
    profileRow = np.genfromtxt('Metadata/' + profile + '.csv', delimiter=",", dtype="str")
    # profileRow = profileRow[:500, :]
    FVOs   = profileRow[:, 1].astype(np.float64)
    Labels = profileRow[:, 0].astype(np.int)

    print "Classifying", len(profileRow), "images of", profile
    print "Initial analysis:"
    accuracyBefore, IBAbefore = drawTable(
        len(FVOs[np.logical_and(FVOs <= frThreshold, Labels == 1)]),
        len(FVOs[np.logical_and(FVOs >  frThreshold, Labels == 1)]),
        len(FVOs[np.logical_and(FVOs >  frThreshold, Labels == 0)]),
        len(FVOs[np.logical_and(FVOs <= frThreshold, Labels == 0)]),
        len(FVOs[np.logical_and(FVOs <= lowerCI,     Labels == 1)]),
        len(FVOs[np.logical_and(FVOs >  upperCI,     Labels == 1)]),
        len(FVOs[np.logical_and(FVOs >  upperCI,     Labels == 0)]),
        len(FVOs[np.logical_and(FVOs <= lowerCI,     Labels == 0)])
    )

    print "\nStarting triage of gray zone:", len(FVOs[np.logical_and(upperCI >= FVOs, FVOs > lowerCI)]), "=", len(FVOs[np.logical_and(np.logical_and(upperCI >= FVOs, FVOs > lowerCI), Labels == 1)]), "[1] +", len(FVOs[np.logical_and(np.logical_and(upperCI >= FVOs, FVOs > lowerCI), Labels == 0)]), "[0]"

    global accepted, discarded
    accepted = profileRow[FVOs <= lowerCI]
    discarded = profileRow[upperCI < FVOs]

    newFR = np.copy(FVOs)
    newFR[np.logical_and(upperCI >= FVOs, FVOs > lowerCI)] = np.apply_along_axis(func1d=reevaluateFR, axis=1, arr=profileRow[np.logical_and(upperCI >= FVOs, FVOs > lowerCI)])

    print "\nRefining using FR cross-validation:"
    accuracyAfter, IBAafter = drawTable(
        len(newFR[np.logical_and(newFR <= frThreshold, Labels == 1)]),
        len(newFR[np.logical_and(newFR >  frThreshold, Labels == 1)]),
        len(newFR[np.logical_and(newFR >  frThreshold, Labels == 0)]),
        len(newFR[np.logical_and(newFR <= frThreshold, Labels == 0)]),
        len(newFR[np.logical_and(newFR <= lowerCI,     Labels == 1)]),
        len(newFR[np.logical_and(newFR >  upperCI,     Labels == 1)]),
        len(newFR[np.logical_and(newFR >  upperCI,     Labels == 0)]),
        len(newFR[np.logical_and(newFR <= lowerCI,     Labels == 0)])
    )
    print "\n=====================================================================================================\n"
    print "\n                         Completed processing data for " + profile + "\n"
    print "\n=====================================================================================================\n"
    return (accuracyBefore, IBAbefore, accuracyAfter, IBAafter)



# profiles = ["Abrha", "Astraat", "Bonji", "Heeda", "Hickam", "Hmouda", "Holu", "Khufu", "Laghbesh", "Mekah", "Mimyth", "Sakis", "Sierra", "Sokhoi", "Yakouza"]
profiles = ["Mimyth"]

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