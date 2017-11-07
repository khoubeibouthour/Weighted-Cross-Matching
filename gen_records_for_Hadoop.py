import cx_Oracle
import gpxpy.geo
import numpy as np
from time import time

totalExecutionTime = time()

fields = {
    "face_id":            0,
    "description":        1,
    "label":              2,
    "image":              3,
    "path":               4,
    "nbr_faces":          5,
    # "mimetype":           6,
    "fileaccessdate":     7,
    "filemodifydate":     8,
    "filesize":           9,
    # "filetype":           10,
    # "filetypeextension":  11,
    "imageheight":        12,
    "imagewidth":         13,
    "datetimeoriginal":   14,
    "createdate":         15,
    "modifydate":         16,
    "exifimageheight":    17,
    "exifimagewidth":     18,
    "gpslongitude":       19,
    "gpslatitude":        20,
    "gpsaltitude":        21,
    "gpsimgdirection":    22,
    "gpslongituderef":    23,
    "gpslatituderef":     24,
    "gpsaltituderef":     25,
    "gpsimgdirectionref": 26,
    "gpstimestamp":       27,
    "orientation":        28,
    "flash":              29,
    "make":               30,
    "model":              31
}

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()
cursor.execute("SELECT face_id, description, label, image, "
               "path, "
               "nbr_faces, "
               # "mimetype, "
               "fileaccessdate, "
               "filemodifydate, "
               "filesize, "
               # "filetype, "
               # "filetypeextension, "
               "imageheight, "
               "imagewidth, "
               "datetimeoriginal, "
               "createdate, "
               "modifydate, "
               "exifimageheight, "
               "exifimagewidth, "
               "gpslongitude, "
               "gpslatitude, "
               "gpsaltitude, "
               "gpsimgdirection, "
               "gpslongituderef, "
               "gpslatituderef, "
               "gpsaltituderef, "
               "gpsimgdirectionref, "
               "gpstimestamp, "
               "orientation, "
               "flash, "
               "make, "
               "model FROM faces, images WHERE image = image_id AND label <> 'Others' AND treatedForHadoop = 0 ORDER BY face_id")

faces = cursor.fetchall()
totalToCompare = len(faces)
counter = 1
for face in faces:
#############################################################################################################
    f = open("./queriesForHadoop/" + face[fields["face_id"]] + ".txt", "w+")
    # f.write('"face1_id","face2_id","same_path","diff_nbr_faces","same_mimetype","diff_fileaccessdate","diff_filemodifydate","diff_filesize","same_filetype","same_filetypeextension","same_imageheight","same_imagewidth","diff_datetimeoriginal","diff_createdate","diff_modifydate","same_exifimageheight","same_exifimagewidth","distance","diff_gpsaltitude","diff_gpsimgdirection","same_gpslongituderef","same_gpslatituderef","same_gpsaltituderef","same_gpsimgdirectionref","same_orientation","same_flash","same_make","same_model","fr","neighbor"')
    f.write('"face1_id","face2_id","same_path","diff_nbr_faces","diff_fileaccessdate","diff_filemodifydate","diff_filesize","same_imageheight","same_imagewidth","diff_datetimeoriginal","diff_createdate","diff_modifydate","same_exifimageheight","same_exifimagewidth","distance","diff_gpsaltitude","diff_gpsimgdirection","same_gpslongituderef","same_gpslatituderef","same_gpsaltituderef","same_gpsimgdirectionref","same_orientation","same_flash","same_make","same_model","fr","neighbor"')
