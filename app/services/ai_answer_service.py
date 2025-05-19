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
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType

# 환경변수 로드
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 설정
MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "faq_collection_pdf"
PDF_PATH = "data/usim.pdf"
SIMILARITY_THRESHOLD = 0.85

# 모델 & 클라이언트 초기화
sbert_model = SentenceTransformer(MODEL_NAME)
chroma_client = chromadb.Client(Settings(anonymized_telemetry=False))

# 질문 재작성 프롬프트 + 체인
rewrite_prompt = PromptTemplate.from_template(
    """
너는 고객센터 FAQ 질의 재작성 어시스턴트야.
다음 질문을 공식적인 FAQ 질문처럼 고쳐줘. 문맥은 유지하면서 구체화해줘.

[사용자 질문]
{user_question}

[FAQ 스타일 질문]
"""
)
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
rewrite_chain = LLMChain(llm=llm, prompt=rewrite_prompt)

# PDF에서 FAQ 추출
def extract_faq_from_pdf(pdf_path: str):
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    pattern = r"Q\d+:\s*(.*?)\s*A:\s*(.*?)(?=\s*Q\d+:|\Z)"
    matches = re.findall(pattern, text, re.DOTALL)
    return [{"question": q.strip(), "answer": a.strip()} for q, a in matches]

# 벡터 DB 준비
def prepare_vector_db():
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    except:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    )

    faq_data = extract_faq_from_pdf(PDF_PATH)
    if faq_data:
        ids = [f"faq_{i}" for i in range(len(faq_data))]
        docs = [f"{item['question']} {item['answer']}" for item in faq_data]
        collection.add(ids=ids, documents=docs, metadatas=faq_data)

    return collection

# 벡터 검색 + 결과 상태 리턴
def search_faq_with_flag(user_query: str):
    try:
        collection = chroma_client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
        )
    except:
        collection = prepare_vector_db()

    results = collection.query(
        query_texts=[user_query],
        n_results=5,
        include=["distances", "metadatas"]
    )

    distances = results.get("distances", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not distances or not metadatas:
        return False, user_query, "FAQ에 해당하는 질문이 없습니다."

    filtered = [(m, d) for m, d in zip(metadatas, distances) if d <= SIMILARITY_THRESHOLD]
    if not filtered:
        return False, user_query, "FAQ에 해당하는 질문이 없습니다."

    best_match = filtered[0]
    return True, user_query, best_match[0]["answer"]

# LangChain Tool 정의
vector_tool = Tool(
    name="FAQSearchTool",
    func=lambda x: search_faq_with_flag(x)[2],
    description="FAQ 스타일 질문을 받아 관련된 질문과 답변을 벡터 검색을 통해 반환하는 도구입니다."
)

# LangChain Agent 정의
agent = initialize_agent(
    tools=[vector_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False
)

# 최종 질의 함수
def ask_faq_agent(user_question: str):
    rewritten = rewrite_chain.run(user_question).strip()
    return search_faq_with_flag(rewritten)

def get_gpt_response(user_question: str):
    """
    외부 서비스용 진입점 함수: 질문 입력 시
    - test: 벡터 검색 가능 여부
    - question_text: 원 질문 (재작성 전)
    - answer_text: 벡터 검색 답변 또는 fallback 메시지
    """
    return ask_faq_agent(user_question)

# 초기 로딩 시 DB 준비만 수행
if __name__ == "__main__":
    prepare_vector_db()
