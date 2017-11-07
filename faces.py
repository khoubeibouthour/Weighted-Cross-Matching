import time
import cx_Oracle
import pyexifinfo #exiftool
from PIL import Image, ImageDraw
from os.path import exists
from os import makedirs
import pyexifinfo as p

p.ver() #retrieve your ExifTool version
filename = 'Astraat.jpg'
print(p.get_json(filename)) #retrieve a json representation of this file exif
exit()
global_start_time = time.time()

counter = 0
imagePath = ""
path = ""

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()

cursor.execute("SELECT face_id, path, name, left, top, right, bottom, filetypeextension FROM faces, images WHERE image_id = image ORDER BY path, name")

with pyexifinfo.ExifTool() as et:
    # metadata = et.get_metadata(imagePath)
    faces = cursor.fetchall()
    corpusSize = str(cursor.rowcount)
    for face in faces:
        if path != face[1]:
            path = face[1]
            if not exists("Rendered/" + path[27:]):
                makedirs("Rendered/" + path[27:])
        if imagePath != face[1] + "/" + face[2]:
            imagePath = face[1] + "/" + face[2]
            img = Image.open(imagePath)
            metadata = et.get_metadata(imagePath)
            if "EXIF:Orientation" in metadata:
                if metadata["EXIF:Orientation"] == 3:
                    img = img.rotate(180, expand=True)
                elif metadata["EXIF:Orientation"] == 6:
                    img = img.rotate(270, expand=True)
                elif metadata["EXIF:Orientation"] == 8:
                    img = img.rotate(90, expand=True)
        counter += 1
        print("\r" + str(counter) + " of " + corpusSize + ": " + imagePath + "                                                     ",)
        img.crop((face[3], face[4], face[5], face[6])).save("Rendered/" + path[27:] + "/" + face[0] + "." + face[7])

cursor.close()
connection.close()

print("\n\nTotal execution time: " + str(round(time.time() - global_start_time)) + " seconds")
