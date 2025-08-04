
import RPi.GPIO as GPIO
from time import sleep

# Constants
servo_tilt_pin = 12
servo_head_pin = 32 # physical pin 12 == GPIO18

def init_servos():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(servo_tilt_pin, GPIO.OUT)
    GPIO.setup(servo_head_pin, GPIO.OUT)

    pwm_tilt = GPIO.PWM(servo_tilt_pin, 50)  # 50 Hz for servos
    pwm_head = GPIO.PWM(servo_head_pin, 50)  # 50 Hz for servos
    
    pwm_tilt.start(7.5)                 # centre position (≈1.5 ms pulse)
    pwm_head.start(7.5)
    return pwm_tilt, pwm_head



def move_servo(pwm_tilt, pwm_head, x, y):
    try:
        # Test catching pwm_tilt and pwm_head must be correct objects,
        # Must map the boundaries of the duty cycle
        
        print(f"Moving to X: {x}, Y: {y}")
        pwm_tilt.ChangeDutyCycle(x)
        pwm_head.ChangeDutyCycle(y)
        sleep(0.5)
    except KeyboardInterrupt:
        GPIO.cleanup()
        
        



if __name__ == "__main__":
    
    try:
        pwm_tilt, pwm_head = init_servos()
        sleep(1)
        for i in range(0, 10, 2):  # from 0 to 58, step by 2
            move_servo(pwm_tilt, pwm_head, i, i)
            sleep(1.5)

        
        
    finally:
        print('Running clean up')
        pwm_tilt.stop()
        pwm_head.stop()
        GPIO.cleanup()



GPIO.cleanup()


    


    
