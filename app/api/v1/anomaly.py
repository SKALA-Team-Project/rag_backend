from webbrowser import get
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.anomaly import AnomalyResponse, AnomalyFilter
from app.services.anomaly_service import AnomalyService
from app.models.anomaly import AnomalyStatus

router = APIRouter(prefix="/anomaly", tags=["anomaly"])

@router.get("/list", response_model=List[AnomalyResponse])
async def get_anomaly_list(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    eq_id: Optional[str] = None,
    fault_codes: Optional[str] = None,  # 쉼표로 구분
    severities: Optional[str] = None,
    statuses: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """이상 이벤트 목록 조회"""
    
    filters = AnomalyFilter(
        start_date=start_date,
        end_date=end_date,
        eq_id=eq_id,
        fault_codes=fault_codes.split(',') if fault_codes else None,
        severities=severities.split(',') if severities else None,
        statuses=statuses.split(',') if statuses else None
    )
    
    service = AnomalyService(db)
    anomalies = service.get_anomalies(filters, skip, limit)
    
    return anomalies

@router.get("/{anomaly_id}", response_model=AnomalyResponse)
async def get_anomaly_detail(
    anomaly_id: int,
    db: Session = Depends(get_db)
):
    """이상 이벤트 상세 조회"""
    service = AnomalyService(db)
    anomaly = service.get_anomaly_by_id(anomaly_id)
    
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    
    return anomaly

@router.post("/{anomaly_id}/status")
async def update_anomaly_status(
    anomaly_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """이상 이벤트 상태 업데이트"""
    try:
        anomaly_status = AnomalyStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    service = AnomalyService(db)
    anomaly = service.update_anomaly_status(anomaly_id, anomaly_status)
    
    return {"message": "Status updated", "anomaly_id": anomaly.id}

@router.post("/detect/{eq_id}")
async def detect_realtime_anomaly(
    eq_id: str,
    db: Session = Depends(get_db)
):
    """실시간 이상 탐지"""
    service = AnomalyService(db)
    result = service.detect_realtime_anomaly(eq_id)
    
    if result:
        return {
            "detected": True,
            **result
        }
    else:
        return {
            "detected": False,
            "message": "No anomaly detected"
        }

@router.get("/statistics/top-equipments")
async def get_top_anomaly_equipments(
    top_k: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """이상 발생 빈도 Top K 설비"""
    service = AnomalyService(db)
    result = service.get_top_anomaly_equipments(top_k)
    
    return {"top_equipments": result}

@router.get("/statistics/heatmap")
async def get_anomaly_heatmap(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """시간대별 이상 발생 히트맵"""
    service = AnomalyService(db)
    heatmap_data = service.get_heatmap_data(days)
    
    return {
        "days": days,
        "heatmap": heatmap_data
    }