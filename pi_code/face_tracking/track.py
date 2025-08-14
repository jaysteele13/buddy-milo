import face_recognition
import cv2 as cv
import numpy as np
from picamera2 import Picamera2
import time
import pickle
import pigpio
import sys
import asyncio
import os
import random

# sudo systemctl start pigpiod more exact for servo
# sudo systemctl stop pigpiod


SERVO_TILT_PIN = 19   # BCM/GPIO numbers when using pigpio
SERVO_PAN_PIN = 18   # BCM 16 == BOARD 36 (adjust to suit)
# Based on Calbration -> must be done without camera controller
SERVO_PAN_MIN = 500
SERVO_PAN_MAX = 1200

SERVO_TILT_MIN = 800
SERVO_TILT_MAX = 1600
STEP_US = 20

# Define tracking window


print("[INFO] load the trained encodings")
with open("face_detection/encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
known_face_encodings = data["encodings"]
known_face_names = data["names"]

# what happens -> I get a frame -> run model against pickle encodings and general face detection
# when getting frame function every fps I can return the frame, face_encodings and face_names
# firstly get face locations in this function
# for found faces put it into array
# compare encoded pickle file (pictures of me ) if they exist find name either 'jay' or 'enemy'

# Init camera
def init_cam():
    frame_width = 640
    frame_height = 480
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={'format':'XRGB8888', 'size': (frame_width,frame_height)}))
    picam2.start()
    return picam2

# CV scaler, what is this?
cv_scaler = 2

start_time = time.time()


def sweep(pi, pin, start_pw, end_pw, step_us=STEP_US, delay=0.01):
    direction = 1 if end_pw > start_pw else -1
    for pw in range(start_pw, end_pw + direction*step_us, direction*step_us):
        pi.set_servo_pulsewidth(pin, pw)
        time.sleep(delay)

def move(pi, pin, target_pw, *, step_us=20, delay=0.01, default_pw=1500):
    current_pw = pi.get_servo_pulsewidth(pin)
    if current_pw == 0:                # servo idle? assume centre
        current_pw = default_pw
        pi.set_servo_pulsewidth(pin, current_pw)
        time.sleep(delay)

    direction = 1 if target_pw > current_pw else -1
    for pw in range(current_pw,
                    target_pw + direction * step_us,
                    direction * step_us):
        pi.set_servo_pulsewidth(pin, pw)
        time.sleep(delay)

def allow_tilt(target, min = SERVO_TILT_MIN, max = SERVO_TILT_MAX):
    if target >= min and target <= max:
        #print(f'Tilt Target of {target}ms is valid.')
        return True
    else:
        print(f'Tilt Target not within bounds returning min bound of {min} Your target is {target}. Min and Max of Tilt is {min} and {max}')
        return False
    
def allow_pan(target, min = SERVO_PAN_MIN, max = SERVO_PAN_MAX):
    if target >= min and target <= max:
        #print(f'Pan Target of {target}ms is valid.')
        return True
    else:
        print(f'Pan Target not within bounds returning false; bound not within {min}')
        return False

def process_frame(frame):
    # Resize frame using cv Scaler to increase performance!
    resized_frame = cv.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
    
    # Must convert BGR to RGB with open CV
    rgb_resized_frame = cv.cvtColor(resized_frame, cv.COLOR_BGR2RGB)
    
    # Find all faces with face_rec library
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations,
                                                     model='small')
    # ^ Could model large be changed to be mor eperformant
    face_names = []
    
    for face_encoding in face_encodings:
        # See if I can find buddy matches
        print('Found a face!')
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Enemy"
        
        # use known face with smallest distance
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        
        best_match_idx = np.argmin(face_distances)
        if matches[best_match_idx]:
            name = known_face_names[best_match_idx]
            print(f'found {name}')
        face_names.append(name)
    return frame, face_locations, face_names

def map_servo_range(value, cam_min, cam_max, servo_min, servo_max):
    return int((value - cam_min) * (servo_max - servo_min)
               / (cam_max - cam_min) + servo_min)

def map_servo_range(angle, in_min, in_max, out_min, out_max):
    return out_min + (angle - in_min) * (out_max - out_min) / (in_max - in_min)


