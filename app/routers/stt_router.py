from fastapi import APIRouter, UploadFile, File
import shutil
import os
from app.services.stt_service import transcribe_audio_file, convert_webm_to_wav

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def stt(audio: UploadFile = File(...)):
    webm_path = os.path.join(UPLOAD_DIR, audio.filename)

    with open(webm_path, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    try:
        # webm → wav 변환
        wav_path = webm_path.replace(".webm", ".wav")
        convert_webm_to_wav(webm_path, wav_path)

        # Whisper STT
        text = transcribe_audio_file(wav_path)

        os.remove(webm_path)
        os.remove(wav_path)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}
