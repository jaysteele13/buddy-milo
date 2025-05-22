# V1

# from fastapi import FastAPI, File, UploadFile, HTTPException, Header
# import whisper
# import os
# import tempfile
# from fastapi.responses import JSONResponse

# from dotenv import load_dotenv
# load_dotenv()

# app = FastAPI()

# key = os.getenv('API_KEY')
# print(key)

# # Load whisper model (tiny for speed)
# model = whisper.load_model("models/tiny.pt", device="cpu")

# # Max file size: 10 MB (adjust if needed)
# MAX_FILE_SIZE_MB = 10

# @app.post("/transcribe")
# async def transcribe(file: UploadFile = File(...),
#                      x_api_key: str = Header(...)):
    
#     # auth
#     print(key)
#     if x_api_key != key:
#         raise HTTPException(status_code=401, detail='Invalid API Key Yo!')

#     # 1. Check file extension
#     if not file.filename.lower().endswith(".wav"):
#         raise HTTPException(status_code=400, detail="File must be a .wav format")

#     # 2. Save to temp file
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
#             contents = await file.read()
#             if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
#                 raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
#             tmp.write(contents)
#             tmp_path = tmp.name
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to process file")

#     try:
#         # 3. Load and process audio
#         audio = whisper.load_audio(tmp_path)
#         audio = whisper.pad_or_trim(audio)
#         mel = whisper.log_mel_spectrogram(audio).to(model.device)

#         # 4. Decode
#         options = whisper.DecodingOptions()
#         result = whisper.decode(model, mel, options)
#         transcription = result.text.strip()

#         if not transcription:
#             raise HTTPException(status_code=404, detail="No speech found in audio.")

#         return JSONResponse(content={"transcription": transcription})

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

#     finally:
#         # 5. Clean up temp file
#         if os.path.exists(tmp_path):
#             os.remove(tmp_path)


#V2

from fastapi import FastAPI, File, UploadFile, HTTPException, Header
import os
import tempfile
import subprocess
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
API_KEY = os.getenv("API_KEY")


# Path to whisper.cpp binary and model
WHISPER_CPP_BINARY = "./whisper.cpp/build/bin/whisper-cli"
MODEL_PATH = "./whisper.cpp/models/ggml-tiny.en.bin"

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...),
                     x_api_key: str = Header(...)):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="Only .wav files supported")

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            tmp.write(contents)
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


        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr)

        with open("output.txt", "r") as f:
            transcription = f.read().strip()
        

        if not transcription:
            raise HTTPException(status_code=404, detail="No speech found")
        
        return JSONResponse(content={"transcription": transcription})

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists("output.txt"):
            os.remove("output.txt")