# PD gain
def map_pwm_to_angle(pwm_value, pwm_min, pwm_max, angle_min=0, angle_max=180):
    return (pwm_value - pwm_min) * (angle_max - angle_min) / (pwm_max - pwm_min) + angle_min

FULL_PWM_MIN = 500
FULL_PWM_MAX = 2500

PAN_MIN_ANGLE = map_pwm_to_angle(SERVO_PAN_MIN, FULL_PWM_MIN, FULL_PWM_MAX)
PAN_MAX_ANGLE = map_pwm_to_angle(SERVO_PAN_MAX, FULL_PWM_MIN, FULL_PWM_MAX)
TILT_MIN_ANGLE = map_pwm_to_angle(SERVO_TILT_MIN, FULL_PWM_MIN, FULL_PWM_MAX)
TILT_MAX_ANGLE = map_pwm_to_angle(SERVO_TILT_MAX, FULL_PWM_MIN, FULL_PWM_MAX)
def track_face(local_pi, x, y, prev_error_x, prev_error_y, pan_angle, tilt_angle):
    
    # Still decent. Stabilise. Robot looks at face and around the face but never sticks to face and stops moving. Perhaps future work to amend this?
    Kp = 0.052
    Kd = 0.02
    DEADZONE = 32
    MAX_CONTROL_STEP = 3

    frame_center_x = 640 // 2
    frame_center_y = 480 // 2

    # Compute error between face and center
    error_x = x - frame_center_x
    error_y = y - frame_center_y
    print(f"Error of X: {error_x}. Error of y: {error_y}")

    # Apply deadzone
    if abs(error_x) < DEADZONE:
        error_x = 0
        delta_error_x = 0
    else:
        delta_error_x = error_x - prev_error_x

    if abs(error_y) < DEADZONE:
        error_y = 0
        delta_error_y = 0
    else:
        delta_error_y = error_y - prev_error_y

    # PD control
    control_x = Kp * error_x + Kd * delta_error_x
    control_y = Kp * error_y + Kd * delta_error_y

    # Clamp control signal
    control_x = max(min(control_x, MAX_CONTROL_STEP), -MAX_CONTROL_STEP)
    control_y = max(min(control_y, MAX_CONTROL_STEP), -MAX_CONTROL_STEP)

    # Update angles - adjust these if direction is wrong
    pan_angle -= control_x  # Use += if needed (depends on servo setup)
    tilt_angle += control_y  # Use -= if camera goes wrong direction

    # Clamp to allowed angles
    pan_angle = max(min(pan_angle, PAN_MAX_ANGLE), PAN_MIN_ANGLE)
    tilt_angle = max(min(tilt_angle, TILT_MAX_ANGLE), TILT_MIN_ANGLE)

    # Map to PWM range
    servo_x = map_servo_range(pan_angle, PAN_MIN_ANGLE, PAN_MAX_ANGLE, SERVO_PAN_MIN, SERVO_PAN_MAX)
    servo_y = map_servo_range(tilt_angle, TILT_MIN_ANGLE, TILT_MAX_ANGLE, SERVO_TILT_MIN, SERVO_TILT_MAX)

    # Optional: only move if inside limits
    if allow_pan(servo_x) and allow_tilt(servo_y):
        move(local_pi, SERVO_PAN_PIN, servo_x)
        move(local_pi, SERVO_TILT_PIN, servo_y)

    return error_x, error_y, pan_angle, tilt_angle

