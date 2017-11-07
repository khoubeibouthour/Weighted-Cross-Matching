import cx_Oracle
import numpy as np
import gpxpy.geo
from os.path import isfile

frThreshold = 1.13
lowerCI     = .6
upperCI     = 1.6

fields = {
    "face_id":          0,
    "face_recog":       1,
    "description":      2,
    "label":            3,
    "path":             4,
    "nbr_faces":        5,
    "filesize":         6,
    "imagewidth":       7,
    "datetimeoriginal": 8,
    "gpslongitude":     9,
    "gpslatitude":      10,
    "gpsaltitude":      11,
    "gpsimgdirection":  12,
    "orientation":      13,
    "model":            14
}

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()

def generateComparisons(profile, profileName):
    query = "SELECT comparisons.face, comparisons.face_recog, faces.description, comparisons.label, " \
            "images.path, " \
            "images.nbr_faces, " \
            "images.filesize, " \
            "images.imagewidth, " \
            "images.datetimeoriginal, " \
            "images.gpslongitude, " \
            "images.gpslatitude, " \
            "images.gpsaltitude, " \
            "images.gpsimgdirection, " \
            "images.orientation, " \
            "images.model FROM faces, images, comparisons WHERE " \
            "comparisons.profile = '" + profile + "' " \
            "AND comparisons.face_recog <= " + str(upperCI) + " " \
            "AND comparisons.face_recog > " + str(lowerCI) + " " \
            "AND comparisons.face = faces.face_id " \
            "AND faces.image = images.image_id"
    cursor.execute(query)
    candidates = cursor.fetchall()
    toBeTreated = str(len(candidates))

    query = "SELECT comparisons.face, comparisons.face_recog, faces.description, comparisons.label, " \
            "images.path, " \
            "images.nbr_faces, " \
            "images.filesize, " \
            "images.imagewidth, " \
            "images.datetimeoriginal, " \
            "images.gpslongitude, " \
            "images.gpslatitude, " \
            "images.gpsaltitude, " \
            "images.gpsimgdirection, " \
            "images.orientation, " \
            "images.model FROM faces, images, comparisons WHERE " \
            "comparisons.profile = '" + profile + "' " \
            "AND ((comparisons.face_recog <= " + str(lowerCI) + ") " \
            "OR (comparisons.face_recog > " + str(upperCI) + ")) " \
            "AND comparisons.face = faces.face_id " \
            "AND faces.image = images.image_id"
    cursor.execute(query)
    references = cursor.fetchall()
    counter = 0
    for candidate in candidates:
        wasCreated = False # if some comparisons exist, then the file will be created, otherwise pass
        counter += 1
        filename = "C:/dataset/" + profileName + "/" + str(profile) + "_" + str(candidate[fields["face_id"]]) + ".txt"
        if isfile(filename):
            print "\r" + str(counter) + "/" + toBeTreated + " skipped",
            continue

        face1 = np.fromstring(candidate[fields["description"]][1:-1], dtype=float, sep=" ")
        for reference in references:
            face2 = np.fromstring(reference[fields["description"]][1:-1], dtype=float, sep=" ")
            d = face1 - face2
            d = np.dot(d, d)
            if lowerCI < d <= upperCI: continue
            if d > upperCI and reference[fields["face_recog"]] > upperCI: continue
            if not wasCreated:
                wasCreated = True
                f = open(filename, "w+")
                f.write('fr_direct,fr_comp,fr_ref,same_path,diff_nbr_faces,diff_filesize,same_imagewidth,diff_datetimeoriginal,distance,diff_gpsaltitude,same_orientation,same_model,response')
            query = '\n' + str(candidate[fields["face_recog"]]) + ','
            query += str(d) + ',' + str(reference[fields["face_recog"]])
            query += ',1' if candidate[fields["path"]] == reference[fields["path"]] else ',0'
            query += ',' + str(abs(candidate[fields["nbr_faces"]] - reference[fields["nbr_faces"]]))
            query += ',' + str(abs(candidate[fields["filesize"]] - reference[fields["filesize"]]))
            query += ',1' if candidate[fields["imagewidth"]] == reference[fields["imagewidth"]] else ',0'
            query += ',' if candidate[fields["datetimeoriginal"]] == None or reference[fields["datetimeoriginal"]] == None else ',' + str(int(abs(candidate[fields["datetimeoriginal"]] - reference[fields["datetimeoriginal"]]).total_seconds()))
            query += ',' if candidate[fields["gpslongitude"]] == None or reference[fields["gpslatitude"]] == None or candidate[fields["gpslongitude"]] == None or reference[fields["gpslatitude"]] == None else ',' + str(int(gpxpy.geo.haversine_distance(candidate[fields["gpslongitude"]], reference[fields["gpslatitude"]], candidate[fields["gpslongitude"]], reference[fields["gpslatitude"]])))
            query += ',' if candidate[fields["gpsaltitude"]] == None or reference[fields["gpsaltitude"]] == None else ',' + str(int(abs(candidate[fields["gpsaltitude"]] - reference[fields["gpsaltitude"]])))
            query += ',' if candidate[fields["orientation"]] == None or reference[fields["orientation"]] == None else ',1' if candidate[fields["orientation"]] == reference[fields["orientation"]] else ',0'
            query += ',' if candidate[fields["model"]] == None or reference[fields["model"]] == None else ',1' if candidate[fields["model"]] == reference[fields["model"]] else ',0'
            query += ',' + str(candidate[fields["label"]])
            f.write(query)
        if wasCreated: f.close()
        print "\r" + str(counter) + "/" + toBeTreated + " faces treated",


cursor.execute("SELECT profile_id, name FROM profiles ORDER BY name")
# completed = ["Abrha", "Astraat", "Bonji", "Heeda", "Hickam", "Hmouda", "Holu", "Khufu", "Laghbesh", "Mekah", "Mimyth", "Sakis", "Sierra", "Sokhoi", "Yakouza"]
completed = []
profiles = cursor.fetchall()
for profile in profiles:
    print "\n=================================================================================\n"
    if profile[1] in completed:
        print "Profile", profile[1], "skipped"
        continue
    print "Genearting pairwise comparisons for", profile[1]
    generateComparisons(profile[0], profile[1])

cursor.close()
connection.close()