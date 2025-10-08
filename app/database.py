# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine.url import make_url
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
url = make_url(SQLALCHEMY_DATABASE_URL)

# SQLite일 때와 MySQL일 때를 분기
engine_kwargs = {
    "future": True,
}

if url.get_backend_name().startswith("sqlite"):
    # SQLite는 스레드 체크 해제 + 풀 파라미터 사용 X
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=False,
        **engine_kwargs,
    )
else:
    # MySQL (pymysql) 최적화 옵션
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,   # 연결 유효성 체크
        pool_recycle=3600,    # MySQL의 wait_timeout 대응
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG,  # DEBUG일 때만 SQL 로그
        **engine_kwargs,
    )

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

Base = declarative_base()

# FastAPI 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
