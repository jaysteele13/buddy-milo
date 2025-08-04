import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import playsound
import os


# Code now works, must make I/O device compatible, then we can start doing camera looking.

# After camera looking we can start doing LEDs Simultaneously with main brain and functioning

local_prefix = "http://127.0.0.1:8000"
server_prefix = "http://192.168.4.39:8000"

prefix = server_prefix

API_KEY = "pi_is_awesome"
AUDIO_FILE = "audio.wav"
TTS_OUTPUT = "myOutput.wav"

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



# === Transcribe via /transcribe ===
def transcribe_audio():
    print("🧠 Transcribing...")
    url = f"{prefix}/transcribe/"
    with open(AUDIO_FILE, 'rb') as f:
        response = requests.post(
            url,
            headers={"x-api-key": API_KEY},
            files={"file": f}
        )
    response.raise_for_status()
    print(response.json()["transcription"])
    return response.json()["transcription"]


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


# === MAIN FLOW ===
if __name__ == "__main__":

    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nWelcome to Milo, sarcastic surf buddy dude! 🌊")
    while True:

      user_input = input("\nPress [t] to speak or [q] to quit or just 'ctrl c' ya savage!: ").strip().lower()

      if user_input == 'q':
        break

      if user_input == 't':
        receive_prompt()
        sentence = transcribe_audio()
        new_sentence = process_personality(sentence)
        synthesize_speech(new_sentence)
        play_output(TTS_OUTPUT)
        os.system('cls' if os.name == 'nt' else 'clear')
      else:
          print('bitch give me something real!')