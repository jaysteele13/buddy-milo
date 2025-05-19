from fastapi import FastAPI, File, UploadFile, HTTPException, Header
import whisper
import os
import tempfile
from fastapi.responses import JSONResponse

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

key = os.getenv('API_KEY')
print(key)

# Load whisper model (tiny for speed)
model = whisper.load_model("models/tiny.pt", device="cpu")

# Max file size: 10 MB (adjust if needed)
MAX_FILE_SIZE_MB = 10

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...),
                     x_api_key: str = Header(...)):
    
    # auth
    print(key)
    if x_api_key != key:
        raise HTTPException(status_code=401, detail='Invalid API Key Yo!')

    # 1. Check file extension
    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=400, detail="File must be a .wav format")

    # 2. Save to temp file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(status_code=413, detail="File too large (max 10 MB)")
            tmp.write(contents)
            tmp_path = tmp.name
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process file")

    try:
        # 3. Load and process audio
        audio = whisper.load_audio(tmp_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # 4. Decode
        options = whisper.DecodingOptions()
        result = whisper.decode(model, mel, options)
        transcription = result.text.strip()

        if not transcription:
            raise HTTPException(status_code=404, detail="No speech found in audio.")

        return JSONResponse(content={"transcription": transcription})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    finally:
        # 5. Clean up temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


