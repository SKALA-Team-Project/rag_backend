# app/api/v1/__init__.py
#라우터 통합
from fastapi import APIRouter

# 실제 파일명에 맞게 수정하세요 (예시는 kpi/equipment/anomaly/prediction/report/health)
from . import kpi, equipment, anomaly, prediction, report

api_router = APIRouter()
api_router.include_router(kpi.router,        prefix="/kpi",        tags=["kpi"])
api_router.include_router(equipment.router,  prefix="/equipment",  tags=["equipment"])
api_router.include_router(anomaly.router,    prefix="/anomaly",    tags=["anomaly"])
api_router.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
api_router.include_router(report.router,     prefix="/report",     tags=["report"])

__all__ = ["api_router"]
