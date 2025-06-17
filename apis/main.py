from fastapi import FastAPI


from llm_logic.app import router as personality_router
from text_to_speech.app import router as t2s_router
from speech_to_text.app import router as s2t_router

app = FastAPI()

app.include_router(personality_router, prefix="/personality")
app.include_router(t2s_router, prefix="/text2speech")
app.include_router(s2t_router, prefix="/transcribe")
