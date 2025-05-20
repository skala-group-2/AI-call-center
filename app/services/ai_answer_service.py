import os
import fitz
import re
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from openai.error import RateLimitError, AuthenticationError

# 환경변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 설정
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "faq_collection_pdf"
PDF_PATH = os.path.join(os.path.dirname(__file__), "data/usim.pdf")

# 초기화
sbert_model = SentenceTransformer(MODEL_NAME)
chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

# 질문 재작성 프롬프트
rewrite_prompt = PromptTemplate.from_template("""
너는 SKT 고객센터의 FAQ 질문 생성 어시스턴트야.

고객이 입력한 문장은 통화 또는 자연어 문장 형식이야.
내용이 USIM 또는 eSIM과 관련된 경우, 그 질문을 공식 FAQ 스타일로 간단하고 명확하게 정리해줘.
- 설명이나 배경은 제거하고
- 질문만 남기고
- 간단한 문장으로 변환해

만약 질문이 USIM과 관련이 없다면, 아래처럼 말해:
관련 없는 질문입니다.

절대로 답변을 하지 말고, 반드시 질문 형태로 끝내줘.

[사용자 질문]
{user_question}

[FAQ 질문]
""")
rewrite_chain = LLMChain(llm=llm, prompt=rewrite_prompt)

# 상담사 말투로 포장하는 프롬프트
wrap_prompt = PromptTemplate.from_template("""
너는 SKT 고객센터의 상담사야.
고객에게 아래의 내용을 정중하고 친절한 말투로 전달해줘.
내용은 바꾸지 말고, 말투만 부드럽고 친절하게 포장해줘.

[답변 원문]
{raw_answer}

[상담사 응답]
""")
wrap_chain = LLMChain(llm=llm, prompt=wrap_prompt)

# PDF FAQ 추출
def extract_faq_from_pdf(pdf_path: str):
    print(f"[INFO] PDF 로딩: {pdf_path}")
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    pattern = r"Q\d+:\s*(.*?)\s*A:\s*(.*?)(?=\s*Q\d+:|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)
    print(f"[INFO] 추출된 FAQ 수: {len(matches)}")
    return [{"question": q.strip(), "answer": a.strip()} for q, a in matches]

# 벡터DB 구성
def prepare_vector_db():
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    )
    print("[INFO] 벡터 컬렉션 확보 완료")

    if collection.count() == 0:
        faq_data = extract_faq_from_pdf(PDF_PATH)
        ids = [f"faq_{i}" for i in range(len(faq_data))]
        docs = [f"{item['question']} {item['answer']}" for item in faq_data]
        collection.add(ids=ids, documents=docs, metadatas=faq_data)
        print(f"[INFO] 총 {len(docs)}개 FAQ 문서 인덱싱 완료")
    else:
        print(f"[INFO] 기존 FAQ 문서 수: {collection.count()}")

    return collection

# 유사 FAQ LLM 선택
def search_faq_answer(user_query: str):
    collection = prepare_vector_db()
    results = collection.query(
        query_texts=[user_query],
        n_results=20,
        include=["metadatas"]
    )

    metadatas = results["metadatas"][0]
    if not metadatas:
        print("[WARN] FAQ 검색 결과 없음")
        return False, "관련된 FAQ가 없습니다. 상담사에게 연결해 드릴게요."

    faq_list_str = "\n".join([
        f"- 질문: {m['question']}\n  답변: {m['answer']}" for m in metadatas
    ])

    selection_prompt = PromptTemplate.from_template("""
너는 SKT 고객센터 FAQ 추천 어시스턴트야.
아래는 사용자의 질문과 관련된 FAQ 질문/답변 목록이야.
사용자 질문에 가장 적절한 FAQ의 '답변'만 출력해줘. 설명은 하지 마.
정확히 매칭되는 것이 없으면 "관련된 FAQ를 찾지 못했습니다."라고 말해줘.

[사용자 질문]
{user_question}

[후보 FAQ 목록]
{faq_list}

[선택된 답변]
""")
    selection_chain = LLMChain(llm=llm, prompt=selection_prompt)

    try:
        best_answer = selection_chain.invoke({
            "user_question": user_query,
            "faq_list": faq_list_str
        })["text"].strip()

        # 📌 다양한 실패 표현 탐지
        FAILURE_INDICATORS = [
            "관련된 FAQ를 찾지 못했습니다",
            "FAQ를 찾지 못했어요",
            "찾지 못했습니다",
            "답변을 제공해 드릴 수 없습니다",
            "상담사에게 연결",
            "정보가 없습니다",
            "죄송합니다"
        ]

        if any(keyword in best_answer for keyword in FAILURE_INDICATORS) or len(best_answer) < 10:
            print("[INFO] LLM이 관련 FAQ를 찾지 못했다고 판단")
            return False, "죄송합니다. 해당 질문에 대한 정보를 찾지 못했어요. 상담사에게 연결해 드릴게요."

        wrapped = wrap_chain.invoke({"raw_answer": best_answer})["text"].strip()
        return True, wrapped

    except Exception as e:
        print(f"[ERROR] LLM 판단 오류: {str(e)}")
        return False, "FAQ 판단 중 오류가 발생했습니다."


# 메인 질의 처리
def ask_faq_agent(user_question: str):
    try:
        rewritten = rewrite_chain.invoke({"user_question": user_question})["text"].strip()
        print(f"[INFO] 재작성된 질문: {rewritten}")
    except RateLimitError:
        return False, "현재 AI 처리 요청이 많아 지연되고 있습니다. 잠시 후 다시 시도해 주세요."
    except AuthenticationError:
        return False, "API 인증 오류입니다. OpenAI 키를 다시 확인해 주세요."
    except Exception as e:
        return False, f"질문 재작성 중 오류 발생: {str(e)}"

    if "관련 없는 질문입니다" in rewritten:
        print("[INFO] USIM 관련 없는 질문으로 판단됨")
        return True, "관련 없는 질문입니다."

    return search_faq_answer(rewritten)

# 최상위 진입점
def get_gpt_response(user_question: str):
    is_valid, answer = ask_faq_agent(user_question)
    print(answer)
    print(is_valid)
    return is_valid, answer