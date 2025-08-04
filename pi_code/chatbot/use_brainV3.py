import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import playsound
import os
import pyaudio
import wave
import time
import audioop
import threading
import re


# Code now works, must make I/O device compatible, then we can start doing camera looking.

# After camera looking we can start doing LEDs Simultaneously with main brain and functioning


# Next we must get the camera working and introduce threading so Milo Knows who he is talking to whilst
# communicating

# Get servos tuned properly

# introduce lights

# introduce other features like drop a beat, buzzer when thinking, array of 50 phrases that could be
#said about funny topics to give the illusion of greater intelligence

local_prefix = "http://127.0.0.1:8000"
server_prefix = "http://192.168.4.39:8000"

prefix = server_prefix

API_KEY = "pi_is_awesome"
AUDIO_FILE = "audio.wav"
TTS_OUTPUT = "myOutput.wav"



# Function to configure LED and enable them based on what stage the chatbot is in


# Recording with Cam Mic Parameters
THRESHOLD = 500    # Depends on Mic Sensitivity for 'silence'
SILENCE_DURATION = 3
CHUNK = 1024 # Buffer Size
FORMAT = pyaudio.paInt16 # 16 bit wave
CHANNELS = 2
RATE = 16000
SECONDS_BEFORE_RECORDING = 5
stop_recording = False # global flag yo
has_voice_activity = False

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
    global stop_recording
    stop_recording = False
    
    global has_voice_activity
    has_voice_activity = False
    
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
    collecting = False # collecting audio frames
    
    start_time = time.time()
    max_total_duration = 30  # seconds — maximum cap

    while True:
        # Check max recording cap
        if time.time() - start_time > max_total_duration:
            print("Max recording time reached.")
            break

        data = stream.read(CHUNK, exception_on_overflow=False)

        if not is_silent(data):
            print("Heard something.")
            frames.append(data)
            silence_start = None
            has_voice_activity = True
        else:
            print("Silence...")
            frames.append(data)
            if has_voice_activity:
                if silence_start is None:
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
        with wave.open(f'recordings/{filename}', 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        print(f"Saved Recording as {filename}")
        return f'recordings/{filename}'
    else:
        print("No speech detected.")
        return '[BLANK]'
    
    
# === Transcribe via /transcribe ===
def transcribe_audio(audio_file = AUDIO_FILE):
    print("🧠 Transcribing...")
    url = f"{prefix}/transcribe/"
    try:
        with open(audio_file, 'rb') as f:
            response = requests.post(
                url,
                headers={"x-api-key": API_KEY},
                files={"file": f}
            )
        response.raise_for_status()
        print(response.json()["transcription"])
        return response.json()["transcription"]
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 400:
            print("⚠️  400 Bad Request — Likely an invalid or corrupted audio file.")
        else:
            print(f"HTTP error occurred: {http_err} ({response.status_code})")
        return "[BLANK]"

    except Exception as e:
        print(f"❌ Unexpected error during transcription: {e}")
        return "[BLANK]"


# === Process via /personality ===
def process_personality(sentence):
    print("🧠 Applying personality...")
    url = f"{prefix}/personality/"
    response = requests.post(
        url,
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={"sentence": sentence}
    )
    response.raise_for_status()
    print(response.json()["personality"])
    return response.json()["personality"]


# === Convert via /text2speech ===
def synthesize_speech(sentence):
    print("🗣 Synthesizing speech...")
    url = f"{prefix}/text2speech/"
    response = requests.post(
        url,
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={"sentence": sentence}
    )

    if response.status_code == 200:
        with open(TTS_OUTPUT, 'wb') as f:
            f.write(response.content)
        print(f"🔊 Audio saved to {TTS_OUTPUT}")
    else:
        raise Exception(f"Failed TTS: {response.text}")


# === Play final output ===
def play_output(file_path):
    print("🎧 Playing response...")
    playsound.playsound(file_path, block=True)


def hasSquareOrBracket(sentence):
    return bool(re.search(r'[\[\(]', sentence))

def stopListening(sentence):
    return bool(re.search(r'stop listening', sentence, re.IGNORECASE))

# === MAIN FLOW ===
if __name__ == "__main__":

    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nWelcome to Milo, sarcastic surf buddy dude! 🌊")
    while True:

      user_input = input("\nPress [t] to speak for set time, [l] to actively listen or [q] to quit... or just 'ctrl c' ya savage!: ").strip().lower()

      if user_input == 'q':
        break

      if user_input == 't':
        receive_prompt()
        sentence = transcribe_audio()
        
        if hasSquareOrBracket(sentence):
            os.system('cls' if os.name == 'nt' else 'clear')
            print('inaudible stop brain function')
            
        else:
            new_sentence = process_personality(sentence)
            synthesize_speech(new_sentence)
            play_output(TTS_OUTPUT)
            os.system('cls' if os.name == 'nt' else 'clear')
      elif user_input == 'l':
        print("now listening - say 'stop listening' to stop")
        filename = '[BLANK]'
        while True:
            filename = listen_for_prompt()
            while filename == '[BLANK]':
                filename = listen_for_prompt()
                print(f"here is filename: {filename}")
            
            # check for [BLANK] if filename blank keep recording
            
            sentence = transcribe_audio(filename)
            
            if stopListening(sentence):
                break
            
            if hasSquareOrBracket(sentence):
                os.system('cls' if os.name == 'nt' else 'clear')
                print('inaudible stop brain function')
                
            else:
                new_sentence = process_personality(sentence)
                synthesize_speech(new_sentence)
                play_output(TTS_OUTPUT)
      else:
          print('bitch give me something real!')



