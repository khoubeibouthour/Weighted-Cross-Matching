# https://github.com/opencv/opencv/tree/master/data/haarcascades

import cv2, sys, math, time										#OpenCV Library
from PIL import Image, ImageDraw								#To resize, crop and rotate images
from os import getcwd, walk, listdir, makedirs, unlink			#To browse File system
from os.path import isdir, isfile, exists, join					#To check files
import exiftool  												#To retrieve files' metadata
import json
from time import strftime, localtime
import openface, dlib

start_time = time.time()
extensions = {".jpg", ".JPG", ".jpeg", ".png", ".gif"}
RenderedFolder = "Rendered"


# Creates the list of images to be treated
def buildFilesList(currentDirectory):
	images = []
	for root, dirs, files in walk(currentDirectory):
		if root.rstrip().split('/')[-1] == RenderedFolder: continue
		for name in files:
			if any(name.endswith(ext) for ext in extensions):
				images.append(join(root, name))
	return images

# Get user supplied values to build the files' list based on the given input
if len(sys.argv) == 1:
	print "Analyzing the current directory for images: \"" + getcwd() + "\""
	corpus = buildFilesList(getcwd())
elif isdir(sys.argv[1]):
	print "Only 1 folder to be analyzed: \"" + sys.argv[1] + "\""
	corpus = buildFilesList(sys.argv[1])
elif exists(sys.argv[1]):
	if any(sys.argv[1].endswith(ext) for ext in extensions):
		print "Only 1 file to be analyzed: \"" + sys.argv[1] + "\""
		corpus = [sys.argv[1]]
	else:
		print "The file's format is not supported."
		print "Only files which extensions listed below are supported"
		print extensions
		exit()
else:
	print "Check your parameter: " + sys.argv[1]
	print "Your parameter must be:"
	print "\t- Blank: treats the current folder + all subdirectories"
	print "\t- A folder: Analyzes all the files in it"
	print "\t- A file: Only analyzes the given file"
	exit()


if not exists(RenderedFolder):
	makedirs(RenderedFolder)
else:
	for file in listdir(RenderedFolder):
		file_path = join(getcwd() + "/" + RenderedFolder, file)
		if isfile(file_path): unlink(file_path)

# Create the haar cascade
# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
#faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
#eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

