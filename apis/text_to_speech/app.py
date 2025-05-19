# Pseduo Code

# Configure Restful API using FastAPI with correct naming conventions -> save to README

# import whisper model locally (probably tiny) await the model prediction when code is brought in

# output the model output, have validation to give error if audio file is bad or incorrect

# Must ensure prompt is less than 30 seconds!!!!!!!

# Have rror logging if ram is used up

# Have error if other thing happened

# Error if server is down






# V1
# import whisper

# model = whisper.load_model('tiny')
# result = model.transcribe('test.wav', fp16=False)

# print(result['text'])

# output: Hello, my name is Jay and that's okay. You, my little. You, my little. Hey, what's going on you? What's the weather like? Hello.

# V2 - Working
# import whisper

# model = whisper.load_model('base')
# # result = model.transcribe('test.wav', fp16=False)

# # load audio to fit into 30 seconds
# audio = whisper.load_audio('../../samples/test1.wav')
# audio = whisper.pad_or_trim(audio)

# # Make log-Mel spectrogram and move to same device as model
# # Converting Audio analog to digital in a logarithmic way
# mel = whisper.log_mel_spectrogram(audio).to(model.device)

# # detect spoken language
# _, probs = model.detect_language(mel)
# print(f'Detected language: {max(probs, key=probs.get)}')

# # decode audio for string
# options = whisper.DecodingOptions()
# result = whisper.decode(model,mel,options)

# # Print String Result
# print(result.text)

# # with Tiny: Yes sir, watch the surf like, Donnellite, you mylo, you mylo, y
# # you mylo, you mylo. Hello, fun, Xbox. Cook, cool, yeah, yeah, that's the set man. Yeah, good luck, glasses, you mylo. You mylo, watch the surf like, watch the weather like.

# #with base
# # Yes sir, watch the surf like, Donnellite, you mylo, you mylo, you mylo, you mylo. Hello, fun, Xbox. Cook, cool, yeah, yeah, 
# # that's the set man. Yeah, good luck, glasses, you mylo. You mylo, watch the surf like, watch the weather like.



# V3 with ram usage monitoring!
import whisper
import psutil
import os

def get_memory_usage_mb():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 ** 2)  # Convert bytes to MB

# Monitor RAM before loading model
print(f"RAM Before loading model: {get_memory_usage_mb():.2f} MB")

# Change 'base' to 'tiny' to compare
model = whisper.load_model('models/tiny.pt', device="cpu")

print(f"RAM After loading model: {get_memory_usage_mb():.2f} MB")

# load audio to fit into 30 seconds
audio = whisper.load_audio('../../samples/test1.wav')
audio = whisper.pad_or_trim(audio)

# Make log-Mel spectrogram and move to same device as model
mel = whisper.log_mel_spectrogram(audio).to(model.device)

print(f"RAM After preprocessing audio: {get_memory_usage_mb():.2f} MB")

# detect spoken language
_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")

# decode audio for string
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)

print(f"RAM After decoding: {get_memory_usage_mb():.2f} MB")

# Print String Result
print(result.text)

# Base Ram: 800; Base superior in transcription
# Tiny Ram: 600; Tiny is better for RAM!
