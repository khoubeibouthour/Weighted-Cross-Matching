#!/usr/bin/env python
import sys
import numpy as np
import datetime
from gpxpy.geo import haversine_distance

weightFactor = 3.
magnitude    = 1.
lowerCI      = .65
frThreshold  = 1.08
upperCI      = 1.67
CIF = None

accepted  = np.genfromtxt('CFS.csv', delimiter=",", dtype="str")
discarded = np.genfromtxt('DFS.csv', delimiter=",", dtype="str")

def checkWeights(TCI):
    descCIF = np.fromstring(CIF[9][1:-1], dtype=np.float64, sep=" ")
    descTCI = np.fromstring(TCI[9][1:-1], dtype=np.float64, sep=" ")
    d = descCIF - descTCI
    FVO = np.dot(d, d)

    if FVO <= lowerCI:     return weightFactor, 0.
    if FVO >  upperCI:     return 0., 1.
    if FVO >  frThreshold: return 0., 0.

    weight = 0.
    if TCI[2]  == CIF[2]:  weight += 1.                                             # same path
    if TCI[3]  == CIF[3]:  weight += 1.                                             # same number of faces ?
    if abs(int(TCI[4]) - int(CIF[4])) <= 200000:  weight += 1.                       # same file size (within a reasonable margin: 200KB) ?
    if TCI[5] != '' and CIF[5] != '':                                               # same timeframe (5 minutes) ?
        t1 = datetime.datetime.strptime(TCI[5], "%d-%b-%Y %H:%M:%S")
        t2 = datetime.datetime.strptime(CIF[5], "%d-%b-%Y %H:%M:%S")
        if abs(t1 - t2) <= datetime.timedelta(minutes=5): weight += 1.
    if TCI[6] != '' and CIF[6] != '' and TCI[7] != '' and CIF[7] != '':             # same location (150 meters) ?
        if haversine_distance(float(TCI[6]), float(TCI[7]), float(CIF[6]), float(CIF[7])) < 150: weight += 1.
    if TCI[8] == CIF[8]: weight += 1.                                               # same camera ?
    return 1. / weightFactor + weight, 0.

for line in sys.stdin:
    line = line.strip()
    CIF = line.split(',')

    if float(CIF[1]) <= frThreshold:
        if CIF[0] == '1':
            output = 'TP'
        else:
            output = 'FP'
    else:
        if CIF[0] == '1':
            output = 'FN'
        else:
            output = 'TN'

    alpha = 0
    beta = 0

    if len(accepted) > 0:
        toBeConfirmed = np.apply_along_axis(checkWeights, 1, accepted)
        alpha = pow(np.sum(toBeConfirmed[:, 0]), 2)
        beta = np.sum(toBeConfirmed[:, 1])

    if len(discarded) > 0:
        toBeDiscarded = np.apply_along_axis(checkWeights, 1, discarded)
        beta  = pow(beta + np.sum(toBeDiscarded[:, 0]), 2)

    if (alpha * lowerCI + magnitude * float(CIF[1]) + beta * upperCI) / (alpha + magnitude + beta) <= frThreshold:
        if CIF[0] == '1':
            output += ',TP'
        else:
            output += ',FP'
    else:
        if CIF[0] == '1':
            output += ',FN'
        else:
            output += ',TN'

    print output