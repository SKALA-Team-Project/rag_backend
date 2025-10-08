# app/config.py
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    APP_NAME: str = "TEP Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database (기본값을 SQLite로 둬서 .env 없을 때도 서버가 안 죽음)
    DATABASE_URL: str = "sqlite:///./dev.db"

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # ML Models
    LSTM_MODEL_PATH: str = "./data/models/lstm_model.pt"
    ISOLATION_FOREST_PATH: str = "./data/models/isolation_forest.pkl"

    # pydantic-settings v2 방식
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