#start analyzing image after another
corpusSize = len(corpus)
print "Total number of images: " + str(corpusSize)
print "\nGenerating the file descriptor"
counter = 0
countFilesAffected = 0
fileDescriptor = []
with exiftool.ExifTool() as et:
	for imagePath in corpus:
		counter += 1
		print "Analyzing image " + str(counter) + " of " + str(corpusSize) + "..."

		# Read the image
		image = cv2.imread(imagePath)

		#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		rgbImg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

		align = openface.AlignDlib("/home/cs0800/openface/models/dlib/shape_predictor_68_face_landmarks.dat")
		net = openface.TorchNeuralNet("/home/cs0800/openface/models/openface/nn4.small2.v1.t7", 96)
		faces = align.getAllFaceBoundingBoxes(rgbImg)
		#gray = cv2.equalizeHist(gray)

		# Detect faces in the image
		#faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3, flags=cv2.CASCADE_SCALE_IMAGE)
		'''
		output = faceCascade.detectMultiScale3(
			gray,
			scaleFactor=1.3,
			minNeighbors=4,							# We tolerate false positive rather than false negative as they will be ignored
			flags = cv2.CASCADE_SCALE_IMAGE,		# in the recognition phase
			outputRejectLevels = True
		)
		faces = output[0]
		'''
		# Add entry to the file descriptor if there is any face detected:
		if len(faces) > 0:
			Entry = "\t{\n" + \
	"\t\t\"File\": \"" + imagePath + "\",\n" + \
	"\t\t\"NbrFaces\": \"" + str(len(faces)) + "\",\n" + \
	"\t\t\"Identified\": \"0\",\n" + \
	"\t\t\"EntryDate\": \"" + strftime("%Y:%m:%d %H:%M:%S", localtime()) + "\",\n" + \
	"\t\t\"LastUpdate\": \"" + strftime("%Y:%m:%d %H:%M:%S", localtime()) + "\",\n"
			metadata = et.get_metadata(imagePath)
			Entry += "\t\t\"Metadata\": {\n" + \
		"\t\t\t\"File\": {\n" + \
			"\t\t\t\t\"MIMEType\": \"" + metadata["File:MIMEType"] + "\",\n" + \
			"\t\t\t\t\"FileAccessDate\": \"" + metadata["File:FileAccessDate"] + "\",\n" + \
			"\t\t\t\t\"FileModifyDate\": \"" + metadata["File:FileModifyDate"] + "\",\n" + \
			"\t\t\t\t\"FileSize\": \"" + str(metadata["File:FileSize"]) + "\",\n" + \
			"\t\t\t\t\"FileType\": \"" + metadata["File:FileType"] + "\",\n" + \
			"\t\t\t\t\"FileName\": \"" + metadata["File:FileName"] + "\",\n" + \
			"\t\t\t\t\"FileTypeExtension\": \"" + metadata["File:FileTypeExtension"] + "\",\n" + \
			"\t\t\t\t\"Directory\": \"" + metadata["File:Directory"] + "\",\n" + \
			"\t\t\t\t\"ImageHeight\": \"" + str(metadata["File:ImageHeight"]) + "\",\n" + \
			"\t\t\t\t\"ImageWidth\": \"" + str(metadata["File:ImageWidth"]) + "\"\n" + \
		"\t\t\t},\n" + \
		"\t\t\t\"EXIF\": {\n" + \
			"\t\t\t\t\"DateTimeOriginal\": \"" + (metadata["EXIF:DateTimeOriginal"] if "EXIF:DateTimeOriginal" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"CreateDate\": \"" + (metadata["EXIF:CreateDate"] if "EXIF:CreateDate" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"ModifyDate\": \"" + (metadata["EXIF:ModifyDate"] if "EXIF:ModifyDate" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"ExifImageHeight\": \"" + (str(metadata["EXIF:ExifImageHeight"]) if "EXIF:ExifImageHeight" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"ExifImageWidth\": \"" + (str(metadata["EXIF:ExifImageWidth"]) if "EXIF:ExifImageWidth" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSLongitude\": \"" + (str(metadata["EXIF:GPSLongitude"]) if "EXIF:GPSLongitude" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSLatitude\": \"" + (str(metadata["EXIF:GPSLatitude"]) if "EXIF:GPSLatitude" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSAltitude\": \"" + (str(metadata["EXIF:GPSAltitude"]) if "EXIF:GPSAltitude" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSImgDirection\": \"" + (str(metadata["EXIF:GPSImgDirection"]) if "EXIF:GPSImgDirection" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSLongitudeRef\": \"" + (metadata["EXIF:GPSLongitudeRef"] if "EXIF:GPSLongitudeRef" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSLatitudeRef\": \"" + (str(metadata["EXIF:GPSLatitudeRef"]) if "EXIF:GPSLatitudeRef" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSAltitudeRef\": \"" + (str(metadata["EXIF:GPSAltitudeRef"]) if "EXIF:GPSAltitudeRef" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSImgDirectionRef\": \"" + (str(metadata["EXIF:GPSImgDirectionRef"]) if "EXIF:GPSImgDirectionRef" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSTimeStamp\": \"" + (metadata["EXIF:GPSTimeStamp"] if "EXIF:GPSTimeStamp" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"Orientation\": \"" + (str(metadata["EXIF:Orientation"]) if "EXIF:Orientation" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"Flash\": \"" + (str(metadata["EXIF:Flash"]) if "EXIF:Flash" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"Make\": \"" + (str(metadata["EXIF:Make"]) if "EXIF:Make" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"Make\": \"" + (str(metadata["EXIF:Make"]) if "EXIF:Make" in metadata else "N/A") + "\"\n" + \
		"\t\t\t},\n" + \
		"\t\t\t\"Composite\": {\n" + \
			"\t\t\t\t\"GPSLongitude\": \"" + (str(metadata["Composite:GPSLongitude"]) if "Composite:GPSLongitude" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSLatitude\": \"" + (str(metadata["Composite:GPSLatitude"]) if "Composite:GPSLatitude" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSAltitude\": \"" + (str(metadata["Composite:GPSAltitude"]) if "Composite:GPSAltitude" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"GPSPosition\": \"" + (str(metadata["Composite:GPSPosition"]) if "Composite:GPSPosition" in metadata else "N/A") + "\",\n" + \
			"\t\t\t\t\"Megapixels\": \"" + str(metadata["Composite:Megapixels"]) + "\",\n" + \
			"\t\t\t\t\"ImageSize\": \"" + str(metadata["Composite:ImageSize"]) + "\"\n" + \
		"\t\t\t}\n" + \
	"\t\t},\n" + \
	"\t\t\"Faces\": ["
			countFilesAffected += 1

			# Draw a rectangle around the faces
			countFaces = 0

			img =  Image.open(imagePath)
			if metadata["EXIF:Orientation"] == 3:
				img = img.rotate(180, expand=True)
			elif metadata["EXIF:Orientation"] == 6:
				img = img.rotate(270, expand=True)
			elif metadata["EXIF:Orientation"] == 8:
				img = img.rotate(90, expand=True)
			for face in faces:
				Entry += "\n\t\t\t{\n" + \
				"\t\t\t\t\"Identified: \"NO\",\n" + \
				"\t\t\t\t\"PersonID\": \"N/A\",\n" + \
				"\t\t\t\t\"LocationOnImage\": [(" + str(face.left()) + ", " + str(face.top()) + "), (" + str(face.right()) + ", " + str(face.bottom()) + ")],\n"

				countFaces += 1
				img.crop((face.left(), face.top(), face.right(), face.bottom())).save(RenderedFolder + "/File-" + str(countFilesAffected) + "_Face-" + str(countFaces) + ".jpg")
				cv2.rectangle(image, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 10)

				alignedFace = align.align(96, rgbImg, face, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
				if alignedFace is None:
					raise Exception("Unable to align image: {}".format(imagePath))
				rep = net.forward(alignedFace)
				Entry += "\t\t\t\t\"Description\": \"" + str(rep) + "\"\n" + \
				"\t\t\t},"
			img.close()
			cv2.imwrite(RenderedFolder + "/File-" + str(countFilesAffected) + ".jpg", image)

			Entry = Entry[:-1]
			Entry += "\n\t\t]\n" + \
"\t},\n"
			fileDescriptor.append(Entry)

fileDescriptor[-1] = fileDescriptor[-1][:-2]
f = open("FileDescriptor.json", 'w')
f.write("{\n\t\"CreationDate\": \"" + strftime("%Y:%m:%d %H:%M:%S", localtime()) + "\",\n\t\"RootFolder\": \"" + getcwd() + "\",\n" + \
		"\t\"FilesNumber\": \"" + str(len(fileDescriptor)) + "\",\n")
for entry in fileDescriptor:
	f.write(entry)
f.write("\n}")
f.close
#cv2.destroyAllWindows()
print "Total execution time: " + str(round(time.time() - start_time)) + " seconds"
