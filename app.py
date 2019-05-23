# -*- coding: utf-8 -*-
"""
Created on Thu May 16 15:20:12 2019

@author: Chanabasagoudap
"""
import pickle
from werkzeug import secure_filename
import face_recognition
from flask import Flask
from flask import request
from flask import jsonify 
import base64
import os ,json
from flask import send_from_directory
import sqlite3
from sqlite3 import Error
from imutils import paths
import face_recognition
import pickle
import regex as re
import cv2
import imutils
import requests
from datetime import datetime, date
import random

ALLOWED_EXTENSIONS = set(['mkv', 'avi', 'mp4'])
videos = 'videos/'
application = app = Flask(__name__)
app.config['videos'] = videos

db_file = 'facerecognition.db'

""" 
 ############################################ Start of Database part############################################
 
"""
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)



def create_table(conn, sql_query):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_query)
        c.close()
    except Error as e:
        print(e)
        



def database():
    # 2.0 update 
    # added UserType column  and made some column as form NotNull
    print("Inside of def_database function")
    users_table = """ CREATE TABLE IF NOT EXISTS users_table (
                                        TransID integer PRIMARY KEY AUTOINCREMENT,
                                        MemberID text,
                                        FirstName text NOT NULL,
                                        LastName text NOT NULL,
                                        Email text,
                                        MobileNumber text,
                                        Department text,
                                        imagebase_enc text NOT NULL,
                                        UserType integer NOT NULL,
                                        Savedto text NOT NULL,
                                        RegDate Date
                                       ); """
 
    video_path = """CREATE TABLE IF NOT EXISTS video_path (
                                    VidID integer PRIMARY KEY AUTOINCREMENT,
                                    name text NOT NULL,
                                    input_path text NOT NULL,
                                    output_path text NOT NULL
                                   );""" 
    
    auth_stat = """CREATE TABLE IF NOT EXISTS auth_stat(
                                        StatID integer PRIMARY KEY AUTOINCREMENT,
                                        MemberID text NOT NULL,
                                        name text NOT NULL,
                                        UserType integer NOT NULL,
                                        AuthDate text NOT NULL
                                        );"""
    
    video_stat = """CREATE TABLE IF NOT EXISTS video_stat(
                                            userTrackID integer PRIMARY KEY AUTOINCREMENT,
                                            imagebase text NOT NULL,
                                            name text NOT NULL,
                                            Date Date NOT NULL,
                                            Time text NOT NULL,
                                            Location text NOT NULL,
                                            videolink text NOT NULL
                                        );"""

    real_time_stat = """CREATE TABLE IF NOT EXISTS real_time_stat(
                                            RealTimeID integer PRIMARY KEY AUTOINCREMENT,
                                            BuildingNum text NOT NULL,
                                            fllor text NOT NULL,
                                            Lab text NOT NULL,
                                            CoffeeRoom text NOT NULL,
                                            FitnessCenter text NOT NULL,
                                            Pool text NOT NULL,
                                            realDateTime Date
                                            );"""
    
    conn = create_connection(db_file)
    if conn is not None:
        # create users table
        create_table(conn, users_table)
        create_table(conn, video_path)
        create_table(conn, auth_stat)
        create_table(conn, video_stat)
        create_table(conn, real_time_stat)
        
        # create tasks table
#        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")
        
    conn.close()
    print("End of def_database function")
# Inserting the data to tabel
def insert_user_data(data):
    print("Start of the insert_user_data function")    
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    dates = date.today()
    dates = dates.strftime("%m/%d/%Y")
    t = datetime.now()
    times = "%d:%d:%d" % (t.hour,t.minute,t.second)
    c.execute("INSERT INTO users_table VALUES(?,?,?,?,?,?,?,?,?,?,datetime())", (None,data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],data[8]))
    conn.commit()
    if c.lastrowid:
        conn.close()
        print("End of the insert_user_data function")
        return jsonify({'status' : 'success', 'message' : "User Registration Successfull!!!"})
    else:
        conn.close()
        print("End of the insert_user_data function")
        return jsonify({'status' : 'failed', 'message' : "User Registration Failed!!!"})

