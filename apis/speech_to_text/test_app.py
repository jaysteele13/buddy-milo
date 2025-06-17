import os
import tempfile
import subprocess
import psutil

# Path to whisper.cpp binary and model
WHISPER_CPP_BINARY = "./whisper.cpp/build/bin/whisper-cli"
MODEL_PATH = "./whisper.cpp/models/ggml-tiny.en.bin"

def get_memory_usage_mb():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 ** 2)  # Convert bytes to MB
# Path to input WAV file
INPUT_FILE = "../../samples/test1.wav"

def transcribe_audio(input_path):
    tmp_path = None
    try:
        print(f"RAM before decoding: {get_memory_usage_mb():.2f} MB")
        # Copy the input file to a temp file (if needed for processing)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            with open(input_path, "rb") as source:
                tmp.write(source.read())
            tmp_path = tmp.name

        # Run whisper.cpp with subprocess
        result = subprocess.run(
            [ WHISPER_CPP_BINARY, 
             "-m", MODEL_PATH,
             "-f", tmp_path, 
             "-otxt", 
             "-of", "output"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"RAM DURING decoding: {get_memory_usage_mb():.2f} MB")

        if result.returncode != 0:
            print("Error during transcription:")
            print(result.stderr)
            return None

        # Read the result from output.txt
        with open("output.txt", "r") as f:
            transcription = f.read().strip()

        print("Transcription:")
        print(transcription)
        print(f"RAM After decoding: {get_memory_usage_mb():.2f} MB")
        return transcription

    finally:
        # Clean up temp and output files
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists("output.txt"):
            os.remove("output.txt")

if __name__ == "__main__":
    transcribe_audio(INPUT_FILE)
