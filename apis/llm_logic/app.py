from fastapi import FastAPI, Header, HTTPException, Request, APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException, Header
import os
from dotenv import load_dotenv

from llm_logic.app_logic import check_for_main_prompt

load_dotenv()

router = APIRouter()
API_KEY = os.getenv("API_KEY")



class PersonalityRequest(BaseModel):
    sentence: str

@router.post("/")
async def transcribe(request: PersonalityRequest,
                     x_api_key: str = Header(..., alias="x-api-key")):
    
   

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not request.sentence.strip():
        raise HTTPException(status_code=400, detail=f"Sentence must be populated. Sentence: {request.sentence}")

    try:
        new_sentence = check_for_main_prompt(request.sentence)
        return JSONResponse(content={"personality": new_sentence})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