def insert_video_data(data):
    print("Start of insert_video_data function")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("INSERT INTO video_path VALUES(?,?,?,?)", (None,data[0], data[1], data[2]))
    conn.commit()
    if c.lastrowid:
        conn.close()
        print("End of the insert_video_data function")
        return jsonify({'status' : 'success', 'address': data[2],'message' : "Video path insertion Successfull!!!"})
    else:
        conn.close()
        print("End of the insert_video_data function")
        return jsonify({'status' : 'failed', 'message' : "Video path insertion Failed!!!"})

    
def reterive_user_data(name):
    print("Inside of the retreive_user_data function")

    print("name for Authenitification", name)
    namez = str(name)
    print("Name inside retrive user data function",namez)
    
    user_name = namez.split('-')
    print(user_name[0])
    print(user_name[1])
    fname = re.sub('[^A-Za-z0-9]+', '',user_name[0])
    lname = re.sub('[^A-Za-z0-9]+', '',user_name[1])
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT MemberID,Department,UserType from users_table WHERE FirstName=? and LastName=?", (fname, lname))
    rows = c.fetchall()
    conn.close()
    print("Length",len(rows))
#    return "helo"
    
    if len(rows)==0:
        print("Inside if function")
        details = {
                "ststus": "success",
                "message":"No User found in record"
                }
        return jsonify(details)
    else:
        print("Inside else function")
        res = rows[0]
        print("ERes",res)
        print(type(res))
    #    print(res[0])
    #    print(res[1])
        MemberID = res[0]
        Department = res[1]
        UserType = res[2]
        FullName = fname +" " + lname
        details = {
                    "Name" : FullName,
                    "MemberID" : MemberID,
                    "Department" : Department,
                    "UserType" : UserType
                    }
      
        return details

def convertTuple(tup): 
    str =  ''.join(tup) 
    return str


def retreive_vid_addr(videoname):
    print("Start of retreive_vid_adddr function")
    print("VideoName",videoname)
   
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT output_path from video_path WHERE name =?", [videoname])
    rows = c.fetchall()
    conn.close()
#    print(rows)
    print(rows)
    addr = convertTuple(rows[0])    
    print(addr)
    print("End of retreive_vid_adddr function")
    return addr

def retreive_user_stat(Year):
    print("Start if retrieve uder_data function")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
#    Year=int(Year)
    sql="SELECT strftime('%Y', RegDate) as valYear,strftime('%m', RegDate) as valMonth, count(*) FROM users_table WHERE valYear = '"+Year+"' GROUP BY valMonth"
    c.execute(sql)
    rows = c.fetchall()
    conn.close()
    print("End of retreive_user_data function")
    rows = [{"Year": x[0], "Month": x[1], "Count": x[2]} for x in rows]
    return json.dumps(rows)

def insert_auth_stat(data):
    print("Inside of the insert_auth_stat function")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("INSERT INTO auth_stat VALUES(?,?,?,?,datetime())",(None,data[0], data[1], data[2]))
    conn.commit()
    conn.close()
    print("End of insert_auth_stat function")
    return "Hello"

def insert_real_time_data(BuildingNum,floor,lab, coffeeroom, fitnesscenter, pool):
    print("Inside the insert_real_time_data function")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("INSERT INTO real_time_stat VALUES(?,?,?,?,?,?,?,datetime())",(None,BuildingNum,
                                                 floor,lab, coffeeroom, fitnesscenter, pool))
    conn.commit()
    conn.close()
    print("End of insert_auth_stat function")
    return None

def retreive_real_time_data():
    print("Start of retreive_real_tine_data function")
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
#    sql = "SELECT * FROM real_time_stat ORDER BY RealTimeID DESC LIMIT 1"
    c.execute("SELECT BuildingNum,fllor,Lab,CoffeeRoom,FitnessCenter,Pool,realDateTime FROM real_time_stat ORDER BY RealTimeID DESC LIMIT 1")
    rows = c.fetchall()
    conn.close()
    print("End of retrieval_real_time_data function")
    return rows

def retreieve_video_stat():
     print("Start of retreieve_video_stat function")
     conn = sqlite3.connect(db_file)
     c = conn.cursor()
