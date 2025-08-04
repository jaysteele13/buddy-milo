from fastapi import APIRouter, File, UploadFile, HTTPException, Header
import os
import tempfile
import subprocess
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()
API_KEY = os.getenv("API_KEY")


# Path to whisper.cpp binary and model

# Must use absolute paths as running from main.app!

# So would be below amend after dinner then can think about expanding to home server when all works!
WHISPER_CPP_BINARY = "./speech_to_text/whisper.cpp/build/bin/whisper-cli"
MODEL_PATH = "speech_to_text/whisper.cpp/models/ggml-base.en.bin"

@router.post("/")
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
            JSONResponse(content={"transcription": 'I do not understand what you just said'})
        
        return JSONResponse(content={"transcription": transcription})

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if os.path.exists("output.txt"):
            os.remove("output.txt")

