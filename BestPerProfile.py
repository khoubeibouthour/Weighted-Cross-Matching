"""
Generating separate ROC curve for each candidate of the profile
Look mainly for the AUC to determine the best input image
"""

print(__doc__)

from time import time
import cx_Oracle, sys
import numpy as np
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
from itertools import cycle
from os.path import isfile
import cv2, exiftool, dlib, openface
from PIL import Image

start_time = time()

if len(sys.argv) < 3:
    print "In order to run a 'Best ROC Check', you must provide at least the correct profile name + a path to its image."
    exit()

for file in sys.argv[2:]:
    if not isfile(file):
        print file + " is not a valid image path."
        exit()

connection = cx_Oracle.connect('python/python')
cursor = connection.cursor()

profile = sys.argv[1]

cursor.execute("SELECT label FROM faces WHERE label = '" + profile + "'")
if cursor.fetchone() == None:
    print "No face is labeled \"" + profile + "\"\nCheck your command."
    exit()

print "Generating ROC curve(s) for " + profile

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
align = openface.AlignDlib("/home/cs0800/openface/models/dlib/shape_predictor_68_face_landmarks.dat")
net = openface.TorchNeuralNet("/home/cs0800/openface/models/openface/nn4.small2.v1.t7", 96)

counter = 0
candidates = []
for file in sys.argv[2:]:
    counter += 1
    print "\nAnalyzing file " + file + " looking for a face"
    image = cv2.imread(file)
    rgbImg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output = faceCascade.detectMultiScale3(
        rgbImg,
        scaleFactor=1.3,
        minNeighbors=4,
        flags = cv2.CASCADE_SCALE_IMAGE,
        outputRejectLevels = True,
        minSize = (30, 30)
    )
    if len(output[0]) == 0:
        print "No face detected in " + file
        exit()
    if len(output[0]) > 1:
        print "More than one face detected. Check the generated \"multi-" + file + "\" for details"
        for (x, y, w, h) in output[0]:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 5)
        cv2.imwrite("multi-" + file, image)
        img = Image.open('multi-' + file)
        img.show()
        img.close()
        exit()
    else:
        print "1 Face detected. Proceeding with description [file: " + file + "]"
        img = Image.open(file)
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(file)
            if "EXIF:Orientation" in metadata:
                if metadata["EXIF:Orientation"] == 3:
                    img = img.rotate(180, expand=True)
                elif metadata["EXIF:Orientation"] == 6:
                    img = img.rotate(270, expand=True)
                elif metadata["EXIF:Orientation"] == 8:
                    img = img.rotate(90, expand=True)
            (x, y, w, h) = output[0][0]
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 5)
            cv2.imwrite("Faced-" + file, image)
            face = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
            alignedFace = align.align(96, rgbImg, face, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
            if alignedFace is None:
                print "Failed to align face in " + file
                exit()
            rep = net.forward(alignedFace)
            img.crop((face.left(), face.top(), face.right(), face.bottom())).save(profile + "-face-" + str(counter) + ".jpg")
            img.close()
            print "Description from '" + file + "' completed."
            candidates.append([file, rep, np.empty([0, 1])])

print "\nStarting comparison phase..."


cursor.execute("SELECT label, description FROM faces")

response = np.asarray(cursor.fetchall())

globalTruth = response[:, 0]
globalTruth[globalTruth == profile] = 1
globalTruth[globalTruth != '1'] = 0
globalTruth = globalTruth.astype(int)

faces = response[:, 1]
totalFaces = str(len(faces))
counter = 0
for face in faces:
    counter += 1
    for candidate in candidates:
        d = candidate[1] - np.fromstring(face[1:-1], dtype=float, sep=" ")
        candidate[2] = np.append(candidate[2], np.array([1 - (np.dot(d, d) / 4)]))
    print "\rCompairing " + str(counter) + " / " + totalFaces + "               ",

plt.clf()
colors = cycle(['navy', 'turquoise', 'darkorange', 'cornflowerblue', 'teal', 'tomato', 'purple', 'magenta'])
minDistance = 0
for candidate, color in zip(candidates, colors):
    file, _, compareTable = candidate
    fpr, tpr, thresholds = roc_curve(globalTruth, compareTable)
    # print 'AUC:', auc(fpr, tpr) ' == ROC AUC:', roc_auc_score(globalTruth, compareTable)
    index = np.argmin(fpr * fpr + (1 - tpr) * (1 - tpr))
    idx = np.argwhere(np.diff(np.sign(1 - tpr - fpr)) != 0).reshape(-1) + 0
    plt.plot(fpr, tpr, lw=1, color=color, label='ROC ' + file + '  AUC={0:0.2f}'.format(auc(fpr, tpr)) + '  Threshold={0:0.2f}'.format((1 - thresholds[index]) * 4) + '  Equal-Error={0:0.2f}'.format((1 - thresholds[idx][0]) * 4))
    plt.plot(fpr[index], tpr[index], marker='o', markersize=5, color="blue")
    plt.plot(fpr[idx], tpr[idx], marker='o', markersize=3, color="red")
plt.xlabel('False-Positive Rate')
plt.ylabel('True-Positive Rate')
plt.plot([1, 0], c='black', ls='--', lw=1.0)
# https://matplotlib.org/users/pyplot_tutorial.html
plt.ylim([0.0, 1.0])
plt.xlim([0.0, 1.0])
plt.title('Receiver Operating Characteristic [ROC] curve for ' + profile)
plt.legend(loc="lower left")
print "\n\nExecution time: " + str(time() - start_time) + " seconds"
plt.show()
