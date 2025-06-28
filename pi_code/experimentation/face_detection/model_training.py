import os
from imutils import paths
import face_recognition
import pickle
import cv2 as cv

print("starting to process faces...")
imagePaths = list(paths.list_images('dataset'))
knownEncodings = []
knownNames = []

for(i, imagePath) in enumerate(imagePaths):
    print(f"processing image {i+1}/{len(imagePaths)}")
    name = imagePath.split(os.path.sep)[-2]
    
    image = cv.imread(imagePath)
    rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    
    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)
    
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

print("[INFO] serialising encodings")
data = {"encodings": knownEncodings, "names": knownNames}

with open("encodings.pickle", "wb") as f:
    f.write(pickle.dumps(data))
    
print('training complete and dumped into pickle. yeh man thas wassup man')