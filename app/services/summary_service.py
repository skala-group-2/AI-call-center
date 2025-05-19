'''
파일명: /service/summary_service.py(가칭)
설명: 고객과 AI의 대화 내용을 보고 요약 생성 -> 민채
- 함수명: summary(가칭)
    - input: 고객&AI간 전체 대화 내용(list[(str, str)])
    - output: 요약된 대화 내용(str)
'''

import openai
from dotenv import load_dotenv
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summary(conversation_history: list[tuple[str, str]]) -> str:
    """
    SKT 콜센터 상황 요약 Agent

    고객과 AI 챗봇 간의 통신 서비스 관련 대화를 분석하여,
    상담사가 빠르게 파악할 수 있는 구조화된 요약을 생성합니다.

    Args:
        conversation_history: [(고객 질문, AI 응답), ...]
        
    Returns:
        structured_summary (str): 상담사에게 전달할 도메인 특화 요약 텍스트
    """
    
    # 대화 기록 포맷 정리
    chat_transcript = "\n".join(
        f"[고객] {user}\n[AI] {ai}" for user, ai in conversation_history
    )

    # 프롬프트 구성 (SKT 특화)
    prompt = f"""
당신은 SKT 콜센터용 AI 요약 전문가입니다.

다음은 고객과 AI 챗봇 간의 실제 대화입니다.
이 대화를 분석하여 상담사가 통신 서비스 상황을 빠르게 이해할 수 있도록 아래 항목에 맞게 요약해주세요.

💡 반드시 **통신서비스 도메인 기준**으로 분석하며, 고객의 감정과 요구사항을 정확히 파악해주세요.

### 요약 포맷:
1. 📌 고객 감정 상태 (예: 혼란, 불만, 분노, 침착 등)
2. 📞 핵심 문의 내용 (요금제/데이터/통신장애/단말기 등)
3. 🤖 AI가 제공한 주요 안내 요약
4. ✅ 해결 여부 및 남은 이슈
5. 🔁 상담 연결 필요 여부 (필요/불필요 + 간단한 이유)

--- 대화 기록 ---
{chat_transcript}

--- 상담사 전달용 요약 ---
"""
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 SKT 텔레콤 콜센터에 특화된 AI 요약 분석 전문가이다. "
                    "고객과 챗봇의 대화를 바탕으로 상담사가 빠르게 파악할 수 있도록 구조화된 요약을 생성하라."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return response.choices[0].message["content"].strip()

# conversation = [
#     ("아 네 안녕하세요, 이번 유심 사태 때문에 문의하고 싶은게 있어서 전화했는데요, 그 유심보호서비스 있잖아요, 그거 가입하면 유심 교체 안해도 괜찮은건가요?", 
#      "네, 유심 보호 서비스는 유심 분실/도난 시 고객님의 정보를 보호해주는 서비스입니다."),
#     ("그래도 좀 불안해서 그런데 유심 교체하려면 어떻게 해야하나요?", 
#      "유심 교체는 가까운 SKT 대리점에서 진행하실 수 있습니다. 신분증 지참 부탁드립니다."),
#     ("저희 집 근처에 SKT 대리점이 없는 것 같은데, 혹시 근처 SKT 대리점이 어디있는지 알려주실 수 있나요?", 
#      "죄송합니다. 대리점 위치 안내는 상담사를 통해 도와드릴 수 있습니다. 지금 연결해드리겠습니다.")
# ]

# summary_text = summary(conversation)
# print(summary_text)