async def track_faceV2(local_pi, x, y, prev_error_x, prev_error_y, pan_angle, tilt_angle):
    
    # Still decent. Stabilise. Robot looks at face and around the face but never sticks to face and stops moving. Perhaps future work to amend this?
    Kp = 0.052
    Kd = 0.02
    DEADZONE = 32
    MAX_CONTROL_STEP = 3

    frame_center_x = 640 // 2
    frame_center_y = 480 // 2

    # Compute error between face and center
    error_x = x - frame_center_x
    error_y = y - frame_center_y
    print(f"Error of X: {error_x}. Error of y: {error_y}")

    # Apply deadzone
    if abs(error_x) < DEADZONE:
        error_x = 0
        delta_error_x = 0
    else:
        delta_error_x = error_x - prev_error_x

    if abs(error_y) < DEADZONE:
        error_y = 0
        delta_error_y = 0
    else:
        delta_error_y = error_y - prev_error_y

    # PD control
    control_x = Kp * error_x + Kd * delta_error_x
    control_y = Kp * error_y + Kd * delta_error_y

    # Clamp control signal
    control_x = max(min(control_x, MAX_CONTROL_STEP), -MAX_CONTROL_STEP)
    control_y = max(min(control_y, MAX_CONTROL_STEP), -MAX_CONTROL_STEP)

    # Update angles - adjust these if direction is wrong
    pan_angle -= control_x  # Use += if needed (depends on servo setup)
    tilt_angle += control_y  # Use -= if camera goes wrong direction

    # Clamp to allowed angles
    pan_angle = max(min(pan_angle, PAN_MAX_ANGLE), PAN_MIN_ANGLE)
    tilt_angle = max(min(tilt_angle, TILT_MAX_ANGLE), TILT_MIN_ANGLE)

    # Map to PWM range
    servo_x = map_servo_range(pan_angle, PAN_MIN_ANGLE, PAN_MAX_ANGLE, SERVO_PAN_MIN, SERVO_PAN_MAX)
    servo_y = map_servo_range(tilt_angle, TILT_MIN_ANGLE, TILT_MAX_ANGLE, SERVO_TILT_MIN, SERVO_TILT_MAX)

    # Optional: only move if inside limits
    if allow_pan(servo_x) and allow_tilt(servo_y):
        move(local_pi, SERVO_PAN_PIN, servo_x)
        move(local_pi, SERVO_TILT_PIN, servo_y)

    return error_x, error_y, pan_angle, tilt_angle


TILT_SWEEP_MIN = 1000
TILT_SWEEP_MAX = 1400
def sentry_sweep(step_size=40, delay_between_steps=0.05):
   
    
    pan_pos = SERVO_PAN_MIN
    tilt_pos = TILT_SWEEP_MIN # Range between 1200 -> 1400
    pan_direction = 1  # 1 = right, -1 = left
    tilt_direction = 1
    last_step_time = time.monotonic()

    while True:
        current_time = time.monotonic()
        if current_time - last_step_time < delay_between_steps:
            continue  # Non-blocking wait
        
        last_step_time = current_time  # Reset timer for next pan step
        if(allow_pan(pan_pos)):
            move(pi, SERVO_PAN_PIN, pan_pos)
        if(allow_pan(tilt_pos)):
            move(pi, SERVO_TILT_PIN, tilt_pos)
        
            
        #time.sleep(settle_delay)  # Small delay to let movement take effect

        frame = picam2.capture_array()
        processed_frame, face_locations, face_names = process_frame(frame)

        if face_locations and len(face_locations) > 0:
            print("🎯 Face detected during sweep!")
            display_frame, x, y = draw_results_and_coord(processed_frame, face_locations, face_names)

            servo_x = map_servo_range(x, 0, frame_width, 0, 180)
            servo_y = map_servo_range(y, 0, frame_height, 0, 180)

            track_face(servo_x, servo_y)
            return

        # Increment pan position
        pan_pos += pan_direction * step_size
        tilt_pos += tilt_direction * step_size
        

        # Reverse direction at limits
        if pan_pos >= SERVO_PAN_MAX:
            pan_pos = SERVO_PAN_MAX
            pan_direction = -1
        elif pan_pos <= SERVO_PAN_MIN:
            pan_pos = SERVO_PAN_MIN
            pan_direction = 1
            
        if tilt_pos >= TILT_SWEEP_MAX:
            tilt_pos = TILT_SWEEP_MAX
            tilt_direction = -1
        elif tilt_pos <= TILT_SWEEP_MIN:
            tilt_pos = TILT_SWEEP_MIN
            tilt_direction = 1
       