#############################################################################################################
    startTime = time()
    print("***********************************************************************")
    print("Comparing labeled face " + str(counter) + "/" + str(totalToCompare) + " '" + face[fields["face_id"]] + "'")
    cursor.execute("SELECT face_id, description, label, image, "
                   "path, "
                   "nbr_faces, "
                   # "mimetype, "
                   "fileaccessdate, "
                   "filemodifydate, "
                   "filesize, "
                   # "filetype, "
                   # "filetypeextension, "
                   "imageheight, "
                   "imagewidth, "
                   "datetimeoriginal, "
                   "createdate, "
                   "modifydate, "
                   "exifimageheight, "
                   "exifimagewidth, "
                   "gpslongitude, "
                   "gpslatitude, "
                   "gpsaltitude, "
                   "gpsimgdirection, "
                   "gpslongituderef, "
                   "gpslatituderef, "
                   "gpsaltituderef, "
                   "gpsimgdirectionref, "
                   "gpstimestamp, "
                   "orientation, "
                   "flash, "
                   "make, "
                   "model FROM faces, images WHERE image = image_id AND image <> '" + face[fields['image']] + "' AND treatedForHadoop = 0")
    sub_faces = cursor.fetchall()
    print("Query time: " + str(round(time() - startTime, 1)) + " seconds")
    print("Comparing to " + str(len(sub_faces)) + " faces")
    # counter2 = 1
    for sub_face in sub_faces:
        # print("Comparing labeled face " + str(counter) + " '" + face[fields["face_id"]] + "' to face " + str(counter2) + " '" + sub_face[fields["face_id"]] + "'")
        query = '\n"' + face[fields["face_id"]] + '","' + sub_face[fields["face_id"]] + '"'
        query += ",1" if face[fields["path"]] == sub_face[fields["path"]] else ",0"
        query += "," + str(abs(face[fields["nbr_faces"]] - sub_face[fields["nbr_faces"]]))
        # query += ",1" if face[fields["mimetype"]] == sub_face[fields["mimetype"]] else ",0"
        query += "," + str(int(abs(face[fields["fileaccessdate"]] - sub_face[fields["fileaccessdate"]]).total_seconds()))
        query += "," + str(int(abs(face[fields["filemodifydate"]] - sub_face[fields["filemodifydate"]]).total_seconds()))
        query += "," + str(abs(face[fields["filesize"]] - sub_face[fields["filesize"]]))
        # query += ",1" if face[fields["filetype"]] == sub_face[fields["filetype"]] else ",0"
        # query += ",1" if face[fields["filetypeextension"]] == sub_face[fields["filetypeextension"]] else ",0"
        query += ",1" if face[fields["imageheight"]] == sub_face[fields["imageheight"]] else ",0"
        query += ",1" if face[fields["imagewidth"]] == sub_face[fields["imagewidth"]] else ",0"
        query += "," if face[fields["datetimeoriginal"]] == None or sub_face[fields["datetimeoriginal"]] == None else "," + str(int(abs(face[fields["datetimeoriginal"]] - sub_face[fields["datetimeoriginal"]]).total_seconds()))
        query += "," if face[fields["createdate"]] == None or sub_face[fields["createdate"]] == None else "," + str(int(abs(face[fields["createdate"]] - sub_face[fields["createdate"]]).total_seconds()))
        query += "," if face[fields["modifydate"]] == None or sub_face[fields["modifydate"]] == None else "," + str(int(abs(face[fields["modifydate"]] - sub_face[fields["modifydate"]]).total_seconds()))
        query += ",1" if face[fields["exifimageheight"]] == sub_face[fields["exifimageheight"]] else ",0"
        query += ",1" if face[fields["exifimagewidth"]] == sub_face[fields["exifimagewidth"]] else ",0"
        query += "," if face[fields["gpslongitude"]] == None or face[fields["gpslatitude"]] == None or sub_face[fields["gpslongitude"]] == None or sub_face[fields["gpslatitude"]] == None else "," + str(int(gpxpy.geo.haversine_distance(face[fields["gpslongitude"]], face[fields["gpslatitude"]], sub_face[fields["gpslongitude"]], sub_face[fields["gpslatitude"]])))
        query += "," if face[fields["gpsaltitude"]] == None or sub_face[fields["gpsaltitude"]] == None else "," + str(int(abs(face[fields["gpsaltitude"]] - sub_face[fields["gpsaltitude"]])))
        query += "," if face[fields["gpsimgdirection"]] == None or sub_face[fields["gpsimgdirection"]] == None else "," + str(int(abs(face[fields["gpsimgdirection"]] - sub_face[fields["gpsimgdirection"]]))) if int(abs(face[fields["gpsimgdirection"]] - sub_face[fields["gpsimgdirection"]])) < 180 else ", " + str(360 - int(abs(face[fields["gpsimgdirection"]] - sub_face[fields["gpsimgdirection"]])))
        query += "," if face[fields["gpslongituderef"]] == None or sub_face[fields["gpslongituderef"]] == None else ",1"  if face[fields["gpslongituderef"]] == sub_face[fields["gpslongituderef"]] else ",0"
        query += "," if face[fields["gpslatituderef"]] == None or sub_face[fields["gpslatituderef"]] == None else ",1"  if face[fields["gpslatituderef"]] == sub_face[fields["gpslatituderef"]] else ",0"
        query += "," if face[fields["gpsaltituderef"]] == None or sub_face[fields["gpsaltituderef"]] == None else ",1"  if face[fields["gpsaltituderef"]] == sub_face[fields["gpsaltituderef"]] else ",0"
        query += "," if face[fields["gpsimgdirectionref"]] == None or sub_face[fields["gpsimgdirectionref"]] == None else ",1"  if face[fields["gpsimgdirectionref"]] == sub_face[fields["gpsimgdirectionref"]] else ",0"
        query += "," if face[fields["orientation"]] == None or sub_face[fields["orientation"]] == None else ",1"  if face[fields["orientation"]] == sub_face[fields["orientation"]] else ",0"
        query += "," if face[fields["flash"]] == None or sub_face[fields["flash"]] == None else ",1"  if face[fields["flash"]] == sub_face[fields["flash"]] else ",0"
        query += "," if face[fields["make"]] == None or sub_face[fields["make"]] == None else ",1"  if face[fields["make"]] == sub_face[fields["make"]] else ",0"
        query += "," if face[fields["model"]] == None or sub_face[fields["model"]] == None else ",1"  if face[fields["model"]] == sub_face[fields["model"]] else ",0"
        face1 = np.fromstring(face[fields["description"]][1:-1], dtype=float, sep=" ")
        face2 = np.fromstring(sub_face[fields["description"]][1:-1], dtype=float, sep=" ")
        d = face1 - face2
        diff = np.dot(d, d)
        query += "," + str(diff)
        query += ",1" if face[fields["label"]] == sub_face[fields["label"]] else ",0"
        ################################################################################################
        f.write(query)
        ################################################################################################
        # cursor.execute(query)
        # counter2 += 1
        # if counter2 == 5: break
