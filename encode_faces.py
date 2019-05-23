# USAGE
# python encode_faces.py --dataset dataset --encodings encodings.pickle

# import the necessary packages
from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
# construct the argument parser and parse the arguments
 
def encode_faces():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--dataset", required=True,
    	help="path to input directory of faces + images")
    ap.add_argument("-e", "--encodings", required=True,
    	help="path to serialized db of facial encodings")
    ap.add_argument("-d", "--detection-method", type=str, default="cnn",
    	help="face detection model to use: either `hog` or `cnn`")
    args = vars(ap.parse_args())
    
    # grab the paths to the input images in our dataset
    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images(args["dataset"]))
    
    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []
    print("hello")
    
    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        
    #    print("Doing image:",i)
    	# extract the person name from the image path
    	print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
    	name = imagePath.split(os.path.sep)[-2]
    
    	# load the input image and convert it from RGB (OpenCV ordering)
    	# to dlib ordering (RGB)
    	image = cv2.imread(imagePath)
    	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    	# detect the (x, y)-coordinates of the bounding boxes
    	# corresponding to each face in the input image
    	boxes = face_recognition.face_locations(rgb,model=args["detection_method"])
    
    	# compute the facial embedding for the face
    	encodings = face_recognition.face_encodings(rgb, boxes)
    
    	# loop over the encodings
    	for encoding in encodings:
    		# add each encoding + name to our set of known names and
    		# encodings
            
    		knownEncodings.append(encoding)
    		knownNames.append(name)
            
    data = {"encodings":knownEncodings, "names":knownNames}
    file = args["encodings"]
    
    if os.path.exists(file):
        print("Inside of the existing file")
        exfile = open(file, 'rb')
        record = pickle.load(exfile, encoding='latin1')
        exfile_encodings = record['encodings']
        exfile_name = record['names']
        exfile.close()
        exvfile = open(file, 'wb')
        exvfile_encodings =[]
        exvfile_name = []
        for enck in knownEncodings:
            exvfile_encodings.append(enck)
        for encx in exfile_encodings:
            exvfile_encodings.append(encx)
        
        for namek in knownNames:
            exvfile_name.append(namek)
        for namex in exfile_name:
            exvfile_name.append(namex)
        new_data = {"encodings": exvfile_encodings, "names": exvfile_name}
        print("New Encoding:",len(exvfile_encodings))
        print("New Names:",len(exvfile_name))
        data = pickle.dump(new_data, exvfile)
        exvfile.close()
    else:
        f= open(file,'wb')
        print("Inside other reaing pickle fuction")
        datas = pickle.dump(data, f)
        f.close()

encode_faces()

