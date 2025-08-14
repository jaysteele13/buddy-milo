import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import playsound
import os
import pyaudio
import wave
import time
import pigpio
import audioop
import threading
import re
import random
import sys
import jellyfish
import RPi.GPIO as gpio
import asyncio
from picamera2 import Picamera2
from chatbot.use_brainV3 import transcribe_audio, process_personality, synthesize_speech, SERVER_NOT_ON, SERVER_ERROR
from control_led.blink_led import init_led, enable_led, disable_led, blink_led, LED_RED_PIN, LED_GREEN_PIN
from face_tracking.track import sentry_sweepV4, sentry_sweepV3, SERVO_TILT_PIN, SERVO_PAN_PIN, track_faceV2, process_frame, draw_results_and_coord
from control_audio.control_audio import find_and_think, pick_random_file, play_audio, play_output_blocking
from control_servos.controlV2 import dance
from activation_word.activation import hasMilo
from control_button.button import kill_switch_watcher, initButton


local_prefix = "http://127.0.0.1:8000"
server_prefix = "http://192.168.4.39:8000"

prefix = server_prefix

API_KEY = "pi_is_awesome"
AUDIO_FILE = "audio.wav"
TTS_OUTPUT = "myOutput.wav"



# Microphone Configuration Variables
THRESHOLD = 480    # Depends on Mic Sensitivity for 'silence'
SILENCE_DURATION = 3
CHUNK = 1024 # Buffer Size
FORMAT = pyaudio.paInt16 # 16 bit wave
CHANNELS = 2
RATE = 16000
SECONDS_BEFORE_RECORDING = 5
stop_recording = False # global flag yo
has_voice_activity = False

async def erase_recordings(filename='recording*'):
    recording_dir = 'chatbot/recordings'
    
    # Ensure the recordings directory exists
    os.makedirs(recording_dir, exist_ok=True)

    place_of_recordings = f"{recording_dir}/{filename}"
    command = f"rm {place_of_recordings}"
    
    file_count = len([
        name for name in os.listdir(recording_dir) 
        if os.path.isfile(os.path.join(recording_dir, name))
    ])
    
    if file_count > 0:
        process = await asyncio.create_subprocess_shell(command)
        await process.wait()
    else:
        return

    

def receive_prompt(duration_seconds=5, sample_rate=16000):
    print(f"🎤 Recording for {duration_seconds} seconds...")

    recording = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='int16'
    )
    sd.wait()  # Wait for recording to finish
    
    wav.write(AUDIO_FILE, sample_rate, recording)
    print(f"✅ Audio saved to {AUDIO_FILE}")

def is_silent(data): 
    rms = audioop.rms(data, 2) # two bytes per sample
    return rms < THRESHOLD
    
def generate_name():
    timestamp = time.strftime("%Y_m_%d_H_%M_%S")
    return f"recording_{timestamp}.wav"