#    sql = "SELECT * FROM real_time_stat ORDER BY RealTimeID DESC LIMIT 1"
     c.execute("SELECT imagebase,name, Date, Time,Location,videolink FROM video_stat")
     rows = c.fetchall()
     conn.close()
     print("End of retreieve_video_stat function")
     return rows
 
    
""" 
 ############################################ End of Database part############################################
"""


""" 
 ####################################### Beginning of Face Recognition part############################################
"""

def encoding_images(folder):
    print("Inside of Encoding file")
    knownEncodings = []
    knownNames = []
    new_name = []

    print("Encoding file",folder)
#    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images(folder))
    print("Imagepaths",imagePaths)
    # initialize the list of known encodings and known names
    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
        
    #    print("Doing image:",i)
    	# extract the person name from the image path
    	print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))
    	name = imagePath.split(os.path.sep)[-2]
    	print("Name", name)
    
    	# load the input image and convert it from RGB (OpenCV ordering)
    	# to dlib ordering (RGB)
    	image = cv2.imread(imagePath)
    	rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    	# detect the (x, y)-coordinates of the bounding boxes
    	# corresponding to each face in the input image
    	boxes = face_recognition.face_locations(rgb,model='cnn')
    
    	# compute the facial embedding for the face
    	encodings = face_recognition.face_encodings(rgb, boxes)
    
    	# loop over the encodings
    	for encoding in encodings:
    		# add each encoding + name to our set of known names and
    		# encodings
    		knownEncodings.append(encoding)
    		knownNames.append(name);print("Name",name)
        
    for k in knownNames:
        if "dataset/" in k:
            k = k.replace('dataset/','')
            new_name.append(k)
        else:
            new_name.append(k)
    
    print("New Names",new_name)
            
    # dump the facial encodings + names to disk
    print("[INFO] serializing encodings...")
    
    
    data = {"encodings": knownEncodings, "names": knownNames}
    file = 'encodings.pickle'
    if os.path.exists(file):
        print("Inside existing doirectory")
        exefile = open(file, 'rb')
        new_dict = pickle.load(exefile, encoding='latin1')
        encodings = new_dict['encodings']
        names = new_dict['names']
        exefile.close()
        with open(file, "wb") as varfile:
            var_enc = []
            var_name = []
            for enc in encodings:
                var_enc.append(enc)
            for kenc in knownEncodings:
                var_enc.append(kenc)
                
            for name in names:
                var_name.append(name)
            for nname in new_name:
                var_name.append(nname)
            print(var_name)
            print("Looooking for this",var_name)
            new_data = {"encodings": var_enc, "names":var_name}
            pickle.dump(new_data, varfile)
            varfile.close()
            print ("end of encodeing")
#            exit()
        
    else:
        print("Inside of Non existing doirectory")
        with open(file, "wb") as f:
            for k in knownNames:
                if "dataset/" in k:
                    k = k.replace('dataset/','')
                    new_name.append(k)
                else:
                    new_name.append(k)
            
            newdata = {"encodings": knownEncodings, "names": new_name}
            pickle.dump(newdata, f)
            f.close()
            exit()
    print("Encoding is done")
    return "data is getting encoded"

# This function will recognise the unknown image
def recognition_image(Imageaddrs):
    print("Inside the recognition_image Function")
	# Recognize the images
    print("Image Address is ",Imageaddrs)
    image_to_be_matched = face_recognition.load_image_file(Imageaddrs)
    image_to_be_matched_encoded = face_recognition.face_encodings(image_to_be_matched)[0]
    name = []
    infile = open("encodings.pickle",'rb')
    new_dict = pickle.load(infile, encoding='latin1')

    known_encodings = new_dict['encodings']
    known_name = new_dict['names']
    files_count = len(known_encodings)
