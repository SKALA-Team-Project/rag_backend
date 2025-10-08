# 설비 모니터링 API
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.equipment import Equipment
from app.models.timeseries import TimeSeriesTag

router = APIRouter(prefix="/equipment", tags=["Equipment"])

@router.get("/list")
async def get_equipment_list(
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    설비 목록 및 건강점수
    """
    query = db.query(Equipment)
    
    if type:
        query = query.filter(Equipment.type == type)
    
    equipments = query.all()
    
    return {
        "equipments": [
            {
                "eq_id": eq.eq_id,
                "name": eq.name,
                "type": eq.type.value,
                "health_score": eq.health_score,
                "utilization": eq.utilization,
                "status": eq.status
            }
            for eq in equipments
        ]
    }

@router.get("/{eq_id}/timeseries")
async def get_equipment_timeseries(
    eq_id: str,
    tag_name: str = Query(..., description="temperature, pressure, flow, level"),
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    특정 설비의 시계열 태그 데이터
    """
    time_ago = datetime.utcnow() - timedelta(hours=hours)
    
    data = db.query(TimeSeriesTag).filter(
        and_(
            TimeSeriesTag.eq_id == eq_id,
            TimeSeriesTag.tag_name == tag_name,
            TimeSeriesTag.timestamp >= time_ago
        )
    ).order_by(TimeSeriesTag.timestamp).all()
    
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    
    # 정상 범위 계산 (평균 ± 3σ)
    values = [d.value for d in data]
    import numpy as np
    mean = np.mean(values)
    std = np.std(values)
    
    return {
        "eq_id": eq_id,
        "tag_name": tag_name,
        "unit": data[0].unit if data else "",
        "data": [
            {
                "timestamp": d.timestamp.isoformat(),
                "value": d.value
            }
            for d in data
        ],
        "normal_range": {
            "lower": mean - 3 * std,
            "upper": mean + 3 * std,
            "mean": mean,
            "std": std
        }
    }

@router.get("/{eq_id}/health")
async def get_equipment_health(
    eq_id: str,
    db: Session = Depends(get_db)
):
    """
    설비 건강 점수 및 상세 정보
    """
    equipment = db.query(Equipment).filter(
        Equipment.eq_id == eq_id
    ).first()
    
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    return {
        "eq_id": equipment.eq_id,
        "name": equipment.name,
        "health_score": equipment.health_score,
        "utilization": equipment.utilization,
        "status": equipment.status,
        "last_updated": equipment.last_updated.isoformat()
    }

@router.post("/{eq_id}/compare")
async def compare_equipments(
    eq_ids: List[str],
    tag_name: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    다중 설비 비교 (최대 3개)
    """
    if len(eq_ids) > 3:
        raise HTTPException(status_code=400, detail="최대 3개 설비까지 비교 가능")
    
    time_ago = datetime.utcnow() - timedelta(hours=hours)
    
    result = {}
    for eq_id in eq_ids:
        data = db.query(TimeSeriesTag).filter(
            and_(
                TimeSeriesTag.eq_id == eq_id,
                TimeSeriesTag.tag_name == tag_name,
                TimeSeriesTag.timestamp >= time_ago
            )
        ).order_by(TimeSeriesTag.timestamp).all()
        
        result[eq_id] = [
            {"timestamp": d.timestamp.isoformat(), "value": d.value}
            for d in data
        ]
    
    return result