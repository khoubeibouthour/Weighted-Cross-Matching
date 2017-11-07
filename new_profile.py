"""
This script helps adding a new profile to the database without affecting any previous data related to faces or images.
Just pass the photo of the new profile as argument

"""

import cx_Oracle, sys, cv2
from os.path import isfile
from PIL import Image
import exiftool
import openface, dlib

extensions = {".jpg", ".JPG", ".jpeg"}
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
align = openface.AlignDlib("/home/cs0800/openface/models/dlib/shape_predictor_68_face_landmarks.dat")
net = openface.TorchNeuralNet("/home/cs0800/openface/models/openface/nn4.small2.v1.t7", 96)

connection = cx_Oracle.connect('python/python')
cursor = connection.cursor()

# Get user supplied values to build the files' list based on the given input
if len(sys.argv) == 1:
    print( "Must provide the photo of the new profile!")
elif isfile(sys.argv[1]):
    if any(sys.argv[1].endswith(ext) for ext in extensions):
        print("Analyzing file " + sys.argv[1] + " looking for a face")
        image = cv2.imread(sys.argv[1])
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
            print("No face detected")
        else:
            if len(output[0]) > 1:
                print("More than one face detected. Check the generated \"new_profile.jpg\" for details")
                for (x, y, w, h) in output[0]:
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 5)
                cv2.imwrite("new_profile.jpg", image)
                new_profile = "new_profile"
            else:
                print("processing new profile...")
                img = Image.open(sys.argv[1])
                with exiftool.ExifTool() as et:
                    metadata = et.get_metadata(sys.argv[1])
                    if "EXIF:Orientation" in metadata:
                        if metadata["EXIF:Orientation"] == 3:
                            img = img.rotate(180, expand=True)
                        elif metadata["EXIF:Orientation"] == 6:
                            img = img.rotate(270, expand=True)
                        elif metadata["EXIF:Orientation"] == 8:
                            img = img.rotate(90, expand=True)
                    (x, y, w, h) = output[0][0]
                    face = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
                    alignedFace = align.align(96, rgbImg, face, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
                    if alignedFace is None:
                        print("Failed to align face")
                        exit()
                    rep = net.forward(alignedFace)
                    if len(sys.argv) > 2:
                        new_profile = sys.argv[2]
                    else:
                        new_profile = raw_input("New profile name: ")
                    img.crop((face.left(), face.top(), face.right(), face.bottom())).save("./" + new_profile + "-face.jpg")
                    img.close()
                    cursor.execute("SELECT profile_id FROM profiles WHERE name = '" + new_profile + "'")
                    if cursor.fetchone() == None:
                        cursor.execute("INSERT INTO profiles(profile_id, name, description) VALUES ('" + str(hash(str(rep))) + "', '" + new_profile + "', '" + str(rep) + "')")
                        print("Profile '" + new_profile + "' successfully added!")
                    else:
                        cursor.execute("UPDATE profiles SET profile_id = '" + str(hash(str(rep))) + "', description = '" + str(rep) + "' WHERE name = '" + new_profile + "'")
                        print("Profile '" + new_profile + "' updated!")
                    cursor.close()
                    connection.commit()
                    connection.close()
            print("\nFace file is stored at ./" + new_profile + "-face.jpg")
            # img = Image.open("./" + new_profile + '.jpg')
            # img.show()
            # img.close()
    else:
        print("Must provide a valid photo")
else:
    print("Only photos are accepted")