#    print("known Names in recogntion part", known_name)
    name = []
    for i in range(0,files_count):
        current_image_encoded = known_encodings[i]
        result = face_recognition.compare_faces(
            [image_to_be_matched_encoded], current_image_encoded)
        if result[0] == True:
            print("Matched: ") 
            name.append(known_name[i])
            break
        else:
            print("")
    if len(name) == 0:
        data = ["Null","Null",2]
        result = insert_auth_stat(data)
        return jsonify({'status' : 'success', 'message' : "Unknown"})
    else:
        users_data = reterive_user_data(name)
        MemberID = users_data['MemberID']; Name = users_data['Name']; UserType = users_data['UserType']
        data = [MemberID, Name, UserType]
#        print("users_data",users_data)
        
        result = insert_auth_stat(data)
    print("End of recognition_image")
    return jsonify({'status' : 'success', 'message' : users_data})
#        return "hello"
    
""" 
 ####################################### End of Face Recognition part############################################
"""
   
"""
 ################################## Beginning of misc function############################################
"""
#Function to create the dataset folder dataset_creation 01.02
def dataset_creation(image_encoding, FirstName, LastName):
    print("Start of the dataset creation function")
    folder = "dataset/"+ FirstName +"-"+ LastName 
    print("Folder Name", folder)
    
    if  os.path.isdir(folder) is False:
        os.makedirs(folder)
        #Calling Function image_save ID-01.03
        savedto = image_save(folder, image_encoding)
        print("save to dateset",savedto)
        print("End the dataset creation function")
        return savedto
    else:
       return None
# Function to save the image by decoding from base64 to jpg format ID-01.03
def image_save(folder, image_encoding):
    print("Start of image_Save function")
#    print("Folder is",folder) 

    file_name = len([name for name in os.listdir(folder) if os.path.isfile(os.path.join(folder, name))]) + 1
    img_format = ".jpg"
    address = folder + "/"
    savedto = f'{address}{file_name}{img_format}'

    fh = open(savedto, "wb")
    fh.write(image_encoding)
    fh.close()
    print("End of image_Save function")
    return savedto
    
	
def temp_image_save(folder, image_encoding):
    print("Start of image_Save function")
#    print("Folder is",folder) 
    file_name = len([name for name in os.listdir(folder) if os.path.isfile(os.path.join(folder, name))]) + 1
    img_format = ".jpg"
    address = folder + "/"
    savedto = f'{address}{file_name}{img_format}'

    fh = open(savedto, "wb")
    fh.write(image_encoding)
    fh.close()
    
    print("End of image_Save function")
    return savedto

# Funcation to convert the base64 to string image encoding base_enc_image 01.01
def base_enc_image(Imagebase, FirstName, LastName):
    print("Start of base_enc_image function")
    if type(Imagebase) is None:
        print("Include the photo")
    else:
        Imagebase = str.encode(Imagebase)
        #print(type(Imagebase))
        image_encoding = base64.decodebytes(Imagebase)
        #print(type(image_encoding))
        # Calling Function dataset_creation 01.02
        savedto = dataset_creation(image_encoding, FirstName, LastName)
        print("Saved to in Base Encoding ",savedto)
#        print("Type in base enci",type(savedto))
    print("End of base_enc_image function")
    return savedto

# Encoding the Image for Unknown Face Authentification
def encoding_temp_image(Imagebase):
    print("Inside the encode_temp_image function")
    if type(Imagebase) is None:
        print("Include the photo")
    else:
        Imagebase = str.encode(Imagebase)
        #print(type(Imagebase))
        image_encoding = base64.decodebytes(Imagebase)
        folder = "temp" 
#    print("Folder Name", folder)

    if os.path.isdir(folder):
        # Calling Function image_save ID-01.03
        savedto = temp_image_save(folder, image_encoding)
    else:
        os.makedirs(folder)
        #Calling Function image_save ID-01.03
        savedto = temp_image_save(folder, image_encoding)
    
    print("End of encode_temp_image function")
    return savedto

#
#def download_video(video_addr):
#    print("Hello")
#    return "Hello"

    
"""
################################## End of misc function############################################
"""


""" 
################################## Beginning of Application Interaction part############################################
"""


@app.route('/', methods=['GET'])
def hello():

    return "Hello World!"


