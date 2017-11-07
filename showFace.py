import cx_Oracle
from PIL import Image, ImageDraw
import exiftool

connection = cx_Oracle.connect('python/python@127.0.0.1/xe')
cursor = connection.cursor()

cursor.execute("SELECT path, name, left, top, right, bottom, label FROM faces, images WHERE image_id = image AND face_id = '" + str(input("Face ID: ")) + "'")

image =cursor.fetchone()
if image == None:
    print("Face not found!")
    exit()

imagePath = 'E:/private/Images' + image[0][26:] + "/" + image[1]
img = Image.open(imagePath)

with exiftool.ExifTool() as et:
    metadata = et.get_metadata(imagePath)
    if "EXIF:Orientation" in metadata:
        if metadata["EXIF:Orientation"] == 3:
            img = img.rotate(180, expand=True)
        elif metadata["EXIF:Orientation"] == 6:
            img = img.rotate(270, expand=True)
        elif metadata["EXIF:Orientation"] == 8:
            img = img.rotate(90, expand=True)

draw = ImageDraw.Draw(img)
for i in range(0, 10):
    draw.rectangle(((image[2] - i, image[3] - i), (image[4] + i, image[5] + i)), fill=None, outline="yellow")
draw.text((20, 70), image[6])
img.show()
img.close()