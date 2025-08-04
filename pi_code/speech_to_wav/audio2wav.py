import pyaudio
import wave
import numpy as np
import time
import audioop
from pynput import keyboard
import threading

# Parameters
THRESHOLD = 500    # Depends on Mic Sensitivity for 'silence'
SILENCE_DURATION = 2
CHUNK = 1024 # Buffer Size
FORMAT = pyaudio.paInt16 # 16 bit wave
CHANNELS = 2  
RATE = 16000
SECONDS_BEFORE_RECORDING = 10
filename = 'base_recording.wav'


stop_recording = False # global flag yo

def is_silent(data): 
    rms = audioop.rms(data, 2) # two bytes per sample
    return rms < THRESHOLD
    
def generate_name():
    timestamp = time.strftime("%Y_m_%d_H_%M_%S")
    return f"recording_{timestamp}.wav"
    
def record():
    global stop_recording
    stop_recording = False
    
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        info = audio.get_device_info_by_index(i)
        if info.get('maxInputChannels') > 0:
            print(f"input device: {i} - {info['name']}" ) 
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input_device_index=2,input=True, frames_per_buffer=CHUNK, start=False)
    stream.start_stream()
    
    
    
    
    print('Actively Recording')
    
    frames = []
    silence_start = None
    
    
    
    for _ in range(0, int(RATE / CHUNK * SECONDS_BEFORE_RECORDING)):
        data =stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        
        if is_silent(data):
            print('silence true')
            silence_start = time.time()
            if time.time() - silence_start > SILENCE_DURATION:
                print('you too quiet yo') # timer isn't working
        else:
            print('i can hear u')
    # Clean up Crew
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    # Save Recording
    filename = generate_name()
    with wave.open(f'recordings/{filename}', 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        
    print(f'Saved Recording as {filename}')
    print('press SPACEBAR to rerecord!')
    
def on_press(key):
    global stop_recording
    if key == keyboard.Key.space:
        record()
    elif hasattr(key, 'char') and key.char == 'w':
        print('W PRESSED STOP RECORDING')
        stop_recording = True 
        
        
if __name__ == "__main__":
      while True:
          user_input = input("\nPress [t] to survailance or [q] to quit or just 'ctrl c' ya savage!: ").strip().lower()

          if user_input == 'q':
            break

          if user_input == 't':
              record()
