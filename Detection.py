#https://github.com/opencv/opencv/tree/master/data/haarcascades

import cv2, sys, Image, math, ImageDraw, time
from os import getcwd, walk, listdir, makedirs, unlink
from os.path import isdir, isfile, exists, join

start_time = time.time()
extensions = {".jpg", ".JPG", ".jpeg", ".png", ".gif"}
RenderedFolder = "Rendered"

def buildFilesList(currentDirectory):
	images = []
	for root, dirs, files in walk(currentDirectory):
		if root.rstrip().split('\\')[-1] == RenderedFolder: continue
		for name in files:
			if any(name.endswith(ext) for ext in extensions):
				images.append(join(root, name))
	return images

# Get user supplied values
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
		file_path = join(getcwd() + "\\" + RenderedFolder, file)
		if isfile(file_path): unlink(file_path)

# Create the haar cascade
# multiple cascades: https://github.com/Itseez/opencv/tree/master/data/haarcascades

#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#https://github.com/Itseez/opencv/blob/master/data/haarcascades/haarcascade_eye.xml
eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

#start analyzing image after another
corpusSize = len(corpus)
print "Total number of images: " + str(corpusSize)
print "\nGenerating the file descriptor"
counter = 0
countFilesAffected = 0
fileDescriptor = []
for imagePath in corpus:
	counter += 1
	print "Analyzing image " + str(counter) + " of " + str(corpusSize) + "...", '\r',
	
	# Read the image
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	#gray = cv2.equalizeHist(gray)
	
	# Detect faces in the image
	#faces = faceCascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, flags=cv2.CASCADE_SCALE_IMAGE, minSize=(30, 30), maxSize=(100,100))
	output = faceCascade.detectMultiScale3(
		gray,
		scaleFactor=1.3,
		minNeighbors=5,
		flags = cv2.CASCADE_SCALE_IMAGE,
		outputRejectLevels = True
	)
	faces = output[0]
	neighbours = output[1]
	weights = output[2]
	#numDetections, outputRejectLevels = True, rejectLevels = 0, levelWeights = 0
	#cv2.groupRectangles(faces, groupThreshold = 3)
	#Python: cv2.CascadeClassifier.detectMultiScale(image, rejectLevels, levelWeights[, scaleFactor[, minNeighbors[, flags[, minSize[, maxSize[, outputRejectLevels]]]]]])
	if len(faces) > 0:
		#print weights
		#print neighbours
		
		fileDescriptor.append(faces)
		countFilesAffected += 1
		
		# Draw a rectangle around the faces
		countFaces = 0
		for (x, y, w, h) in faces:
			countFaces += 1
			img =  Image.open(imagePath)
			img.crop((x, y, x + w, y + h)).save(RenderedFolder + "\\File-" + str(countFilesAffected) + "_Face-" + str(countFaces) + ".jpg")
			cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
			
			roi_gray = cv2.equalizeHist(gray[y:y+h, x:x+w])
			roi_color = image[y:y+h, x:x+w]
			eyes = eyeCascade.detectMultiScale(roi_gray)
			for (ex, ey, ew, eh) in eyes:
				cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 4)
			
			cv2.imwrite(RenderedFolder + "\\File-" + str(countFilesAffected) + ".jpg", image)
		#print "Found " + str(len(faces)) + " faces in file " + imagePath
	#cv2.imshow("Faces found", image)
	#cv2.waitKey(0)

cv2.destroyAllWindows()
print "Total execution time: " + str(round(time.time() - start_time)) + " seconds"
