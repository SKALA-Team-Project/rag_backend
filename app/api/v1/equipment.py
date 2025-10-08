# 설비 모니터링 API
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import numpy as np  # ← 상단으로 이동

from app.database import get_db
from app.models.equipment import Equipment
from app.models.timeseries import TimeSeriesTag

# app/api/v1/equipment.py
router = APIRouter(prefix="/equipment", tags=["equipment"])  # 소문자로 통일

@router.get("/list")
async def get_equipment_list(
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """설비 목록 및 건강점수"""
    query = db.query(Equipment)
    if type:
        query = query.filter(Equipment.type == type)
    equipments = query.all()
    return {
        "equipments": [
            {
                "eq_id": eq.eq_id,
                "name": eq.name,
                "type": eq.type.value if hasattr(eq.type, "value") else eq.type,
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
    """특정 설비의 시계열 태그 데이터"""
    # DB가 UTC 저장이라고 가정 (로컬이면 timezone 변환 고려)
    time_ago = datetime.now(timezone.utc) - timedelta(hours=hours)

    data = (
        db.query(TimeSeriesTag)
        .filter(
            and_(
                TimeSeriesTag.eq_id == eq_id,
                TimeSeriesTag.tag_name == tag_name,
                TimeSeriesTag.timestamp >= time_ago
            )
        )
        .order_by(TimeSeriesTag.timestamp)
        .all()
    )

    if not data:
        raise HTTPException(status_code=404, detail="데이터가 없습니다.")

    values = [d.value for d in data]
    mean = float(np.mean(values))
    std = float(np.std(values))

    lower = mean - 3 * std
    upper = mean + 3 * std
    # std==0이면 정상범위 폭이 0 → 그대로 두거나 최소폭을 주고 싶으면 아래 주석 해제
    # if std == 0:
    #     lower = upper = mean

    return {
        "eq_id": eq_id,
        "tag_name": tag_name,
        "unit": data[0].unit or "",
        "data": [{"timestamp": d.timestamp.isoformat(), "value": d.value} for d in data],
        "normal_range": {"lower": lower, "upper": upper, "mean": mean, "std": std}
    }

@router.get("/{eq_id}/health")
async def get_equipment_health(
    eq_id: str,
    db: Session = Depends(get_db)
):
    """설비 건강 점수 및 상세 정보"""
    equipment = db.query(Equipment).filter(Equipment.eq_id == eq_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="설비를 찾을 수 없습니다.")
    return {
        "eq_id": equipment.eq_id,
        "name": equipment.name,
        "health_score": equipment.health_score,
        "utilization": equipment.utilization,
        "status": equipment.status,
        "last_updated": equipment.last_updated.isoformat() if equipment.last_updated else None
    }

@router.post("/compare")
async def compare_equipments(
    eq_ids: List[str],
    tag_name: str,
    hours: int = 24,
    db: Session = Depends(get_db),
):
    """다중 설비 비교 (최대 3개)"""
    if not eq_ids:
        raise HTTPException(status_code=400, detail="비교할 설비 ID를 1개 이상 입력하세요.")
    if len(eq_ids) > 3:
        raise HTTPException(status_code=400, detail="최대 3개 설비까지 비교 가능합니다.")
    if not tag_name:
        raise HTTPException(status_code=400, detail="tag_name을 입력하세요.")

    time_ago = datetime.now(timezone.utc) - timedelta(hours=hours)

    result = {}
    for eq_id in eq_ids:
        data = (
            db.query(TimeSeriesTag)
            .filter(
                and_(
                    TimeSeriesTag.eq_id == eq_id,
                    TimeSeriesTag.tag_name == tag_name,
                    TimeSeriesTag.timestamp >= time_ago
                )
            )
            .order_by(TimeSeriesTag.timestamp)
            .all()
        )
        result[eq_id] = [{"timestamp": d.timestamp.isoformat(), "value": d.value} for d in data]

    return {"tag_name": tag_name, "hours": hours, "series": result}
