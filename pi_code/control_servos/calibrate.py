# Calibrate
import time
import pigpio

pi = pigpio.pi()
if not pi.connected:
    exit()

servo_pan_pin = 18  # Your servo GPIO pin
servo_tilt_pin = 19  # Your servo GPIO pin

current_pin = servo_tilt_pin



# Try moving to various positions
for pulse in [500, 1000, 1500, 2000, 2500]:
    print(f"Moving to {pulse}us")
    pi.set_servo_pulsewidth(current_pin, pulse)
    time.sleep(1)

# Turn off
pi.set_servo_pulsewidth(current_pin, 0)
pi.stop()
