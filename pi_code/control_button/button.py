import RPi.GPIO as GPIO
import time
import sys
import asyncio

# Define the GPIO pin connected to the button
BUTTON_PIN = 16



# Initialize the pushbutton pin as an input with a pull-up resistor
# The pull-up input pin will be HIGH when the switch is open and LOW when the switch is closed.
def initButton():
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# isButtonPressed
def isButtonPressed():
    return GPIO.input(BUTTON_PIN)

async def play_output_blocking(file_path):
    print("🎧 Playing response...")

    process = await asyncio.create_subprocess_exec("aplay", file_path)
    await process.wait()
    print("🎧 Playback finished.")

# Must create an audio stop_event
async def kill_switch_watcher(kill_event, pi):
    while True:
        if pi.read(BUTTON_PIN) == 1:  
            print("Kill switch pressed! Shutting down...")
            # Cancel all tasks except this one
            kill_event.set()
            
            
            
            for task in asyncio.all_tasks():
                if task is not asyncio.current_task():
                    task.cancel()
            await play_output_blocking('presets/easter_eggs/tube_time.wav')
          
            return  # exits the watcher
        await asyncio.sleep(0.05)  # check 20x/sec
