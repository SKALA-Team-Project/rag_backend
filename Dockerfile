FROM python:3.11.9-slim

# 1) 기본 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=Asia/Seoul

WORKDIR /app

# 2) 시스템 패키지 (pillow/reportlab 안정 + 빌드툴 + netcat)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-traditional \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libfreetype6-dev \
    # (mysqlclient 쓰면 필요) default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# 3) 파이썬 의존성
#   - 레이어 캐시 효율을 위해 requirements.txt만 먼저 복사
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
 && pip install -r requirements.txt

# 4) 소스 복사
COPY . /app

# 5) 포트
EXPOSE 8000

# 6) 실행 (현재 컨테이너의 파이썬으로 uvicorn 실행)
#    --reload 사용 시 requirements.txt에 uvicorn[standard]가 있어야 함
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 빌드 단계 위쪽 어딘가에 (이미 비슷하게 있다면 유지)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*
