import cv2
from os import walk, makedirs, listdir, getcwd, unlink, rmdir
from os.path import join, exists, isfile
from PIL import Image, ImageDraw								#To resize, crop and rotate images
from shutil import rmtree

extensions = {".jpg", ".JPG", ".jpeg"}
RenderedFolder = "Rendered"
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def preprocessingFoldersandFiles():
	if not exists(RenderedFolder):
		makedirs(RenderedFolder)
		#makedirs(RenderedFolder + "/Images")
		#makedirs(RenderedFolder + "/Faces")
	else:
		# if not exists(RenderedFolder + "/Images"):
		# 	makedirs(RenderedFolder + "/Images")
		# else:
		# 	for file in listdir(RenderedFolder + "/Images"):
		# 		file_path = join(getcwd() + "/" + RenderedFolder + "/Images", file)
		# 		if isfile(file_path): unlink(file_path)
		# if not exists(RenderedFolder + "/Faces"):
		# 	makedirs(RenderedFolder + "/Faces")
		# else:
		# 	for file in listdir(RenderedFolder + "/Faces"):
		# 		file_path = join(getcwd() + "/" + RenderedFolder + "/Faces", file)
		# 		if isfile(file_path): unlink(file_path)

		for d in listdir(RenderedFolder):
			content = join(getcwd() + "/" + RenderedFolder, d)
			if isfile(content):
				unlink(content)
			else:
				rmtree(content)

def registerFace(face, img, image, countFilesAffected, countFaces, imagePath, rep, cursor):
	try:
		tImg = img.crop((face.left(), face.top(), face.right(), face.bottom()))
	except:
		print "Failed to crop face from " + imagePath
		exit()
	newFile = RenderedFolder + imagePath[26:-len(imagePath.split(".")[-1]) - 1] + "[" + str(countFaces) + "].jpg"
	try:
		tImg.save(newFile)
	except:
		folders = imagePath[27:].split("/")
		folders = folders[0:-1]
		folder = RenderedFolder
		for d in folders:
			folder += "/" + d
			if not exists(folder): makedirs(folder)
		tImg.save(newFile)
	cv2.rectangle(image, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 5)
	query = "INSERT INTO faces (" \
		"face_id, " \
		"image, " \
		"left, " \
		"top, " \
		"right, " \
		"bottom, " \
		"filename, " \
		"description) VALUES (" \
		"'" + str(hash(imagePath + str(rep))) + "', " \
		"'" + str(hash(imagePath)) + "', " \
		+ str(face.left()) + ", " \
		+ str(face.top()) + ", " \
		+ str(face.right()) + ", " \
		+ str(face.bottom()) + ", " \
		"'" + newFile.split("/")[-1] + "', " \
		"'" + str(rep) + "')"
	try:
		cursor.execute(query)
	except:
		print query

# Creates the list of images to be treated
def buildFilesList(currentDirectory, cursor):
	roots = {}
	size = 0
	for root, dirs, files in walk(currentDirectory):
		if RenderedFolder in root.rstrip().split('/'): continue
		query = "SELECT completed FROM folders WHERE folder_id = '" + str(hash(root)) + "'"
		cursor.execute(query)
		folder = cursor.fetchone()
		if folder == None:
			query = "INSERT INTO folders (" \
				"folder_id, " \
				"path) VALUES (" \
				"'" + str(hash(root)) + "', " \
				"'" + root + "')"
			cursor.execute(query)
		else: continue
		images = []
		for name in files:
			if any(name.endswith(ext) for ext in extensions):
				images.append(name)
				size += 1
		roots[root] = images
	return roots, size

def getFacesFromImage(imagePath, counter, corpusSize):
	#print "\r" + counter + " of " + corpusSize + ": " + imagePath,

	# Read the image
	image = cv2.imread(imagePath)

	if image is None: return [], False, False

	#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	rgbImg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

	# faces = align.getAllFaceBoundingBoxes(rgbImg)

	#gray = cv2.equalizeHist(gray)

	# Detect faces in the image
	#faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3, flags=cv2.CASCADE_SCALE_IMAGE)
	output = faceCascade.detectMultiScale3(
		rgbImg,
		scaleFactor=1.3,
		minNeighbors=4,							# We tolerate false positive rather than false negative as they will be ignored
		flags = cv2.CASCADE_SCALE_IMAGE,		# in the recognition phase
		outputRejectLevels = True,
		minSize = (30, 30)
	)

	return output[0], rgbImg, image
	#return align.getAllFaceBoundingBoxes(rgbImg), rgbImg, image

