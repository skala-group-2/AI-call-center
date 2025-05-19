# Python 3.11 이미지 사용
FROM python:3.11-slim

# 시스템 패키지 설치 (ffmpeg 포함)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y ffmpeg


# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt ./
COPY . /app

# 의존성 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]