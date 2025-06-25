import numpy as np
from onnxruntime import InferenceSession
import scipy.io.wavfile as wavfile
import json
import re
from pydub import AudioSegment
from text_to_speech.kokoro.kokoro import phonemize, tokenize

with open("text_to_speech/kokoro/config.json", "r") as f:
    config = json.load(f)


vocab = config["vocab"]

def phonemes_to_tokens(phonemes: str, vocab: dict) -> list[int]:
    tokens = []
    for char in phonemes:
        if char in vocab:
            tokens.append(vocab[char])
        else:
            print(f"[WARN] Unknown phoneme symbol: '{char}'")  # Optional
    return tokens

def insert_pauses(phoneme_str: str, pause_token="SP") -> str:
    result = []
    for token in phoneme_str.strip().split():
        result.append(token)
        if token in {".", ",", "!", "?", ";", ":"}:
            result.append(pause_token)
    return " ".join(result)


# did a pip install -q "misaki[en]"

dir_name = "text_to_speech/kokoro"
token_path = f"{dir_name}/tokenizer.json"
model_name = f"{dir_name}/model_q4.onnx"
voice_path = f"{dir_name}/bm_lewis.bin"


def chunk_text(text, max_tokens=510):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if not sentence:
            continue
        tentative = f"{current_chunk} {sentence}".strip()
        phonems = phonemize(tentative, 'b')
        token_count = len(phonemes_to_tokens(insert_pauses(phonems, pause_token=" "), vocab))
        if token_count <= max_tokens:
            current_chunk = tentative
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def text2speech(text):
    phonems = phonemize(text, 'b')

    tokens = tokenize(phonems)
    # Context length is 512, but leave room for the pad token 0 at the start & end

    # Context length is 512, but leave room for the pad token 0 at the start & end
    assert len(tokens) <= 510, len(tokens)

    # Style vector based on len(tokens), ref_s has shape (1, 256)
    voices = np.fromfile(voice_path, dtype=np.float32).reshape(-1, 1, 256)
    # ref_s = voices[len(tokens)]
    ref_s = voices[len(tokens)]  # use appropriate style vector

    # Add the pad ids, and reshape tokens, should now have shape (1, <=512)
    tokens = [[0, *tokens, 0]]

    sess = InferenceSession(model_name)

    audio = sess.run(None, dict(
        input_ids=tokens,
        style=ref_s,
    
        speed= np.array([1.0], dtype=np.float32),
    ))[0]

    # Save Audio file

    filename = 'audio.wav'
    wavfile.write(filename, 24000, audio[0])
    return filename

def generate_full_audio(text):
    audio = AudioSegment.silent(duration=0)
    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        print(f"▶️ Synthesizing chunk {i+1}/{len(chunks)}: {chunk}")
        filename = text2speech(chunk)
        segment = AudioSegment.from_wav(filename)
        audio += segment + AudioSegment.silent(duration=100)  # optional pause between sentences

    final_output = "final_output.wav"
    audio.export(final_output, format="wav")
    return final_output