def registerImage(imagePath, et, cursor, faces):
	fileID = hash(imagePath)
	metadata = et.get_metadata(imagePath)
	# "gpstimestamp, " \
	query = "INSERT INTO images (" \
			"image_id, " \
			"path_id, " \
			"path, " \
			"name, " \
			"nbr_faces, " \
			"mimetype, " \
			"fileaccessdate, " \
			"filemodifydate, " \
			"filesize, " \
			"filetype, " \
			"filetypeextension, " \
			"imageheight, " \
			"imagewidth, " \
			"datetimeoriginal, " \
			"createdate, " \
			"modifydate, " \
			"exifimageheight, " \
			"exifimagewidth, " \
			"gpslongitude, " \
			"gpslatitude, " \
			"gpsaltitude, " \
			"gpsimgdirection, " \
			"gpslongituderef, " \
			"gpslatituderef, " \
			"gpsaltituderef, " \
			"gpsimgdirectionref, " \
			"orientation, " \
			"flash, " \
			"make, " \
			"model) VALUES (" \
			"'" + str(fileID) + "', " \
			"'" + str(hash(metadata["File:Directory"])) + "', " \
			"'" + metadata["File:Directory"] + "', " \
			"'" + metadata["File:FileName"] + "', " \
			+ faces + ", " \
			"'" + metadata["File:MIMEType"] + "', " \
			"to_date('" + metadata["File:FileAccessDate"].split('-')[0] + "', 'yyyy:mm:dd hh24:mi:ss'), " \
			"to_date('" + metadata["File:FileModifyDate"].split('-')[0] + "', 'yyyy:mm:dd hh24:mi:ss'), " \
			+ str(metadata["File:FileSize"]) + ", " \
			"'" + metadata["File:FileType"] + "', " \
			"'" + metadata["File:FileTypeExtension"] + "', " \
			+ str(metadata["File:ImageHeight"]) + ", " \
			+ str(metadata["File:ImageWidth"]) + ", " \
			+ ("to_date('" + metadata["EXIF:DateTimeOriginal"] + "', 'yyyy:mm:dd hh24:mi:ss')" if "EXIF:DateTimeOriginal" in metadata else "NULL") + ", " \
			+ ("to_date('" + metadata["EXIF:CreateDate"] + "', 'yyyy:mm:dd hh24:mi:ss')" if "EXIF:CreateDate" in metadata else "NULL") + ", " \
			+ ("to_date('" + metadata["EXIF:ModifyDate"] + "', 'yyyy:mm:dd hh24:mi:ss')" if "EXIF:ModifyDate" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:ExifImageHeight"]) if "EXIF:ExifImageHeight" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:ExifImageWidth"]) if "EXIF:ExifImageWidth" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:GPSLongitude"]) if "EXIF:GPSLongitude" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:GPSLatitude"]) if "EXIF:GPSLatitude" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:GPSAltitude"]) if "EXIF:GPSAltitude" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:GPSImgDirection"]) if "EXIF:GPSImgDirection" in metadata else "NULL") + ", " \
			+ ("'" + metadata["EXIF:GPSLongitudeRef"] + "'" if "EXIF:GPSLongitudeRef" in metadata else "NULL") + ", " \
			+ ("'" + metadata["EXIF:GPSLatitudeRef"] + "'" if "EXIF:GPSLatitudeRef" in metadata else "NULL") + ", " \
			+ ("'" + str(metadata["EXIF:GPSAltitudeRef"]) + "'" if "EXIF:GPSAltitudeRef" in metadata else "NULL") + ", " \
			+ ("'" + metadata["EXIF:GPSImgDirectionRef"] + "'" if "EXIF:GPSImgDirectionRef" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:Orientation"]) if "EXIF:Orientation" in metadata else "NULL") + ", " \
			+ (str(metadata["EXIF:Flash"]) if "EXIF:Flash" in metadata else "NULL") + ", " \
			+ ("'" + metadata["EXIF:Make"] + "'" if "EXIF:Make" in metadata else "NULL") + ", " \
			+ ("'" + metadata["EXIF:Model"] + "'" if "EXIF:Model" in metadata else "NULL") + ")"
			# + ("to_date('" + metadata["EXIF:GPSTimeStamp"].split(".")[0] + "', 'hh24:mi:ss')" if "EXIF:GPSTimeStamp" in metadata else "NULL") + ", " \
	try:
		cursor.execute(query)
	except(RuntimeError, TypeError, NameError):
		print query
		print RuntimeError + " :: " + TypeError + " :: " + NameError
	img = Image.open(imagePath)
	if "EXIF:Orientation" in metadata:
		if metadata["EXIF:Orientation"] == 3:
			img = img.rotate(180, expand=True)
		elif metadata["EXIF:Orientation"] == 6:
			img = img.rotate(270, expand=True)
		elif metadata["EXIF:Orientation"] == 8:
			img = img.rotate(90, expand=True)
	return img