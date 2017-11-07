import sys, cx_Oracle
from time import time
import numpy as np

start_time = time()

if len(sys.argv) == 1:
    if input("Must provide the profile's name. Do you want to use the defauls? Abrha [Y/N]: ") in ['y', 'Y']:
        person = "Abrha"
    else:
        exit()
else:
    person = sys.argv[1]

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()
cursor.execute("SELECT profile_id, description FROM profiles WHERE name = '" + person + "'")
profile = cursor.fetchone()
if profile == None:
    print("Profile not found!")
    exit()

cursor.execute("SELECT COUNT(0) FROM comparisons WHERE profile = '" + profile[0] + "'")
if int(cursor.fetchone()[0] ) > 0:
    if input("This profile was already treated. Do you want to process it anyway? [Y/N]: ") in ['y', 'Y']:
        cursor.execute("DELETE FROM comparisons WHERE profile = '" + profile[0] + "'")
    else:
        exit()

print("Starting comparison...")
#cursor.execute("SELECT COUNT(*) FROM faces WHERE label <> 'False Positive'")
cursor.execute("SELECT COUNT(*) FROM faces")
totalFaces = str(cursor.fetchone()[0])
counter = 0
#cursor.execute("SELECT face_id, description FROM faces WHERE label <> 'False Positive'")
profileID = profile[0]
profileDescription = np.fromstring(profile[1][1:-1], dtype=float, sep=" ")

cursor.execute("SELECT face_id, description FROM faces")
faces = cursor.fetchall()
print(faces.shape)
exit()
for face in faces:
    counter += 1
    faceDescription = np.fromstring(face[1][1:-1], dtype=float, sep=" ")
    d = profileDescription - faceDescription
    diff = np.dot(d, d)
    print("\rCompairing " + str(counter) + " / " + totalFaces + " : {:0.3f}          ".format(diff),)
    cursor.execute("INSERT INTO comparisons (profile, face, face_recog) VALUES ('" + profileID + "', '" + face[0] + "', " + str(diff) + ")")

cursor.close()
connection.commit()
connection.close()

print("\n\nExecution terminated: " + str(time() - start_time) + " seconds")