def get_tilt_index(tilt_index, len_of_sequence):
    
    tilt_multiplyer = 1
    
    if tilt_index >= len_of_sequence-1:
        tilt_multiplyer = -1
        tilt_index += 1 * tilt_multiplyer
    elif tilt_index <= 0:
        tilt_multiplyer = 1
        tilt_index += 1 * tilt_multiplyer
    else:
        tilt_index += 1 * tilt_multiplyer
    return tilt_index

def map_pwm_to_angle(pwm, pwm_min, pwm_max, angle_min, angle_max):
    return angle_min + ((float(pwm - pwm_min) / (pwm_max - pwm_min)) * (angle_max - angle_min))

# 
def sentry_sweepV3(local_pi, local_cam, step_size=40, delay_between_steps=0.05):
    print('Starting the Mighty Sweep')
    tilt_sequence = [1000, 1200, 1400]
    pan_pos = SERVO_PAN_MIN
    pan_direction = 1  # 1 = right, -1 = left
    tilt_index = 0

    last_step_time = time.monotonic()
    last_face_seen_time = None
    seconds_to_wait = 5

    error_x = 0
    error_y = 0
    # This must be ammended so it inputs the pan angle and tilt angle of the current servo rather than a genric centre one
#     pan_angle = (PAN_MIN_ANGLE + PAN_MAX_ANGLE) // 2
#     tilt_angle = (TILT_MIN_ANGLE + TILT_MAX_ANGLE) // 2
    pan_angle = None
    tilt_angle = None
    first_time_tracking = True
    while True:
        current_time = time.monotonic()

        # Sweep mode
        if last_face_seen_time is None:
            if current_time - last_step_time >= delay_between_steps:
                last_step_time = current_time
                if allow_pan(pan_pos):
                    move(local_pi, SERVO_PAN_PIN, pan_pos)

                pan_pos += pan_direction * step_size
                if pan_pos >= SERVO_PAN_MAX or pan_pos <= SERVO_PAN_MIN:
                    pan_direction *= -1  # reverse direction
                    tilt_index = (tilt_index + 1) % len(tilt_sequence)
                    move(local_pi, SERVO_TILT_PIN, tilt_sequence[tilt_index])
        
        # Capture and process frame
        frame = local_cam.capture_array()
        processed_frame, face_locations, face_names = process_frame(frame)

        if face_locations:
            # Face detected, start or reset tracking mode timer
            last_face_seen_time = current_time

            # Track face
            print('tracking face')
            # IF face is found must then return the x, y, and pan and tilt enagle with the error starting off as 0, 0
            x, y = draw_results_and_coord(face_locations, face_names)
            
            if first_time_tracking or pan_angle is None or tilt_angle is None:
                print("Initializing pan/tilt based on face position")
                
                # Map face to angles
                pan_angle = map_pwm_to_angle(pan_pos, SERVO_PAN_MIN, SERVO_PAN_MAX, PAN_MIN_ANGLE, PAN_MAX_ANGLE)
                tilt_angle = map_pwm_to_angle(tilt_sequence[tilt_index], SERVO_TILT_MIN, SERVO_TILT_MAX, TILT_MIN_ANGLE, TILT_MAX_ANGLE)
                
                tilt_angle = max(TILT_MIN_ANGLE, min(TILT_MAX_ANGLE, (tilt_angle+5))) # Giving Tilt bias so it doesn't overshoot
                
                first_time_tracking = False
            
            # Pan angle is based on pan_pos number	
            # Tilt angle is based on tilt_sequence[tilt_index]
            # Camera resolution
            
            
            error_x, error_y, pan_angle, tilt_angle = track_face(local_pi,
                x, y, error_x, error_y, pan_angle, tilt_angle
            )

        elif last_face_seen_time is not None: # or if chatting to user don't sweep
            # Face was seen before, but not now
            if current_time - last_face_seen_time > seconds_to_wait:  # seconds
                print(f"Lost face for {seconds_to_wait} seconds, resuming sweep.")
                last_face_seen_time = None  # Go back to sweep mode
                pan_angle = None
                tilt_angle = None
                first_time_tracking = True

            
    
def pick_random_file(dir_path):
    # List all file names in the given directory
    files_list = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    
    if not files_list:
        return None  # or raise an error if preferred
    
    # Randomly pick one file name
    return f'{dir_path}/{random.choice(files_list)}'
    
