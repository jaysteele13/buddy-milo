import cv2 as cv
import os
from datetime import datetime
from picamera2 import Picamera2
import time

BUDDY_NAME = 'jay'

def create_folder(name):
    
    buddy_folder = os.path.join('dataset', name)
    if not os.path.exists(buddy_folder):
        os.makedirs(buddy_folder)
    return buddy_folder

def capture_photos(name):
    folder = create_folder(name)
    
    # Initilise Pi Cam
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={'format':'XRGB8888', 'size': (640,480)}))
    
    picam2.start()
    
    time.sleep(2) # Allow cam to warm up yo
    
    photo_count = 0
    
    print(f"taking photos of {name} Press SPACE to capture and 'q' to quit")
    
    while True:
        frame = picam2.capture_array()
        
        cv.imshow('Capture', frame)
        
        key = cv.waitKey(1) & 0xFF
        
        # Capture Logic
        if key == ord(' '):
            photo_count += 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.jpg"
            filepath = os.path.join(folder, filename)
            cv.imwrite(filepath, frame)
            print(f"Photo {photo_count} saved as: {filepath}")
        elif key == ord('q'):
            break
        
    # after while clean up yo
    cv.destroyAllWindows()
    picam2.stop()
    print(f"Photo capture complete, took {photo_count} images for {name}")
    
    

if __name__ == "__main__":
    capture_photos(BUDDY_NAME)
        