########################################################################################################
    f.close()
########################################################################################################
    counter += 1
    # if counter == 5: break
    cursor.execute("UPDATE faces SET treatedForHadoop = 1 WHERE face_id = '" + face[fields["face_id"]] + "'")
    connection.commit()
    print("Completed in " + str(round(time() - startTime, 1)) + " seconds")
    print("Cumulative execution time: " + str(int(time() - totalExecutionTime)) + " seconds")

cursor.close()
connection.commit()
connection.close()

# CREATE TABLE faces_neighbors (
# 	face1_id VARCHAR2(25) NOT NULL,
# 	face2_id VARCHAR2(25) NOT NULL,
# 	same_path NUMBER(1) DEFAULT 0 NOT NULL,
# 	diff_nbr_faces NUMBER(2) DEFAULT 0 NOT NULL,
# 	same_mimetype NUMBER(1) DEFAULT 0 NOT NULL,
# 	diff_fileaccessdate NUMBER(9) DEFAULT 0 NOT NULL,
# 	diff_filemodifydate NUMBER(9) DEFAULT 0 NOT NULL,
# 	diff_filesize NUMBER(8) DEFAULT 0 NOT NULL,
# 	same_filetype NUMBER(1) DEFAULT 0 NOT NULL,
# 	same_filetypeextension NUMBER(1) DEFAULT 0 NOT NULL,
# 	same_imageheight NUMBER(1) DEFAULT 0 NOT NULL,
# 	same_imagewidth NUMBER(1) DEFAULT 0 NOT NULL,
# 	diff_datetimeoriginal NUMBER(9) DEFAULT NULL,
# 	diff_createdate NUMBER(9) DEFAULT NULL,
# 	diff_modifydate NUMBER(9) DEFAULT NULL,
# 	same_exifimageheight NUMBER(1) DEFAULT 0 NOT NULL,
# 	same_exifimagewidth NUMBER(1) DEFAULT 0 NOT NULL,
#   distance NUMBER(8) DEFAULT NULL,
# 	diff_gpsaltitude NUMBER(8) DEFAULT NULL,
# 	diff_gpsimgdirection NUMBER(8) DEFAULT NULL,
# 	same_gpslongituderef NUMBER(1) DEFAULT NULL,
# 	same_gpslatituderef NUMBER(1) DEFAULT NULL,
# 	same_gpsaltituderef NUMBER(1) DEFAULT NULL,
# 	same_gpsimgdirectionref NUMBER(1) DEFAULT NULL,
# 	same_orientation NUMBER(1) DEFAULT NULL,
# 	same_flash NUMBER(1) DEFAULT NULL,
# 	same_make NUMBER(1) DEFAULT NULL,
# 	same_model NUMBER(1) DEFAULT NULL,
#   fr FLOAT NOT NULL,
#   neighbor NUMBER(1) DEFAULT 0 NOT NULL,
# 	CONSTRAINT faces_comp_pk PRIMARY KEY (face1_id, face2_id),
# 	CONSTRAINT face1_fk
#  		FOREIGN KEY (face1_id)
#  		REFERENCES faces(face_id)
# 		ON DELETE CASCADE,
# 	CONSTRAINT face2_fk
#  		FOREIGN KEY (face2_id)
#  		REFERENCES faces(face_id)
# 		ON DELETE CASCADE
# );