async def play_output(file_path):
    print("🎧 Playing response...")

    process = await asyncio.create_subprocess_exec("aplay", file_path)
    await process.wait()

    print("🎧 Playback finished.")
    
async def find_and_greet(dir_path):
    file_path = pick_random_file(dir_path)
    
    if file_path is None:
        print('Invalid File Path')
        return
    await play_output(file_path)
    
    
def face_exists(name):
    dir_name = 'presets/greetings/'
    return name in os.listdir(dir_name)

async def sentry_sweepV4(local_pi, local_cam, stop_event: asyncio.Event, step_size=40, delay_between_steps=0.05) -> None:
    print('Starting the Mighty Sweep')
    await asyncio.sleep(0.1)
    tilt_sequence = [1100, 1200, 1300]
    pan_pos = SERVO_PAN_MIN
    pan_direction = 1  # 1 = right, -1 = left
    tilt_index = 0

    last_step_time = time.monotonic()
    last_face_seen_time = None
    seconds_to_wait = 5

    error_x = 0
    error_y = 0
    # This must be ammended so it inputs the pan angle and tilt angle of the current servo rather than a genric centre one
#     pan_angle = (PAN_MIN_ANGLE + PAN_MAX_ANGLE) // 2
#     tilt_angle = (TILT_MIN_ANGLE + TILT_MAX_ANGLE) // 2
    pan_angle = None
    tilt_angle = None
    first_time_tracking = True
    while not stop_event.is_set(): # was
        current_time = time.monotonic()
  

        # Sweep mode
        if last_face_seen_time is None:
           
            if current_time - last_step_time >= delay_between_steps:
                last_step_time = current_time
                if allow_pan(pan_pos):
                   
                    await asyncio.to_thread(move, local_pi, SERVO_PAN_PIN, pan_pos)

                pan_pos += pan_direction * step_size
                if pan_pos >= SERVO_PAN_MAX or pan_pos <= SERVO_PAN_MIN:
                    pan_direction *= -1  # reverse direction
                    tilt_index = (tilt_index + 1) % len(tilt_sequence)
                    await asyncio.to_thread(move, local_pi, SERVO_TILT_PIN, tilt_sequence[tilt_index])

        
        # Capture and process frame
        face_names = []
        frame = await asyncio.to_thread(local_cam.capture_array)
        processed_frame, face_locations, face_names = await asyncio.to_thread(process_frame, frame)
        

        if face_locations:
            # Face detected, start or reset tracking mode timer
            last_face_seen_time = current_time

            # Track face
            # Greeting Check
            print(f'Here is the name of face: {face_names[0]}')
            if face_exists(face_names[0]): # and (current_time offset of 5 minutes) -> should this even be done
                
                #Name must match greetings dir name
                dir_path = f'presets/greetings/{face_names[0]}'
                await find_and_greet(dir_path)
            
            stop_event.set()
            x, y = draw_results_and_coord(face_locations, face_names)

            pan_angle = map_pwm_to_angle(pan_pos, SERVO_PAN_MIN, SERVO_PAN_MAX, PAN_MIN_ANGLE, PAN_MAX_ANGLE)
            tilt_angle = map_pwm_to_angle(tilt_sequence[tilt_index], SERVO_TILT_MIN, SERVO_TILT_MAX, TILT_MIN_ANGLE, TILT_MAX_ANGLE)
            
            tilt_angle = max(TILT_MIN_ANGLE, min(TILT_MAX_ANGLE, (tilt_angle+5))) # Giving Tilt bias so it doesn't overshoot
            
            
            return x, y, pan_angle, tilt_angle
            
            # Pan angle is based on pan_pos number	
            # Tilt angle is based on tilt_sequence[tilt_index]
            # Camera resolution
            
            
            

        elif last_face_seen_time is not None: # or if chatting to user don't sweep
            # Face was seen before, but not now
            if current_time - last_face_seen_time > seconds_to_wait:  # seconds
                print(f"Lost face for {seconds_to_wait} seconds, resuming sweep.")
                last_face_seen_time = None  # Go back to sweep mode
                pan_angle = None
                tilt_angle = None
                first_time_tracking = True