@app.route('/appregistration', methods=['POST'])
# For the regiestration purposes Function ID - 01
def registration():
	# User registration functionality
	# It includes the following sub-functionality
		# Encoding
		# Saving the data to database    
    print("Start of the Registration Function")
    MemberID = request.form.get('MemberID')
#    MemberID = random.randint(0, 10000)
#    print(MemberID)
    FirstName = request.form.get("FirstName")
#    print("First Name",FirstName)
    LastName = request.form.get("LastName")
#    print("Last Name",LastName)
    Email = request.form.get("Email")
#    print("Department",Department)
    MobileNumber = request.form.get("MobileNumber")
#    print("Position",Position)
    Imagebase = request.form.get('imagebase')
    Department = request.form.get('Department')
    
    UserType = request.form.get("UserType")
    # Calling function basebase_enc_image 01.01
    addr = base_enc_image(Imagebase, FirstName, LastName)
    print("Length",addr)
    if addr is None:
        print("Inside null")
        val = {"Staus": "Failed","Message":"User is already registered"}
        return jsonify(val), 200
    else:
#         Calling function to insert_data into database of user table
         data = (MemberID,FirstName, LastName,Email,MobileNumber,Department,Imagebase,UserType,addr)
         status = insert_user_data(data)
         folder = "dataset/"+ FirstName+"-"+LastName
         val = encoding_images(folder)
         print(val)
         print("End of the Registration Function")
         val = {"Staus": "Successful","Message":"User is registered"}
         return jsonify(val) , 200

    
@app.route('/appauthentication', methods=['POST'])
def authentication():
	# Encoding the user Images
	# It includes the following sub-functionality
		# Encoding
		# Reterival from DB
		# Send notfication to appp
    Imagebase = request.form.get('imagebase')
    
    Imageaddrs = encoding_temp_image(Imagebase)

    dumpo = recognition_image(Imageaddrs)   
    
    return dumpo

@app.route('/apptracking', methods=['POST'])
def tracking():
#    print(type(video))
	# here I need to check the authenticates user and track their movement.
	# It includes the following  sub-functionality
		# encoding
		# Retrieval of known person encoding from database
		# Recongnize the people
    
    video =  request.files["video"]
    videoname = request.form.get('video_name')
    filename = secure_filename(video.filename)
    # TODO check path before save
    path = os.path.join(app.config['videos'])
    print("path",path)
    if not os.path.exists(path):
        os.makedirs(path)
    path_filename = os.path.join(path, filename)
    print("path_filename",path_filename)
    video.save(path_filename)
    inp_file = "videos/" + video.filename
    out_file = videoname + "_output" + ".avi"
    display = 2
    
    
#    # load the known faces and embeddings
#    print("[INFO] loading encodings...")
#    data = pickle.loads(open("encodings.pickle", "rb").read())
#
#    # initialize the pointer to the video file and the video writer
#    print("[INFO] processing video...")
#    stream = cv2.VideoCapture(inp_file)
#    writer = None
#    
#    # loop over frames from the video file stream
#    while True:
#        
##       grab the next frame
#        (grabbed, frame) = stream.read()
#        if not grabbed:
#            break
## convert the input frame from BGR to RGB then resize it to have
## a width of 750px (to speedup processing)
#        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#        rgb = imutils.resize(frame, width=750)
#        r = frame.shape[1] / float(rgb.shape[1])
#        
#	# detect the (x, y)-coordinates of the bounding boxes
#	# corresponding to each face in the input frame, then compute
#	# the facial embeddings for each face
#        boxes = face_recognition.face_locations(rgb,model='cnn')
#        encodings = face_recognition.face_encodings(rgb, boxes)
#        names = []
## loop over the facial embeddings
#        for encoding in encodings:
#            matches = face_recognition.compare_faces(data["encodings"],encoding)
#            name = "Unknown"
#            
#            if True in matches:
#                
## find the indexes of all matched faces then initialize a
#			# dictionary to count the total number of times each face
#			# was matched
#                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
#                counts = {}
## loop over the matched indexes and maintain a count for
#			# each recognized face face
#                for i in matchedIdxs:
#                    name = data["names"][i]
#                    counts[name] = counts.get(name, 0) + 1
#                    
#
## determine the recognized face with the largest number
#			# of votes (note: in the event of an unlikely tie Python
#			# will select first entry in the dictionary)
#                    name = max(counts, key=counts.get)
#            # update the list of names
#            names.append(name)
#        # loop over the recognized faces
#        for ((top, right, bottom, left), name) in zip(boxes, names):
#            # rescale the face coordinates
#            top = int(top * r)
#            right = int(right * r)
#            bottom = int(bottom * r)
#            left = int(left * r)
#    # draw the predicted face name on the image
#            cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
#            y = top - 15 if top - 15 > 15 else top + 15
#            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
#	# if the video writer is None *AND* we are supposed to write
#	# the output video to disk initialize the writer
#        if writer is None and out_file is not None:
#            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
#            writer = cv2.VideoWriter(out_file, fourcc, 24,(frame.shape[1], frame.shape[0]), True)
#    	# if the writer is not None, write the frame with recognized
#	# faces t odisk
#        if writer is not None:
#            writer.write(frame)
#    	# check to see if we are supposed to display the output frame to
#	# the screen
#        if display > 0:
#            cv2.imshow("Frame", frame)
#            key = cv2.waitKey(1) & 0xFF
#            
## if the `q` key was pressed, break from the loop
#            if key == ord("q"):
#                break
#    # close the video file pointers
#    stream.release()
## check to see if the video writer point needs to be released
#    if writer is not None:
#        writer.release()

