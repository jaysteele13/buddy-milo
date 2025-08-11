# sudo systemctl start pigpiod more exact for servo
# sudo systemctl stop pigpiod



import pigpio, time, random, asyncio

SERVO_TILT_PIN = 19   # BCM/GPIO numbers when using pigpio
SERVO_PAN_PIN = 18   # BCM 16 == BOARD 36 (adjust to suit)

STEP_US = 20
# Based on Calbration -> must be done without camera controller
SERVO_PAN_MIN = 500
SERVO_PAN_MAX = 1200

SERVO_TILT_MIN = 800
SERVO_TILT_MAX = 1600




def safe_set_servo(pi, pin, value):
    pulse = clamp_pulse(value, pin)
    pi.set_servo_pulsewidth(pin, pulse)

# Make a function to convert degree of where face is to pwm freq

async def dance(pi):
    pan_start_sequence = [600, 1200, 1000, 800, 600]
    headbang_tilts = [(1000, 1200), (1200, 1000)] * 2

    tilt_drop = 600

    # Start tilt at center
    move(pi, SERVO_TILT_PIN, 1000)

    length = len(pan_start_sequence)
    
    # Shuffle the pan sequence for random movement order
    pan_indices = list(range(length))
    random.shuffle(pan_indices)

    for i in range(length - 1):
        current_index = pan_indices[i]
        next_index = pan_indices[i + 1]

        move(pi, SERVO_PAN_PIN, pan_start_sequence[current_index])
        await asyncio.sleep(random.uniform(0.15, 0.35))  # random short pause

        move(pi, SERVO_PAN_PIN, pan_start_sequence[next_index])
        await asyncio.sleep(random.uniform(0.4, 0.7))  # random longer pause

        # Randomize how many headbang cycles this time
        cycles = random.randint(1, len(headbang_tilts)//2)
        for _ in range(cycles):
            for start, end in headbang_tilts:
                move(pi, SERVO_TILT_PIN, start)
                await asyncio.sleep(random.uniform(0.1, 0.2))
                move(pi, SERVO_TILT_PIN, end)
                await asyncio.sleep(random.uniform(0.1, 0.2))

    # Randomized tilt drops with checks
    for _ in range(length - 1):
        tilt_drop += random.randint(50, 160)
        if tilt_drop >= 1600:
            break
        if allow_tilt(tilt_drop):
            move(pi, SERVO_TILT_PIN, tilt_drop)
            await asyncio.sleep(random.uniform(0.15, 0.3))

    # Return to center and some final random pans
    move(pi, SERVO_PAN_PIN, 1000)
    await asyncio.sleep(0.5)

    for pos in random.sample([600, 800, 1000], 3):
        move(pi, SERVO_PAN_PIN, pos)
        await asyncio.sleep(random.uniform(0.15, 0.4))
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
        time.sleep(0.1)
        print('move pan')
        pi.set_servo_pulsewidth(SERVO_PAN_PIN, 1000)
        time.sleep(0.1)

        # Smooth left and right sweeps
        
        dance(pi)
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