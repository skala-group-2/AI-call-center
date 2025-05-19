'''
파일명: /service/ai_answer_service.py(가칭)
설명: 고객과 AI가 대화할 수 있도록 하는 에이전트 -> 형섭, 성우
- 함수명: get_gpt_response(가칭) --> 여러 함수로 나눠서 해도 됨
    - input: 고객 질문(오디오 파일 path) or 고객 질문(str) 중 택 1
    - output: 검색 가능 여부(boolean), 응답 내용(str)
'''
cnt = 0
#텍스트 입력 → GPT 응답 받기
def get_gpt_response(user_input):
    global cnt
    if cnt < 2:
        is_response_possible = True
        reply = "질문에 대한 응답입니다."
    else:
        is_response_possible = False
        reply = "관련 내용을 검색할 수 없어 상담사와 연결합니다."
    cnt += 1
    
    return is_response_possible, reply

# print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")