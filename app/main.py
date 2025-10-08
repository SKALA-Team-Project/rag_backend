# app/main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.api.v1 import api_router
import logging

log = logging.getLogger("uvicorn.error")

app = FastAPI(title="TEP Dashboard API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        log.info("DB tables ensured.")
    except Exception as e:
        # DB가 아직 안 떠 있어도 서버는 구동되게 함
        log.error(f"DB init failed: {e}")

app.include_router(api_router, prefix="/api/v1")

# app/main.py
@app.get("/")
def root():
    return {"message": "Server is running!"}