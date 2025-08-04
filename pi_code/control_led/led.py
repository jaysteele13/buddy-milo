LED_RED_PIN = 23
LED_GREEN_PIN = 24

import RPi.GPIO as gpio
import time

# in pins 23 and 24

gpio.setmode(gpio.BCM)

gpio.setup(LED_RED_PIN, gpio.OUT, initial=gpio.LOW)
gpio.setup(LED_GREEN_PIN, gpio.OUT, initial=gpio.LOW)

gpio.output(LED_RED_PIN, gpio.HIGH)
gpio.output(LED_GREEN_PIN, gpio.LOW)

print("turn on LED please don't fry none ya")
time.sleep(1)
gpio.output(LED_RED_PIN, gpio.LOW)
gpio.output(LED_GREEN_PIN, gpio.HIGH)


time.sleep(1)
gpio.output(LED_RED_PIN, gpio.LOW)
gpio.output(LED_GREEN_PIN, gpio.LOW)


gpio.cleanup()