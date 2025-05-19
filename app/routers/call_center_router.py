from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import logging
from app.services.stt_service import transcribe_audio_file, convert_webm_to_wav
from app.services.ai_answer_service import get_gpt_response
from app.services.summary_service import summary
from app.services.filtering_service import filtering
from app.services.tts_service import text_to_speech

logger = logging.getLogger(__name__)

router = APIRouter()

# 업로드 디렉토리 설정
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ai_mode = True
dialog = []

@router.post("/")
async def call_senter(audio: UploadFile = File(...)):
    try:
        logger.info("STT → GPT → TTS 요청 시작")
        # 1. 업로드된 파일 저장
        webm_path = os.path.join(UPLOAD_DIR, audio.filename)
        logger.info(f"업로드된 파일 경로: {webm_path}")
        with open(webm_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        # 2. webm → wav 변환
        wav_path = webm_path.replace(".webm", ".wav")
        convert_webm_to_wav(webm_path, wav_path)
        logger.info(f"webm → wav 변환 완료: {wav_path}")

        # 3. STT 처리
        stt_text = transcribe_audio_file(wav_path)
        logger.info(f"STT 변환 결과: {stt_text}")

        if ai_mode:
            return ai_call_center(stt_text)
        else: # human_mode
            return human_call_center(stt_text)
        
    except Exception as e:
        logger.error(f"에러 발생: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
def ai_call_center(user_question):
    global ai_mode
    global dialog

    is_response_possible, gpt_response = get_gpt_response(user_question)
    logger.info(f"GPT 응답 텍스트: {gpt_response}")

    if not is_response_possible:
        '''
        GPT가 답변할 수 없어서 Human mode로 전환되는 상황
        아래와 같은 응답이 생성됨
        return {
            "message": "HUMAN MODE: 필터링된 응답 생성",
            "stt_text": user_question,
            "filtered_question": filtered_question,
            "summary": summary_text
        }
        '''
        ai_mode = False
        summary_text = summary(dialog)
        response = human_call_center(user_question)
        response["summary"] = summary_text
        return response

    # 대화록에 질문 - 응답 저장
    dialog.append((user_question, gpt_response))
    # 5. TTS 처리
    tts_output_path = os.path.join(UPLOAD_DIR, "response.mp3")
    text_to_speech(gpt_response, tts_output_path)
    logger.info(f"TTS 출력 파일 생성 완료: {tts_output_path}")

    # HTTP URL로 반환
    tts_file_url = f"/uploads/response.mp3"
    logger.info(f"클라이언트에 반환된 TTS 파일 경로: {tts_file_url}")
    return {
        "message": "AI MODE: 사용자 질문에 대한 답변 완료",
        "stt_text": user_question,
        "gpt_response": gpt_response,
        "tts_file_path": tts_file_url
    }

def human_call_center(user_question):
    filtered_question = filtering(user_question)
    logger.info(f"필터링된 질문 텍스트: {filtered_question}")

    return {
        "message": "HUMAN MODE: 필터링된 응답 생성",
        "stt_text": user_question,
        "filtered_question": filtered_question
    }

@router.post("/reset")
async def reset_session():
    global dialog, ai_mode
    dialog.clear()
    ai_mode = True
    logger.info("대화 내용과 AI 모드 초기화 완료")
    return {"message": "세션이 초기화되었습니다."}

# def main():
#     user_question = "Usim 변경하려면 어떻게 해야하나요?"
#     print(ai_call_center(user_question))

# if __name__ == "__main__":
#     main()