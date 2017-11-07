#!/usr/bin/env python

import sys
import numpy as np

frThreshold  = 1.08

def fillTheString(nbr, field = 11):
    strNbr = str(nbr)
    if len(strNbr) % 2 == 0: strNbr = " " + strNbr
    for i in range(0, (field - len(strNbr)) / 2):
        strNbr = " " + strNbr + " "
    return strNbr

def drawTable(tp, fn, tn, fp):
    if tp + fn == 0:
        errorRate1 = 0
    else:
        errorRate1 = float(fn) / float(tp + fn)

    if tn + fp == 0:
        errorRate2 = 0
    else:
        errorRate2 = float(fp) / float(tn + fp)

    output = "                                       ==========================================================="
    output += "\n                                      |           0           |           1           | Err. Rate |"
    output += "\n                                      |=======================|=======================|===========|"
    output += "\n True faces classification:" + fillTheString(tp + fn) + "|" + fillTheString(fn, 23) + "|" + fillTheString(tp, 23) + "|" + fillTheString(str(round(errorRate1 * 100, 2)) + "%") + "|"
    output += "\n                                      |=======================|=======================|===========|"
    output += "\nFalse faces classification:" + fillTheString(tn + fp) + "|" + fillTheString(tn, 23) + "|" + fillTheString(fp, 23) + "|" + fillTheString(str(round(errorRate2 * 100, 2)) + "%") + "|"
    output += "\n                                       =======================|=======================|==========="
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
    output += "\n\nMisclassification rate: " + str(fn + fp) + " / " + str(tp + tn + fn + fp) + " = " + str(round(errorRate * 100, 2)) + "%"
    output += "\nAccuracy: " + str(tp + tn) + " / " + str(tp + tn + fn + fp) + " = " + str(round(accuracy * 100, 2)) + "%"
    output += "\nBalanced Accuracy: AVG(" + str(round(errorRate1 * 100, 2)) + ", " + str(round(errorRate2 * 100, 2)) + ") = " + str(round(IBA * 100, 2)) + "%"
    output += "\nF-score: " + str(round(Fscore * 100, 2))
    return output

reportFVO      = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}
reportWeighted = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}

for result in sys.stdin:
    result = result.strip()
    FVO, Weighted = result.split(',', 1)
    try:
        reportFVO[FVO]           += 1
        reportWeighted[Weighted] += 1
    except ValueError:
        continue

accepted  = np.genfromtxt('CFS.csv', delimiter=",", dtype="str")
discarded = np.genfromtxt('DFS.csv', delimiter=",", dtype="str")

reportFVO['TP'] += len(accepted[accepted[:, 0].astype(np.int) == 1])
reportFVO['FP'] += len(accepted[accepted[:, 0].astype(np.int) == 0])
reportFVO['FN'] += len(discarded[discarded[:, 0].astype(np.int) == 1])
reportFVO['TN'] += len(discarded[discarded[:, 0].astype(np.int) == 0])

reportWeighted['TP'] += len(accepted[accepted[:, 0].astype(np.int) == 1])
reportWeighted['FP'] += len(accepted[accepted[:, 0].astype(np.int) == 0])
reportWeighted['FN'] += len(discarded[discarded[:, 0].astype(np.int) == 1])
reportWeighted['TN'] += len(discarded[discarded[:, 0].astype(np.int) == 0])

print str(reportFVO['TP']) + "," + str(reportFVO['FN']) + ',' + str(reportFVO['TN']) + ',' + str(reportFVO['FP']) + ',' + str(reportWeighted['TP']) + "," + str(reportWeighted['FN']) + ',' + str(reportWeighted['TN']) + ',' + str(reportWeighted['FP']) + '\n\n\n' + 'Initial analysis:\n' + drawTable(reportFVO['TP'], reportFVO['FN'], reportFVO['TN'], reportFVO['FP']) + '\n\nFinal analysis:\n' + drawTable(reportWeighted['TP'], reportWeighted['FN'], reportWeighted['TN'], reportWeighted['FP'])