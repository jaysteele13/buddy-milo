# sudo systemctl start pigpiod more exact for servo
# sudo systemctl stop pigpiod



import pigpio, time

SERVO_TILT_PIN = 19   # BCM/GPIO numbers when using pigpio
SERVO_PAN_PIN = 18   # BCM 16 == BOARD 36 (adjust to suit)

STEP_US = 20
# Based on Calbration -> must be done without camera controller
SERVO_PAN_MIN = 600
SERVO_PAN_MAX = 1800

SERVO_TILT_MIN = 800
SERVO_TILT_MAX = 1800



# Make a function to convert degree of where face is to pwm freq

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
        print(f'Tilt Target of {target}ms is valid.')
        return True
    else:
        print(f'Tilt Target not within bounds returning min bound of {min} Your target is {target}. Min and Max of Tilt is {min} and {max}')
        return False
    
def allow_pan(target, min = SERVO_PAN_MIN, max = SERVO_PAN_MAX):
    if target >= min and target <= max:
        print(f'Pan Target of {target}ms is valid.')
        return True
    else:
        print(f'Pan Target not within bounds returning false; bound not within {min}')
        return False
    
# def sentry():
#    
#     tilt_sequence = [1000, 1200, 1400]
#     step = int((SERVO_PAN_MAX - SERVO_PAN_MIN) / 8)
# 
#     for pan_pos in range(SERVO_PAN_MIN, SERVO_PAN_MAX + 1, step):
#         if allow_pan(pan_pos):
#             move(pi, SERVO_PAN_PIN, pan_pos)
# 
#             for tilt_pos in tilt_sequence:
#                 move(pi, SERVO_TILT_PIN, tilt_pos)
#                 time.sleep(0.05)  # Half-second check/hold at each tilt position
#                 
#     move(pi, SERVO_PAN_PIN, SERVO_PAN_MIN)
#     move(pi, SERVO_TILT_PIN, 1200)
#     time.sleep(0.5)

def face_detected():
    return False # will be a function that gets frame of camera and returns if face detected and coords

def sentry(speed = 0.05):
    tilt_sequence = [1000, 1200, 1400]
    step = int((SERVO_PAN_MAX - SERVO_PAN_MIN) / 8)

    pan_positions = list(range(SERVO_PAN_MIN, SERVO_PAN_MAX + 1, step))

    while True:
        for pan_pos in pan_positions:
            if face_detected():
                print("🎯 Face detected! Switching to tracking mode.")
                track_face()
                return  # or `break` to resume later

            if allow_pan(pan_pos):
                move(pi, SERVO_PAN_PIN, pan_pos)
                for tilt_pos in tilt_sequence:
                    if face_detected():
                        print("🎯 Face detected mid-tilt. Switching to tracking.")
                        track_face()
                        return  # exit sentry mode
                   
                    move(pi, SERVO_TILT_PIN, tilt_pos)
                    time.sleep(speed)
            else:
                move(pi, SERVO_PAN_PIN, SERVO_PAN_MIN)
                move(pi, SERVO_TILT_PIN, 1000)
                time.sleep(0.5)

        pan_positions.reverse()  # for sweeping back

    


            


if __name__ == "__main__":
    pi = pigpio.pi()           # pigpiod must be running: sudo systemctl start pigpiod
    try:
        # DONT TAKE APART OR MUST CALBRATE CENTER CORRECTLY
        # CURENNTLY PAN is 500 - 1800
        # Tilt is 800 - 1800 is WRONG 
        
        # Must find a way to change pulse width to be more centre other wise must tilt structure


        # 800 Min

        print('move tilt')
        pi.set_servo_pulsewidth(SERVO_TILT_PIN, 1400)
        time.sleep(0.5)
        print('move pan')
        pi.set_servo_pulsewidth(SERVO_PAN_PIN, 1000)
        time.sleep(0.5)

        # Smooth left and right sweeps
        
        # sentry()
        
        # look centre!
        # sweep(pi, SERVO_HEAD_PIN, LEFT_PW, CENTER_PW)
#         move(pi, SERVO_HEAD_PIN, 1000)  # sweep to far right
#         time.sleep(0.5)
#         move(pi, SERVO_HEAD_PIN, 1500)  # sweep to far right
#         time.sleep(0.5)
#         move(pi, SERVO_HEAD_PIN, 2000)  # sweep to far right
#         time.sleep(0.5)
#         move(pi, SERVO_HEAD_PIN, 2500)  # sweep to far right
#         move(pi, SERVO_PAN_PIN, 500)  # sweep to far right
#         time.sleep(0.5)
#         move(pi, SERVO_PAN_PIN, 2500)  # sweep to far right
#         time.sleep(0.5)

#         move(pi, SERVO_TILT_PIN, 500)  # sweep to far right
#         time.sleep(0.5)
#         move(pi, SERVO_PAN_PIN, 500)  # sweep to far right
#         time.sleep(0.5)
#         move(pi, SERVO_TILT_PIN, 1700)  # sweep to far right
#         time.sleep(0.5)
#         
#         # Cap of Tilt is 500 and 1700
        # Cap of Pan is 500 and 2500
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


# Realistically I want to bring all of this into a new folder where the camera uses sentry
# and can also detect either my face or enemy face and track my face based on mapped coordinates

# Begin the face tracking function tomorrow