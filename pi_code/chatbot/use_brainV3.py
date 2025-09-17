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



local_prefix = "http://127.0.0.1:8000"
server_prefix = "http://192.168.4.39:8000"

prefix = server_prefix

API_KEY = "pi_is_awesome"
AUDIO_FILE = "audio.wav"
TTS_OUTPUT = "myOutput.wav"

SERVER_NOT_ON = '[SERVER_NOT_ON]'
SERVER_ERROR = '[SERVER_ERROR]'



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
        return "[SERVER_EEROR]"

    except Exception as e:
        print(f"❌ Unexpected error during transcription: {e}")
        return "[SERVER_NOT_ON]"


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