def listen_for_prompt():
    
    # Dirty Global Variables
    global stop_recording
    stop_recording = False
    
    global has_voice_activity
    has_voice_activity = False
    
    # Config for Microphone
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info.get('maxInputChannels') > 0:
            print(f"input device: {i} - {info['name']}" ) 
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input_device_index=2,input=True, frames_per_buffer=CHUNK, start=False)
    stream.start_stream()
    
    
    
    
    print('Actively Recording')
    
    frames = []
    silence_start = 0
    collecting = False # collecting audio frames
    
    start_time = time.time()
    max_total_duration = 30  # seconds — maximum cap
    INITIAL_DISCARD_DURATION = 0.2  # seconds to skip at start to avoid feedback
    discard_start_time = start_time
    discarding = True

    while True:
        # must check for kill frame for button
        # Skip initial noisy frames
        if discarding:
            if time.time() - discard_start_time < INITIAL_DISCARD_DURATION:
                
                continue
            else:
                discarding = False
                print("Starting real recording...")
        # Check max recording cap
       
        if time.time() - start_time > max_total_duration:
            print("Max recording time reached.")
            break

        data = stream.read(CHUNK, exception_on_overflow=False)

        if not is_silent(data):
            # ensure there is a .5 second gap to avoid false reading on start up (feedback)
            print("Heard something.")
            frames.append(data)
            silence_start = 0
            has_voice_activity = True
        else:
            print("Silence...")
            frames.append(data)
            if has_voice_activity:
                if silence_start == 0:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION:
                    print("Silence too long. Ending recording.")
                    break
            else:
                # Haven’t heard anything yet — give more time
                if time.time() - start_time > SECONDS_BEFORE_RECORDING:
                    print("Initial silence timeout.")
                    break

    # Clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save only if voice detected
    if has_voice_activity:
        filename = generate_name()
        with wave.open(f'chatbot/recordings/{filename}', 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        print(f"Saved Recording as {filename}")
        return f'chatbot/recordings/{filename}'
    else:
        print("No speech detected.")
        return '[BLANK]'
    

    
async def play_output_with_face_tracking(file_path, playing_output, stop_face_tracking):
    print("🎧 Playing response...")
    playing_output.set()  # Playback has started

    process = await asyncio.create_subprocess_exec("aplay", file_path)
    await process.wait()

    stop_face_tracking.set()
    playing_output.clear()  # Playback has ended
    print("🎧 Playback finished.")


def hasSquareOrBracket(sentence):
    return bool(re.search(r'[\[\(]', sentence))

def stopListening(sentence):
    return bool(re.search(r'stop listening', sentence, re.IGNORECASE))

def hasDiscoBiscuits(sentence):
    return bool(re.search(r'\b(disco biscuits|disco|biscuits)\b', sentence, re.IGNORECASE))

def hasDropBeat(sentence):
    return bool(re.search(r'\b(drop a beat|give me a beat|a beat|the beat|the bit|drop, beat|beat)\b', sentence, re.IGNORECASE))

def hasDance(sentence):
    return bool(re.search(r'\b(boogie|dance|jiggy|slice the kebab|groovy)\b', sentence, re.IGNORECASE))

# CREATE FUNCTION TO SAY SERVER ISN@T TURNED ON!


# === MAIN FLOW ===
def setup_camera():
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={'format':'XRGB8888', 'size': (640, 480)})
        picam2.configure(config)
        picam2.start()
        return picam2
    except RuntimeError as e:
        print("Camera failed to initialize:", e)
        
    
# Make function that does face tracking between listening periods
async def face_repositioning(pi, cam, pan_angle, tilt_angle):
    error_x = 0
    error_y = 0

  
    print('look for face')
    frame = cam.capture_array()
    _, face_locations, face_names = process_frame(frame)

    if face_locations:
      
        print('Found a Face in Repositioning')
        x, y = draw_results_and_coord(face_locations, face_names)
        error_x, error_y, pan_angle, tilt_angle = await track_faceV2(
            pi, x, y, error_x, error_y, pan_angle, tilt_angle
        )
        # If found a face return True face found
        return True
    return False




async def face_tracking(pi, cam, stop_event, pan_angle, tilt_angle):
    error_x = 0
    error_y = 0
    last_face_seen_time = None
    
    while not stop_event.is_set():
        current_time = time.monotonic()
        frame = cam.capture_array()
        _, face_locations, face_names = process_frame(frame)

        if face_locations:
          
            last_face_seen_time = current_time
            x, y = draw_results_and_coord(face_locations, face_names)
            error_x, error_y, pan_angle, tilt_angle = await track_faceV2(
                pi, x, y, error_x, error_y, pan_angle, tilt_angle
            )

        await asyncio.sleep(0.05)  # yield control

    return last_face_seen_time

async def process_prompt_and_reposition(pi, picam2, pan_angle, tilt_angle, face_lost, face_lost_threshold, face_found_event):
 
    filename = await asyncio.to_thread(listen_for_prompt)
    face_found = await face_repositioning(pi, picam2, pan_angle, tilt_angle)

    if not face_found:
        face_lost += 1
        print(f'adding facelost: {face_lost}')
    else:
        face_lost = 0

    if face_lost >= face_lost_threshold:
        print('return to sentry mode!')
        face_found_event.clear()
        return '[SENTRY]', face_lost  # special signal

    return filename, face_lost


