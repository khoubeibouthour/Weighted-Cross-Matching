# https://github.com/opencv/opencv/tree/master/data/haarcascades

import sys, math, time
from os import getcwd  # To browse File system
from os.path import isdir, exists  # To check files
import exiftool  # To retrieve files' metadata
import openface, dlib
import cx_Oracle
from toolz import *

global_start_time = time.time()
# preprocessingFoldersandFiles()

connection = cx_Oracle.connect('python/python')
cursor = connection.cursor()
cursor.execute("DELETE FROM folders WHERE completed = 0")

# Get user supplied values to build the files' list based on the given input
if len(sys.argv) == 1:
    print("Analyzing the current directory for images: \"" + getcwd() + "\"")
    corpus, corpusSize = buildFilesList(getcwd(), cursor)
elif isdir(sys.argv[1]):
    print("Only 1 folder to be analyzed: \"" + sys.argv[1] + "\"")
    corpus, corpusSize = buildFilesList(sys.argv[1], cursor)
elif exists(sys.argv[1]):
    if any(sys.argv[1].endswith(ext) for ext in extensions):
        print("Only 1 file to be analyzed: \"" + sys.argv[1] + "\"")
        corpus, corpusSize = {sys.argv[1]: sys.argv[1]}, 1
    else:
        print("The file's format is not supported.")
        print("Only files which extensions listed below are supported")
        print(extensions)
        exit()
else:
    print("Check your parameter: " + sys.argv[1])
    print("Your parameter must be:")
    print("\t- Blank: treats the current folder + all subdirectories")
    print("\t- A folder: Analyzes all the files in it")
    print("\t- A file: Only analyzes the given file")
    exit()
# Create the haar cascade
# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades


# https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
# eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# start analyzing image after another
counter = 0
countFilesAffected = 0
totalFaces = 0
progress = 0

# cursor.execute("TRUNCATE TABLE faces")
# cursor.execute("TRUNCATE TABLE images")

connection.commit()

align = openface.AlignDlib("/home/cs0800/openface/models/dlib/shape_predictor_68_face_landmarks.dat")
net = openface.TorchNeuralNet("/home/cs0800/openface/models/openface/nn4.small2.v1.t7", 96)
with exiftool.ExifTool() as et:
    for folder, images in corpus.iteritems():
        print "Analyzed: " + str(progress) + "/" + str(corpusSize)
        progress += len(images)
        print "[" + str(len(images)) + " images] in " + folder
        for imagePath in images:
            counter += 1
            faces, rgbImg, image = getFacesFromImage(join(folder, imagePath), str(counter), str(corpusSize))

            # Add entry to the file descriptor if there is any face detected:
            if len(faces) > 0:
                img = registerImage(join(folder, imagePath), et, cursor, str(len(faces)))

                countFilesAffected += 1

                countFaces = 0

                # for face in faces:
                for (x, y, w, h) in faces:
                    face = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
                    alignedFace = align.align(96, rgbImg, face, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
                    if alignedFace is None:
                        continue
                    # raise Exception("Unable to align image: {}".format(imagePath))
                    countFaces += 1
                    totalFaces += 1
                    rep = net.forward(alignedFace)

                    registerFace(face, img, image, countFilesAffected, countFaces, join(folder, imagePath), rep, cursor)

                img.close()
                cv2.imwrite(RenderedFolder + join(folder[26:], imagePath), image)
            # if counter > 100:
            # 	cursor.close()
            # 	connection.commit()
            # 	connection.close()
            # 	exit()
        query = "UPDATE folders SET completed = 1 WHERE folder_id = '" + str(hash(folder)) + "'"
        cursor.execute(query)
        connection.commit()
    # print "Analysis completed in " + str(round(time.time() - start_time))

cursor.close()
connection.commit()
connection.close()

print "\n\nTotal execution time: " + str(round(time.time() - global_start_time)) + " seconds"
print "\nTotal images affected: " + str(countFilesAffected)
print "\nTotal faces found: " + str(totalFaces)
