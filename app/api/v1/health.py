#FastAPI 서버가 켜져 있고 DB 연결이 잘 되는지 확인용
# app/api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/health", tags=["system"])

@router.get("/ping")
async def health_check(db: Session = Depends(get_db)):
    """
    ✅ 시스템 전체 헬스 체크 API
    - 서버 및 DB 연결 상태 확인
    """
    try:
        db.execute("SELECT 1")  # DB 연결 확인
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "db": db_status,
        "message": "TEP Dashboard Backend is running 🚀"
    }