async def main():
    
    # Clear Screen
    # os.system('cls' if os.name == 'nt' else 'clear')
    
    
    # Init Camera
    picam2 = await asyncio.to_thread(setup_camera)
    
    # Allow Initialisation
    await asyncio.sleep(0.2)
    # Clear Recordings on Start up
    await erase_recordings()
    
    # Global Time Managment
    last_face_seen_time = None
    
    # Async Event for Killing Music based off of button
    kill_event = asyncio.Event()
    
    
    
    # Async Events for LED Control
    stop_green_blink = asyncio.Event()
    stop_red_blink = asyncio.Event()
    
    # Async Events for Thinking music
    stop_thinking_music = asyncio.Event()
    stop_buffering_music = asyncio.Event()
    
    stop_easter_egg = asyncio.Event()
    
     # States for Leds
    # 1. Searching - RED blinking Light
    # 2. Listening - RED static Light
    # 3. Thinking - GREEN blinking light
    # 4. Speaking - GREEN static light
    
    # Start LED blinker 1. SEARCHING
    red_blinker = asyncio.create_task(blink_led(pin=LED_RED_PIN,
                                            blink_interval_ms=500,
                                            stop_event=stop_red_blink))
    
    # Sentry and Face Tracking Events
    stop_face_tracking = asyncio.Event()
    face_found_event = asyncio.Event()
    playing_output = asyncio.Event()
    
    
    # Configure Pigmoid Servo Control
    pi = pigpio.pi()
    pi.set_servo_pulsewidth(SERVO_TILT_PIN, 1150)
    pi.set_servo_pulsewidth(SERVO_PAN_PIN, 600)
    
    if not pi.connected:
        raise RuntimeError("Failed to connect to pigpio daemon")
    
    # Init kill Switch
    # asyncio.create_task(kill_switch_watcher(kill_event, pi))
    
    
    
    # On start up -> Start Sentry Sweep
    x, y, pan_angle, tilt_angle = await asyncio.create_task(sentry_sweepV4(pi, picam2, face_found_event))
    
    

    # ---[VARIABLES]---
    # Face tracking Variables
    error_x = 0
    error_y = 0
    face_tracking_task = None
    return_to_sentry = False
    
    

    
    # Timer Variables
    attention_span = 5 # Attention_span in seconds
    
    # Listening Variables
    filename = '[BLANK]'
    
    # Face Lost threshold
    face_lost = 0
    face_lost_threshold = 3
    
    # Chatbot variables
    sentence = None
    miloRequested = False
    wasRude = False

    
   
   
    try:
        print("\nWelcome to Milo, sarcastic surf buddy dude! 🌊")
        # Enter the Event Loop
        while True:

          await asyncio.sleep(0.1)  # 👈 Important! Per cycle to main CPU usage!
          current_time = time.monotonic() # To do non-blocking timers
          
          # Sentry Finds Face.
          if face_found_event.is_set():
            return_to_sentry = False
            
            # Start Face Tracking in a different core
            stop_face_tracking.clear()
            
            
            
            # --- RED LIGHT LOGIC 2. Listening ---
            # As Face Tracking is enabled - Speech is allowed, therefore stop blinking Red LED
            print('STOP RED LED BLINKING')
            stop_red_blink.set()
            await red_blinker
            
            
            print("now listening - say 'stop listening' to stop")
            while True:
                print('ENABLE REDLED')
                enable_led(LED_RED_PIN)
            
                filename, face_lost = await process_prompt_and_reposition(pi, picam2, pan_angle, tilt_angle, face_lost, face_lost_threshold, face_found_event)

                if filename == '[SENTRY]':
                    return_to_sentry = True
                    break

                if filename != '[BLANK]':
                    break  # valid filename received

                print(f"here is filename: {filename}")

            if face_lost >= face_lost_threshold:
                sentence = '[BLANK]'
            else:
                # 3. Thinking
                disable_led(LED_RED_PIN)
                stop_green_blink.clear()  # Ensure the blink loop can run
                stop_green_blink = asyncio.Event()
                green_blinker = asyncio.create_task(blink_led(
                    pin=LED_GREEN_PIN,
                    blink_interval_ms=500,
                    stop_event=stop_green_blink
                ))
                
                # Buffering Logic Here
                # -- Either Buffering Logic (65%) or Insult (35%)
                stop_buffering_music.clear()
                stop_buffering_music = asyncio.Event()
                
                
                INSULT_CHANCE = 33  # percent
                RUDE_CHANCE = 10
                BUFFERING_CHANCE = 50
                SILENCE_CHANCE = 60
                
                silence_key = 'silence'
                
                PRESETS = {
                    'presets/insults': INSULT_CHANCE,
                    'presets/insults/rude': RUDE_CHANCE,
                    'presets/buffering': BUFFERING_CHANCE,
                     silence_key: SILENCE_CHANCE
                }

                preset = random.choices(
                    population=list(PRESETS.keys()),
                    weights=list(PRESETS.values()),
                    k=1
                )[0]

                if not (preset == silence_key):
                    buffer_music = asyncio.create_task(find_and_think(preset, stop_buffering_music, kill_event))
                
                    sentence = await asyncio.to_thread(transcribe_audio, filename)
                    stop_green_blink.set()
                    await green_blinker
                    
                    # Stop buffering music
                    stop_buffering_music.set()
                    await buffer_music
                else:
                    sentence = await asyncio.to_thread(transcribe_audio, filename)
                    stop_green_blink.set()
                    await green_blinker
                    
                if preset == 'presets/insults/rude':
                    wasRude = True
                else:
                    wasRude = False
                    
                
            
            # Take through Activation Logic first
            miloRequested, word_found, sentence = hasMilo(sentence)
            print(f'Activation word found?: {word_found}')
            
            # Error checks
            if sentence == SERVER_NOT_ON:
                await play_audio('presets/error/server_not_on.wav', kill_event=kill_event)
            elif sentence == SERVER_ERROR:
                await play_audio('presets/error/server_error.wav', kill_event=kill_event)
                

            
            elif miloRequested and not wasRude:
            # Determine Easter eggs and Early Cancels!
                if hasSquareOrBracket(sentence) or (sentence is None) or (sentence == ''):
  
                    print(f'inaudible stop brain function - Removing that file {filename}')

                elif hasDiscoBiscuits(sentence):
                    # play output without async determiner
                    enable_led(LED_GREEN_PIN)  # Solid green during speech
                    # await play_output_blocking('presets/easter_eggs/disco_biscuits.wav')
                    await play_audio('presets/easter_eggs/disco_biscuits.wav', kill_event=kill_event)
                    disable_led(LED_GREEN_PIN)  # Solid green during speech
                elif hasDropBeat(sentence):
                    # -- CONTINUE HERE REUSE BUFFER MUSIC FOR CLARITY? MAKE GENRIC EASTER EGG EVENT?? -
                    enable_led(LED_GREEN_PIN)
                    # play random file from easter_eggs/beats with face tracking!
                    if face_tracking_task is None or face_tracking_task.done():
                        stop_face_tracking.clear()  # Ensure it can run again
                        face_tracking_task = asyncio.create_task(
                            face_tracking(pi, picam2, stop_face_tracking, pan_angle, tilt_angle)
                        )
                        
                    
                    # give easter/beat file for this
                    random_beat_file = pick_random_file('presets/easter_eggs/beats')
                    # play_egg = asyncio.create_task(play_output_with_face_tracking(random_beat_file, playing_output, stop_face_tracking))
                 
                    play_egg = asyncio.create_task(play_audio(random_beat_file, playing_output=playing_output, stop_face_tracking=stop_face_tracking, kill_event=kill_event))

                    # Wait until speech is done before listening again
                    await play_egg
                    if playing_output.is_set():
                        print("⏳ Waiting for playback to finish...")
                        await playing_output.wait()
                        
                    
                    
                    disable_led(LED_GREEN_PIN)
                elif hasDance(sentence):
                    # ALMOST WORKS BUT DOESNT CANCEL AUDIO!
                    playing_output.clear()
                    enable_led(LED_GREEN_PIN)
                    random_song_file = pick_random_file('presets/easter_eggs/songs')
                     
                    play_egg = asyncio.create_task(play_audio(random_song_file, stop_event=playing_output, kill_event=kill_event))
                    dance_task = asyncio.create_task(dance(pi))

                    await dance_task  # Wait for dance to finish 20-30 second dance

                    # After dance ends, cancel/stop playback
                    print('cancel music')
                    playing_output.set()
                    await play_egg

                    disable_led(LED_GREEN_PIN)
                    # Assume eancing you have lost face
                    face_lost = face_lost_threshold
                    

                elif stopListening(sentence):
                    # Break from Listening Loop
                    break
                else:
                    # Face Lost will probably be found reset face found counter
                    face_lost = 0
                

                    # --- THINKING ---
                    # This Will either Randomly insult the person or play thinking music! Randomiser Again
                    #
                    stop_thinking_music.clear()
                    stop_thinking_music = asyncio.Event()
                    think_music = asyncio.create_task(find_and_think('presets/thinking', stop_thinking_music, kill_event))
    #                 
                    
                    # --- LED LOGIC 3.  ---
                    print('stop red led static and start green blink')
                    disable_led(LED_RED_PIN)  # Now using brain -> Green LED
                    stop_green_blink.clear()  # Ensure the blink loop can run
                    stop_green_blink = asyncio.Event()
                    green_blinker = asyncio.create_task(blink_led(
                        pin=LED_GREEN_PIN,
                        blink_interval_ms=500,
                        stop_event=stop_green_blink
                    ))

                    # Start face tracking in background if not already running
                    if face_tracking_task is None or face_tracking_task.done():
                        stop_face_tracking.clear()  # Ensure it can run again
                        face_tracking_task = asyncio.create_task(
                            face_tracking(pi, picam2, stop_face_tracking, pan_angle, tilt_angle)
                        )

                    # Apply LLM Personality
                    print(f'trying transcribed SENTENCE: [{sentence}]')
                    # Remove Activation word from sentence
                    new_sentence = await asyncio.to_thread(process_personality, sentence)
                    
                    # --- 3. End of Thinking ---

                    # Synthesize speech (runs in thread since it's blocking)
                    await asyncio.to_thread(synthesize_speech, new_sentence)

                    # Stop Green blink - 4. SPEAKING — Milo is about to talk
                    stop_green_blink.set()
                    await green_blinker
                    print('stop green blink led ')
                    enable_led(LED_GREEN_PIN)  # Solid green during speech
                    print('start green led static')
                    
                    # Stop Thinking Music
                    stop_thinking_music.set()
                    await think_music
    #                 
                  

                    # Play the TTS output (non-blocking task)
                    play_task = asyncio.create_task(play_audio(TTS_OUTPUT, playing_output=playing_output, stop_face_tracking=stop_face_tracking, kill_event=kill_event))
                    # play_task = asyncio.create_task(play_output_with_face_tracking(TTS_OUTPUT, playing_output, stop_face_tracking))
                
                    

                    # Wait until speech is done before listening again
                    await play_task
                    if playing_output.is_set():
                        print("⏳ Waiting for playback to finish...")
                        await playing_output.wait()
                    disable_led(LED_GREEN_PIN)  # Turn off once speech starts
                
                                  
                
                
             # Time to Process with Brain
                
            
                    
                    
     
              
          if return_to_sentry:
            print(f"Lost face for {attention_span} seconds, resuming sweep.")
            face_found_event.clear()
            await erase_recordings()
            
            # Stage 1. Searching -LED LOGIC -
            face_lost = 0
            print('start red led blink')
            stop_red_blink.clear() 
            stop_red_blink = asyncio.Event()
            red_blink_task = asyncio.create_task(blink_led(LED_RED_PIN, 500, stop_red_blink))
            
            x, y, pan_angle, tilt_angle = await asyncio.create_task(sentry_sweepV4(pi, picam2, face_found_event))
            
    finally:
        # Clean Up Crew
        print('Cleaning Up Servo and Camera')
        
        pi.set_servo_pulsewidth(SERVO_TILT_PIN, 0)
        pi.set_servo_pulsewidth(SERVO_PAN_PIN, 0)
        pi.stop()
        picam2.stop()
        



if __name__ == "__main__":
    
    try:
        # Init LED outside of Async Loop
        init_led()
        # init_button() # Dont init button happening in runner guarenteed.
        
        asyncio.run(main())
    except asyncio.CancelledError:
        print("Main loop cancelled.")
    finally:
        print('Cleaning Up LED')
        disable_led(LED_RED_PIN)
        disable_led(LED_GREEN_PIN)
        gpio.cleanup()
        



