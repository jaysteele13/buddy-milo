from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse, FileResponse
from fastapi import FastAPI, HTTPException, Header
import os
from dotenv import load_dotenv
from text_to_speech.model_logic import text2speech, generate_full_audio
import asyncio

load_dotenv()

router = APIRouter()
API_KEY = os.getenv("API_KEY")



class SpeechRequest(BaseModel):
    sentence: str

# @router.post("/")
# async def transcribe(request: SpeechRequest,
#                      x_api_key: str = Header(..., alias="x-api-key")):
    
   

#     if x_api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Unauthorized")

#     if not request.sentence.strip():
#         raise HTTPException(status_code=400, detail="Sentence must be populated")

#     try:
#         wavfilepath = text2speech(request.sentence)
#         return FileResponse(wavfilepath, media_type="audio/wav", filename="output.wav")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {e}")
    
@router.post("/")
async def synthesize(request: SpeechRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401)
    if not request.sentence.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")
    try:
        output_file = await asyncio.to_thread(generate_full_audio, request.sentence)
        return FileResponse(output_file, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


