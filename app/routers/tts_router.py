from fastapi import APIRouter, HTTPException, Form
from app.services.tts_service import text_to_speech
import os

router = APIRouter()

# 출력 파일 저장할 uploads 폴더 경로
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def tts_endpoint(text: str = Form(...)):
    try:
        file_name = "openai_tts_output.mp3"
        output_path = os.path.join(UPLOAD_DIR, file_name)
        # 실제 TTS 생성 처리
        file_path = text_to_speech(text, output_path)  # 내부 저장용 절대경로
        # 클라이언트용 웹 경로 반환
        return {
            "message": "TTS 처리 완료 (OpenAI TTS)",
            "file_path": f"/uploads/{file_name}"  # 웹 경로만 전달
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))