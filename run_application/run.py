# A service which runs all services and can hit endpoints asynchronously and extract the purpose



# Feature
# # Say something for a prompt (wait for speak)


# # Function to accept audio into wav
# def recieve_prompt():
#     prompt = False
#     while prompt != True:
#         listen_to_audio()
#         if quiet:
#             prompt = True
#             audio = write_audio


# # Process this to text using endpoint hit - curl -X POST http://127.0.0.1:8000/transcribe/   -H "x-api-key: pi_is_awesome"   -F "file=@audio.wav"
# sentence = curl transcribe


# # Get this text then Process it in llm endpoint - curl -X POST http://127.0.0.1:8000/personality/   -H "x-api-key: pi_is_awesome"   -H "Content-Type: application/json"   -d '{"sentence": "im bored what should i do"}'
# new_sentence = curl personaility(sentence)


# # process this then finally put it into the text to speech endpoint curl -X POST http://127.0.0.1:8000/text2speech/   -H "x-api-key: pi_is_awesome"   -H "Content-Type: application/json"   -d '{"sentence": "im bored what should i do"}'   -o "myOutput.wav"

# new_audio = curl text2speech(new_sentence)

# # once recieved play the myOutput.wav

# play(new_audio)

import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests

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
    url = "http://127.0.0.1:8000/transcribe/"
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
    url = "http://127.0.0.1:8000/personality/"
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
    url = "http://127.0.0.1:8000/text2speech/"
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
    # wave_obj = sa.WaveObject.from_wave_file(file_path)
    # play_obj = wave_obj.play()
    # play_obj.wait_done()


# === MAIN FLOW ===
if __name__ == "__main__":
    receive_prompt()
    sentence = transcribe_audio()
    new_sentence = process_personality(sentence)
    synthesize_speech(new_sentence)
    play_output(TTS_OUTPUT)
