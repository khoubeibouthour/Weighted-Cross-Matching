import cx_Oracle
import numpy as np
import matplotlib.pyplot as plt

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()

def plotCurve(profile = ""):
    query = ""
    if profile: query = " WHERE profile = '" + profile[0] + "'"
    cursor.execute("SELECT face_recog, label FROM comparisons" + query + " ORDER BY face_recog")
    rows = cursor.fetchall()
    response = np.asarray(rows)
    FVO = response[:, 0]
    Truth = response[:, 1]
    TP = np.empty(0, np.float64)
    TN = np.empty(0, np.float64)

    totalLess = 0.
    totalMore = float(len(FVO))
    ones = 0.
    zeros = totalMore - np.sum(Truth)

    for row in rows:
        totalLess += 1
        ones += row[1]
        TP = np.append(TP, ones / totalLess)
        totalMore -= 1
        zeros -= 1 - row[1]
        if totalMore == 0:
            TN = np.append(TN, 1)
        else:
            TN = np.append(TN, zeros / totalMore)


    idx95TP = np.argwhere(np.diff(np.sign(TP - 0.95)) != 0).reshape(-1)
    idx95TN = np.argwhere(np.diff(np.sign(TN - 0.95)) != 0).reshape(-1)

    plt.clf()
    plt.axhline(y=0.95, c='gray', ls='--', lw=0.5)

    if len(idx95TP) > 0:
        idx95TP = idx95TP[0]
        plt.axvline(x=FVO[idx95TP], c='gray', ls='--', lw=0.5)
        plt.plot(FVO[idx95TP], .95, marker='o', markersize=6, color="magenta")
        plt.text(FVO[idx95TP] + .005, .005, '{0:0.2f}'.format(FVO[idx95TP]), color="r")

    if len(idx95TN) > 0:
        idx95TN = idx95TN[0]
        plt.axvline(x=FVO[idx95TN], c='gray', ls='--', lw=0.5)
        plt.plot(FVO[idx95TN], .95, marker='o', markersize=6, color="#32cd32")
        plt.text(FVO[idx95TN] + .005, .005, '{0:0.2f}'.format(FVO[idx95TN]), color="r")

    plt.text(2.2, 0.90, '95% Confidence')

    plt.plot(FVO, TP, lw=1.0, color="blue", label='TP / total for observations < threshold')
    plt.plot(FVO, TN, lw=1.0, color="red", label='TN / total for observations > threshold')
    # plt.ylim([0.0, 1.02])
    # plt.xlim([0.0, 4.0])
    if profile:
        plt.title(profile[1])
    else:
        plt.title("95%-Confidence Thresholds")

    plt.legend(loc="lower right")
    plt.show()

# cursor.execute("SELECT profile_id, name FROM profiles ORDER BY name")
# profiles = cursor.fetchall()
# for profile in profiles:
#     plotCurve(profile)

plotCurve()
cursor.close()
connection.close()