#    client = boto3.client('s3')
    data = [videoname,inp_file, out_file ]
    
    vid_status = insert_video_data(data)
    return vid_status
    

#@app.route('/video_output/<video_name>', methods=['GET'])
#def retreive_video_file(video_name):
##    videoname = request.form.get('video_name')
#    videoname = video_name
#    file_name = retreive_vid_addr(videoname)
#
#    return send_from_directory(directory='output', filename=file_name, as_attachment=True)


@app.route('/video_output', methods=['POST'])
def retreive_video_file():
    videoname = request.form.get('video_name')
    file_name = retreive_vid_addr(videoname)
#    print(type(file_name))
    val = { "status" :"success","URL":file_name}
    return jsonify(val), 200


@app.route('/live_feed', methods=['POST'])
def live_feed():
#    print("Hello")
#    Image = request.files['image']
    Imagebase = request.form.get('imagebase')
    
    Imageaddrs = encoding_temp_image(Imagebase)

    dumpo = recognition_image(Imageaddrs)   
    
    return dumpo

@app.route('/user_stat', methods=['POST'])
def user_stat():
    Year = request.form.get('year')
    print("Year",Year)
    result = retreive_user_stat(Year)
    return result

@app.route('/real_time', methods=['POST'])
def real_time():
    BuildingNum = random.randrange (1,4,1)
    floor = 1
    lab = random.randrange (0,15,1)
    coffeeroom = random.randrange (0,20,1)
    fitnesscenter = random.randrange (0,30,1)
    pool = random.randrange (0,15,1)
    stat = insert_real_time_data(BuildingNum,floor,lab, coffeeroom, fitnesscenter, pool)
    print(stat)
    results = retreive_real_time_data()

    result = results[0]
    resBuildingNum = result[0]
    resfloor = result[1]
    reslab = result[2]
    rescoffeeroom = result[3]
    fitnessroom = result[4]
    respool = result[5]
    restime = result[6]
    data = {
            "Building": resBuildingNum,
            "Floor" : resfloor,
            "Lab": reslab,
            "CoffeeRoom" :rescoffeeroom,
            "FitneesRoom" :fitnessroom,
            "Pool" : respool,
            "Time" : restime
            }
    return jsonify(data)

@app.route('/video_stat', methods=['POST'])
def video_stat():
    
    results = retreieve_video_stat()
    rows = [{"IMAGEBASE": x[0], "Name": x[1], "Date": x[2],"Time": x[3],"Location": x[4],"VideoLink": x[5]} for x in results]
    print(len(rows))
    return json.dumps(rows)


""" 
 ####################################### End of Application interaction part############################################
"""

if __name__ == '__main__':
    database()
    Port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',debug=True, port=Port)
    #app.run()

    

	
