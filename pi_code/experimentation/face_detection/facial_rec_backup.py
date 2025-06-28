import face_recognition
import cv2 as cv
import numpy as np
from picamera2 import Picamera2
import time
import pickle

print("[INFO] load the trained encodings")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
known_face_encodings = data["encodings"]
known_face_names = data["names"]

# Init camera

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={'format':'XRGB8888', 'size': (640,480)}))
picam2.start()

# CV scaler, what is this?
cv_scaler = 2

face_locations = []
face_encodings = []
face_names = []
frame_count = 0
start_time = time.time()
fps = 0

def process_frame(frame):
    global face_locations, face_encodings, face_names
    
    # Resize frame using cv Scaler to increase performance!
    resized_frame = cv.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
    
    # Must convert BGR to RGB with open CV
    rgb_resized_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2RGB)
    
    # Find all faces with face_rec library
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations,
                                                     model='large')
    # ^ Could model large be changed to be mor eperformant
    face_names = []
    
    for face_encoding in face_encodings:
        # See if I can find buddy matches
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Stranger"
        
        # use known face with smallest distance
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        
        best_match_idx = np.argmin(face_distances)
        if matches[best_match_idx]:
            name = known_face_names[best_match_idx]
        face_names.append(name)
    return frame

def draw_results(frame):
    # Display the results
    for(top, right, bottom, left), name in zip(face_locations, face_names):
        # Have Function which can map these to servo percentages also!
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler
        
        cv.rectangle(frame, (left, top), (right, bottom), (224,42,3),3)
        
        # Draw Label below face
        cv.rectangle(frame, (left-3, top-35), (right+3, top), (224, 42, 3), cv.FILLED)
        font = cv.FONT_HERSHEY_DUPLEX
        cv.putText(frame, name, (left+6, top-6), font, 1.0, (225,225,225),1)
    return frame

def calculate_fps():
    global frame_count, start_time, fps
    frame_count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 1:
        fps = frame_count / elapsed_time
        frame_count = 0
        start_time = time.time()
    return fps

while True:
    frame = picam2.capture_array()
    
    # Assign coords and faces into frame
    processed_frame = process_frame(frame)
    
    # Draw rectangles and text
    display_frame = draw_results(processed_frame)
    
    # Calculate FPS
    current_fps = calculate_fps()
    
    # Attach fps and boxes yo
    cv.putText(display_frame, f"FPS: {current_fps}", (display_frame.shape[1]-150,30), cv.FONT_HERSHEY_SIMPLEX,1,(0,225,0),2)
    
    # Display all
    cv.imshow('Imma track ya.', display_frame)
    
    if cv.waitKey(1) == ord('q'):
        break

# Clean Up Crew
cv.destroyAllWindows()
picam2.stop()
    