async def sentry_sweepV5(local_pi, stop_event: asyncio.Event, step_size=40, delay_between_steps=0.05) -> None:
    print('🔄 Starting the Mighty Sweep V4')
    await asyncio.sleep(0.1)

    tilt_sequence = [1000, 1200, 1400]
    pan_pos = SERVO_PAN_MIN
    pan_direction = 1
    tilt_index = 0

    last_step_time = time.monotonic()
    last_face_seen_time = None
    seconds_to_wait = 5
    
    pan_angle = None
    tilt_angle = None
    first_time_tracking = True

    while not stop_event.is_set():
        current_time = time.monotonic()

        # Sweep Mode
        if last_face_seen_time is None:
            if current_time - last_step_time >= delay_between_steps:
                last_step_time = current_time

                if allow_pan(pan_pos):
                    print(f"📍 Moving to pan position {pan_pos}")
                    await asyncio.to_thread(move, local_pi, SERVO_PAN_PIN, pan_pos)

                pan_pos += pan_direction * step_size

                if pan_pos >= SERVO_PAN_MAX or pan_pos <= SERVO_PAN_MIN:
                    pan_direction *= -1
                    tilt_index = (tilt_index + 1) % len(tilt_sequence)
                    new_tilt = tilt_sequence[tilt_index]
                    print(f"🎯 Adjusting tilt to {new_tilt}")
                    await asyncio.to_thread(move, local_pi, SERVO_TILT_PIN, new_tilt)

        # Frame Capture and Face Detection
        frame = await asyncio.to_thread(picam2.capture_array)
        processed_frame, face_locations, face_names = await asyncio.to_thread(process_frame, frame)
        print("📷 Frame captured and processed")

        if face_locations:
            print("🧠 Face detected — exiting sweep mode")
            stop_event.set()
            return

        elif last_face_seen_time is not None:
            if current_time - last_face_seen_time > seconds_to_wait:
                print(f"😶 Lost face for {seconds_to_wait} seconds — resuming sweep")
                last_face_seen_time = None
                pan_angle = None
                tilt_angle = None
                first_time_tracking = True

            

# Create Function to draw Rectangle and also relay x,y coords of centre of box
def draw_results_and_coord(face_locations, face_names):
    
    x = 0
    y = 0
    
    # Display the results
    for(top, right, bottom, left), name in zip(face_locations, face_names):
        # Have Function which can map these to servo percentages also!
        top *= cv_scaler
        right *= cv_scaler
        bottom *= cv_scaler
        left *= cv_scaler
        
        
        # I believe x and y should just be this. Can experiment with servos
        x = (right + left) // 2
        y = (top + bottom) // 2
   
        
    return x,y


def map_servo_range(value, cam_min, cam_max, servo_min, servo_max):
    return int((value - cam_min) * (servo_max - servo_min)
               / (cam_max - cam_min) + servo_min)

if __name__ == "__main__":
    pi = pigpio.pi()           # pigpiod must be running: sudo systemctl start pigpiod
    try:
        # DONT TAKE APART OR MUST CALBRATE CENTER CORRECTLY
        # CURENNTLY PAN is 500 - 1800
        # Tilt is 800 - 1800 is WRONG 
        
        # Must find a way to change pulse width to be more centre other wise must tilt structure

        pi.set_servo_pulsewidth(SERVO_TILT_PIN, 1150)
        pi.set_servo_pulsewidth(SERVO_PAN_PIN, 800)
        time.sleep(0.5)

        # Smooth left and right sweeps
        
        # face_tracking()
        sentry_sweepV3(pi)
        
        
    except KeyboardInterrupt:
        # Clean up GPIO on keyboard interrupt
        pi.set_servo_pulsewidth(SERVO_TILT_PIN, 0)
        pi.set_servo_pulsewidth(SERVO_PAN_PIN, 0)
        pi.stop()

    finally:
        # Turn pulses off so the servos relax
        pi.set_servo_pulsewidth(SERVO_TILT_PIN, 0)
        pi.set_servo_pulsewidth(SERVO_PAN_PIN, 0)
        pi.stop()

    
    
        
