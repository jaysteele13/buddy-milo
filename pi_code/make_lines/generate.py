import requests

server_prefix = "http://192.168.4.39:8000"

prefix = server_prefix

API_KEY = "pi_is_awesome"

def synthesize_speech(sentence, name):
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
        with open(name, 'wb') as f:
            f.write(response.content)
        print(f"🔊 Audio saved to {name}")
    else:
        raise Exception(f"Failed TTS: {response.text}")
    

if __name__ == "__main__":
    sentence = "target ackwired"
    name = 'robo-greet2.wav'
    
    synthesize_speech(sentence, name)
    