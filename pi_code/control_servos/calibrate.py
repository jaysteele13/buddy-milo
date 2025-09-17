# Calibrate
import time
import pigpio

pi = pigpio.pi()
if not pi.connected:
    exit()

servo_pan_pin = 18  # Your servo GPIO pin
servo_tilt_pin = 19  # Your servo GPIO pin

SERVO_PAN_MIN = 500
SERVO_PAN_MAX = 1200

SERVO_TILT_MIN = 800
SERVO_TILT_MAX = 1600

# Try moving to various positions - tilt
for pulse in [SERVO_PAN_MIN, SERVO_PAN_MAX]:
    print(f"Moving to pan {pulse}us")
    pi.set_servo_pulsewidth(servo_pan_pin, pulse)
    time.sleep(1)

# Turn off

pi.stop()
