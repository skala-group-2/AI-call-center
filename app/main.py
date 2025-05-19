from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers.stt_router import router as stt_router # stt_router와 tts_router 임포트
from app.routers.tts_router import router as tts_router  # tts_router 임포트
from app.routers.stt_tts_router import router as stt_tts_router
import openai

from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

# 명시적으로 .env 파일 경로 지정
dotenv_path = os.path.join(os.path.dirname(__file__), 'app', '.env')
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # /Users/phoenix/.../app
UPLOAD_DIR = os.path.join(BASE_DIR, "routers", "uploads")

app = FastAPI()
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# CORS 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# STT 라우터
app.include_router(stt_router, prefix="/stt")
app.include_router(tts_router, prefix="/tts")

# STT → GPT → TTS 라우터 등록
app.include_router(stt_tts_router, prefix="/stt-tts")

# 정적 파일 (HTML 프론트엔드)
frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# 정적 파일 (STT → GPT → TTS 프론트엔드)
stt_tts_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'stt-tts.html')

@app.get("/stt-tts")
async def serve_stt_tts_page():
    from fastapi.responses import FileResponse
    if not os.path.exists(stt_tts_path):
        raise HTTPException(status_code=404, detail="stt-tts.html 파일을 찾을 수 없습니다.")
    return FileResponse(stt_tts_path)

@app.get("/api-key")
async def get_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API 키가 설정되지 않았습니다.")
    return JSONResponse(content={"api_key": api_key})

# TTS 파일 저장 디렉토리
upload_path = os.path.join(os.path.dirname(__file__), "routers", "uploads")
print(f"정적 파일 경로: {upload_path}")  # 디버깅용 출력
app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)

# uvicorn app.main:app --reload
