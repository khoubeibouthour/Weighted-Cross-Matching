#!/usr/bin/env python
import sys
import numpy as np
import datetime
from gpxpy.geo import haversine_distance

weightFactor = 3.
magnitude    = 100.
lowerCI      = .65
frThreshold  = 1.08
upperCI      = 1.67
CIF = None
descCIF = None

accepted  = np.genfromtxt('CFS.csv', delimiter=",", dtype="str")
discarded = np.genfromtxt('DFS.csv', delimiter=",", dtype="str")

def checkWeights(TCI):
    descTCI = np.fromstring(TCI[9][1:-1], dtype=np.float64, sep=" ")
    d = descCIF - descTCI
    FVO = np.dot(d, d)

    if FVO <= lowerCI : return 1., 0.
    if upperCI < FVO  : return 0., 1.
    return 0., 0.

for line in sys.stdin:
    line = line.strip()
    CIF = line.split(',')
    descCIF = np.fromstring(CIF[9][1:-1], dtype=np.float64, sep=" ")

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
    beta  = 0
    gamma = 0

    if len(accepted) > 0:
        toBeConfirmed = np.apply_along_axis(checkWeights, 1, accepted)
        alpha = np.sum(toBeConfirmed[:, 0])
        beta  = np.sum(toBeConfirmed[:, 1])

    if len(discarded) > 0:
        toBeDiscarded = np.apply_along_axis(checkWeights, 1, discarded)
        gamma = np.sum(toBeDiscarded[:, 0])

    alpha = pow(alpha, 2)
    beta  = pow(beta,  2)
    gamma = pow(gamma, 2)

    if (alpha * lowerCI + magnitude * float(CIF[1]) + beta * upperCI + gamma * upperCI) / (alpha + magnitude + beta + gamma) <= frThreshold:
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