import os
import openai
from dotenv import load_dotenv

# 1) .env에서 OPENAI_API_KEY 불러오기
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise RuntimeError("환경 변수에 OPENAI_API_KEY를 설정해 주세요.")

def filtering(raw_text: str) -> str:
    """
    1) 과도한 욕설·모욕·비속어를 판단해 [차단된 발언] 처리
    2) 상담사 전달용 문의 요지&감정 상태를 정리
    출력은 :
      [상담사 전달용 필터&요약문]
      - 문의 요지: ...
      - 감정 상태: ...
    """
    
    system_prompt = (
        "너는 고객과 상담사 사이의 중간 에이전트야."
        "제공되는 고객 발화에서 과도한 욕설·모욕·비속어는 스스로 판단해서 "
        "`[차단된 발언]`으로 대체하고, **상담사**에게 전달하는 역할이야 "
        "문어체로 작성하며 욕설을 제외하고 원문의 내용을 최대한 포함해줘"
        "반드시 다음 형식으로 응답해 줘:\n\n"
        "[상담사 전달용 필터&요약문]\n"
        "- 문의 요지: <여기에 핵심 문의 내용>\n"
        "- 감정 상태: <여기에 감정 상태>\n"
        "\n\n"

    )
    user_block = f"```\n{raw_text}\n```"

    resp = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_block},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


# if __name__ == "__main__":
#     # STT에서 넘어온 예시 원문
#     raw = (
#         "아니 해킹당해서 사람 번거롭게 하는것도 짜증나는데 AI가 전화받게 시켜?"
#         "됐고, 내 유심이나 빨리 교체해봐요! 씨발 "
#         "똥은 니들이 싸고 왜 나더러 이래라 저래라야? 그냥 니들이 알아서 새 유심 우리집에 보내놓으면 되잖아?"
#         "그리고 유심을 바꾸면 전화번호도 바뀌는지 물어봤는데, 왜 제대로 답변을 못해 씨발"
#     )
#     # raw = ("아 네 안녕하세요, 이번 유심 사태 때문에 문의하고 싶은게 있어서 전화했는데요,"
#     # "그 유심보호서비스 있잖아요, 그거 가입하면 유심 교체 안해도 괜찮은건가요?"
#     # )
#     result = filtering(raw)
#     print(result)