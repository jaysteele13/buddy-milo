LED_RED_PIN = 23
LED_GREEN_PIN = 24

import RPi.GPIO as gpio
import time
import asyncio

# in pins 23 and 24

# function to get current time in milliseconds
def millis():
    return time.perf_counter_ns() // 1000000

# Set up pin mode
def init_led():
    print('Initialise LED Pins')
    gpio.setmode(gpio.BCM)
    gpio.setup(LED_RED_PIN, gpio.OUT, initial=gpio.LOW)
    gpio.setup(LED_GREEN_PIN, gpio.OUT, initial=gpio.LOW)
    
def enable_led(pin):
    gpio.output(pin, gpio.HIGH)

def disable_led(pin):
    gpio.output(pin, gpio.LOW)
    
    

    
# 
# def blink_led(pin, blink_interval = 500):
#     try:
#         previousTime = millis()
#         # blink state variables
#         led_state = gpio.LOW  # led_state used to set the LED
#         prev_button_state = gpio.LOW  # Will store the last time button was updated
#         while True:
#             # Check if it's time to blink the LED
#             currentTime = millis()
# 
#             if currentTime - previousTime >= blink_interval:
#                 # If the LED is off, turn it on, and vice-versa
#                 led_state = not led_state
# 
#                 # Set the LED with the led_state variable
#                 gpio.output(pin, led_state)
# 
#                 # Save the last time you blinked the LED
#                 previousTime = currentTime
# 
# 
#     except KeyboardInterrupt:
#         # Clean up GPIO on keyboard interrupt
#         gpio.cleanup()
        

async def blink_led(pin: int,
                    blink_interval_ms: int,
                    stop_event: asyncio.Event) -> None:
    """
    Blink `pin` every `blink_interval_ms` milliseconds until `stop_event` is set.
    """
    led_state = gpio.LOW
    last = millis()

    try:
        while not stop_event.is_set():
            now = millis()
            if (now - last) >= blink_interval_ms:
                led_state = not led_state
                gpio.output(pin, led_state)
                last = now
            # Don’t block the event loop – tiny sleep is enough
            await asyncio.sleep(0.005)
    finally:
        gpio.output(pin, gpio.LOW)  # make sure LED is off
        # leave general gpio.cleanup() to your global shutdown code

# main
async def run_llm():
    # Pretend this is the expensive call
    print('llm logic simulate')
    await asyncio.sleep(1)
    print('thinking real hard')
    await asyncio.sleep(1)
    print('found the leche') 
    await asyncio.sleep(1)
    # simulate LLM thinking for 4 s
    return "All done!"

# 
# async def main():
#     stop_green_blink = asyncio.Event()
#     stop_red_blink = asyncio.Event()
#     # Start LED blinker
#     green_blinker = asyncio.create_task(blink_led(pin=LED_GREEN_PIN,
#                                             blink_interval_ms=500,
#                                             stop_event=stop_green_blink))
#     
#     red_blinker = asyncio.create_task(blink_led(pin=LED_RED_PIN,
#                                             blink_interval_ms=700,
#                                             stop_event=stop_red_blink))
# #     await green_blinker
# #     await red_blinker# wait for task to finish cleanly
# 
#     # --- Start the real work (LLM call) in parallel ---
#     result = await run_llm()
# 
#     # LLM finished: stop blinking
#     stop_green_blink.set()
#     stop_red_blink.set()
#     
#     print('enable red and green')
#     
#     time.sleep(2)
#     enable_led(LED_GREEN_PIN)
#     enable_led(LED_RED_PIN)
#     
#     print(result)
#     time.sleep(2)
#     print('disable leds (green first)')
#     disable_led(LED_GREEN_PIN)
#     time.sleep(1)
#     disable_led(LED_RED_PIN)
#     
#     
#     # Plan is:
#     # Red On Green Off - ready to take command (listening)
#     # Red Blinking Green Off - looking for face
#     # Red Off Green On - Currently Speaking
#     # Red off Green Blinking - Currently Thinking
# 
# 
# if __name__ == "__main__":
#     try:
#         init_led()
#         asyncio.run(main())
#     finally:
#         print('cleaning up')
#         gpio.cleanup()
# 
# 
# 
# gpio.cleanup()

