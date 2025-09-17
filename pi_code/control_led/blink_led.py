import pigpio
import time
import asyncio

LED_RED_PIN = 24
LED_GREEN_PIN = 25

# function to get current time in milliseconds
def millis():
    return time.perf_counter_ns() // 1000000

# Initialize pigpio and set up pins
def init_led(pi):
    print("Initialise LED Pins")
    if not pi.connected:
        raise RuntimeError("Could not connect to pigpio daemon. Is it running?")
    
    pi.set_mode(LED_RED_PIN, pigpio.OUTPUT)
    pi.set_mode(LED_GREEN_PIN, pigpio.OUTPUT)

    pi.write(LED_RED_PIN, 0)    # Start LOW
    pi.write(LED_GREEN_PIN, 0)  # Start LOW

def enable_led(pin, pi):
    pi.write(pin, 1)

def disable_led(pin, pi):
    pi.write(pin, 0)

    
    

    
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
                    pi: pigpio.pi,
                    blink_interval_ms: int,
                    stop_event: asyncio.Event) -> None:
    """
    Blink `pin` every `blink_interval_ms` milliseconds until `stop_event` is set.
    """
    led_state = 0  # 0 = LOW, 1 = HIGH
    last = millis()

    try:
        while not stop_event.is_set():
            now = millis()
            if (now - last) >= blink_interval_ms:
                led_state = 1 - led_state  # toggle 0/1
                pi.write(pin, led_state)
                last = now
            await asyncio.sleep(0.005)  # don't block loop
    finally:
        pi.write(pin, 0)  # ensure LED is off
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
#     pi = pigpio.pi()
#     init_led(pi)
#     stop_green_blink = asyncio.Event()
#     #stop_red_blink = asyncio.Event()
#     # Start LED blinker
#     green_blinker = asyncio.create_task(blink_led(pin=LED_GREEN_PIN,
#                                             pi=pi,
#                                             blink_interval_ms=500,
#                                             stop_event=stop_green_blink))
#     
#     # red_blinker = asyncio.create_task(blink_led(pin=LED_RED_PIN,
# #                                                 pi=pi,
# #                                             blink_interval_ms=700,
# #                                             stop_event=stop_red_blink))
#     await green_blinker
#     #await red_blinker# wait for task to finish cleanly
# 
#     # --- Start the real work (LLM call) in parallel ---
#     result = await run_llm()
# 
#     # LLM finished: stop blinking
#     stop_green_blink.set()
#     #stop_red_blink.set()
#     
#     print('enable red and green')
#     
#     time.sleep(2)
#     enable_led(LED_RED_PIN, pi)
#     # enable_led(LED_RED_PIN)
#     
#     # print(result)
#     time.sleep(2)
#     print('disable leds (green first)')
#     disable_led(LED_RED_PIN, pi)
#     time.sleep(1)
#     disable_led(LED_RED_PIN, pi)
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
# 
#         asyncio.run(main())
#     finally:
#         print('cleaning up')
#      

# 
# 
# gpio.cleanup()

