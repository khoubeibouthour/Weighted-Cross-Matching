"""
Generating separate ROC curve for each profile
Look mainly for the AUC to determine the best input for each profile
"""

print(__doc__)

from time import time
import cx_Oracle, sys
import numpy as np
from sklearn.metrics import roc_curve, auc, f1_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
from itertools import cycle

start_time = time()

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()

def dmy_roc_curve(truth, prediction):
    a = np.array([15,3,8,4,1,6])
    b = np.array([5,30,18,40,111,60])
    # tt = np.stack((a,b))
    b = b[a.argsort()]
    # tt = np.sort(tt, axis=0)
    print b
    exit()

def my_roc_curve(data):
    truth = data[:, 0]
    truth = truth.astype(int)
    prediction = data[:, 1]
    prediction = prediction.astype(np.float64)
    truth = truth[prediction.argsort()]
    prediction = np.sort(prediction)

    prediction = np.insert(prediction, 0, 0)
    prediction = np.append(prediction, [4])

    tp = 0
    fn = len(truth[truth == 1])
    fp = 0
    tn = len(truth) - fn
    final_precision = float(fn) / float(fn + tn)

    tpr = np.zeros(1, np.float64)
    fpr = np.zeros(1, np.float64)
    precision = np.ones(1, np.float64)

    counter = 1
    for Y in truth:
        print "\r", counter,
        counter += 1
        if Y == 1:
            tp += 1
            fn -= 1
        else:
            fp += 1
            tn -= 1
        tpr = np.append(tpr, float(tp) / float(tp + fn))
        fpr = np.append(fpr, float(fp) / float(tn + fp))
        precision = np.append(precision, float(tp) / float(tp + fp))

    tpr = np.append(tpr, 1)
    fpr = np.append(fpr, 1)
    precision = np.append(precision, final_precision)
    return tpr, fpr, precision, prediction

def show_roc(tpr, fpr, thresholds, profile=None):
    if profile:
        label = 'ROC curve for ' + profile
        title = profile
    else:
        label = 'Global ROC grouping all profiles\' outputs'
        title = 'Global ROC'

    plt.clf()
    index = np.argmin(fpr * fpr + (1 - tpr) * (1 - tpr))
    idx = np.argwhere(np.diff(np.sign(1 - tpr - fpr)) != 0).reshape(-1) + 0
    plt.title(title + ': AUC={0:0.2f}'.format(auc(fpr, tpr)) + '   Best Threshold={0:0.2f}'.format(thresholds[index]) + '   Equal-Error={0:0.2f}'.format(thresholds[idx][0]))
    plt.plot(fpr, tpr, lw = 2, color = "blue", label=label)
    plt.plot([1, 0], c='gray', ls='--', lw=1.0)
    plt.plot(fpr[idx], tpr[idx], marker='o', markersize=6, color="#32cd32")
    plt.plot(fpr[index], tpr[index], marker='o', markersize=6, color="magenta")
    plt.text(fpr[index], tpr[index] - 0.05, 'TPR={0:0.2f}'.format(tpr[index]) + ' / FPR={0:0.2f}'.format(fpr[index]))
    plt.xlabel('False-Positive Rate')
    plt.ylabel('True-Positive Rate')
    plt.ylim([0.0, 1.0])
    plt.xlim([0.0, 1.0])
    plt.legend(loc="lower left")
    plt.show()

def show_fscore(recall, precision, thresholds, profile=None):
    list = np.logical_not(np.logical_and(precision == 0, recall == 0))
    precision = precision[list]
    recall = recall[list]
    thresholds = thresholds[list]

    if profile:
        label = 'F1 Score for ' + profile
        title = profile
    else:
        label = 'Global F1 Score'
        title = 'Global F1 Score'
    f1score = 2 * (precision * recall) / (precision + recall)

    plt.plot(thresholds, f1score, lw=2, color="blue", label=label)
    index = np.argmax(f1score)
    plt.plot(thresholds[index], f1score[index], marker='o', markersize=6, color="#32cd32")
    plt.text(thresholds[index] - 0.3, f1score[index] + 0.2, 'MAX F-SCORE')
    plt.xlabel('Thresholds')
    plt.ylabel('F-score')
    plt.title(title + ': Best F-score={0:0.2f}'.format(f1score[index]) + '   Corresponding Threshold={0:0.2f}'.format(thresholds[index]))
    plt.legend(loc="lower left")
    plt.axvline(thresholds[index], ls='--', lw=1.0, c='gray')
    plt.axhline(f1score[index], ls='--', lw=1.0, c='gray')
    plt.show()

def genROC(profile):
    print("Generating ROC curve for " + profile)
    cursor.execute("SELECT comparisons.label, comparisons.face_recog FROM comparisons, profiles WHERE comparisons.profile = profiles.profile_id AND profiles.name = '" + profile + "'")
    data = np.asarray(cursor.fetchall())

    tpr, fpr, precision, thresholds = my_roc_curve(data)

    show_roc(tpr, fpr, thresholds, profile)

    show_fscore(tpr, precision, thresholds, profile)

if len(sys.argv) == 1:
    print("Generating Multiclass ROC curve for all profiles + Global ROC")
    if sys.version_info[0] < 3:
        allORone = raw_input("Plot individual curves first? (Y/N): ").lower() in ["y", "yes"]
    else:
        allORone = input("Plot individual curves first? (Y/N): ").lower() in ["y", "yes"]

    cursor.execute("SELECT name FROM profiles ORDER BY name")
    profiles = cursor.fetchall()
    if allORone:
        for profile in profiles:
            genROC(profile[0])
    print("Generating global ROC curve")

    cursor.execute("SELECT label, face_recog FROM comparisons")
    data = np.asarray(cursor.fetchall())

    tpr, fpr, precision, thresholds = my_roc_curve(data)

    show_roc(tpr, fpr, thresholds)

    show_fscore(tpr, precision, thresholds)

else:
    profile = sys.argv[1]
    cursor.execute("SELECT profile_id FROM profiles WHERE name = '" + profile + "'")
    if cursor.fetchone() == None:
        print("Profile not found!")
        exit()
    else:
        genROC(profile)
