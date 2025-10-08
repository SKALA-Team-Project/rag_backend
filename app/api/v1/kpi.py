# 홈 KPI API
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.models.lot import Lot, LotStatus
from app.models.equipment import Equipment
from app.models.anomaly import Anomaly, Severity

router = APIRouter(prefix="/kpi", tags=["KPI"])

@router.get("/summary")
async def get_kpi_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    홈 화면 KPI 카드 데이터 반환
    - 목표량, 양품량, 납기준수율, 생산수율, 불량량, 설비가동률
    """
    
    # 최근 24시간 기준
    time_24h_ago = datetime.utcnow() - timedelta(hours=24)
    
    # 1. 목표량 (임의 설정 or DB에서 가져오기)
    target_quantity = 1200
    
    # 2. 양품량 (완료된 LOT 중 defect_rate < 5%)
    good_quantity = db.query(func.count(Lot.id)).filter(
        Lot.status == LotStatus.COMPLETED,
        Lot.defect_rate < 5.0,
        Lot.completed_at >= time_24h_ago
    ).scalar() or 0
    
    # 3. 총 생산량
    total_quantity = db.query(func.count(Lot.id)).filter(
        Lot.status == LotStatus.COMPLETED,
        Lot.completed_at >= time_24h_ago
    ).scalar() or 0
    
    # 4. 불량량
    defect_quantity = total_quantity - good_quantity
    
    # 5. 생산수율
    yield_rate = (good_quantity / target_quantity * 100) if target_quantity > 0 else 0
    
    # 6. 납기준수율 (임의 계산)
    delivery_rate = 98.5
    
    # 7. 설비 가동률
    avg_utilization = db.query(func.avg(Equipment.utilization)).scalar() or 0
    
    # 8. 데이터 신뢰도
    total_records = db.query(func.count(Lot.id)).scalar() or 1
    valid_records = db.query(func.count(Lot.id)).filter(
        Lot.defect_rate.isnot(None)
    ).scalar() or 0
    data_reliability = (valid_records / total_records * 100) if total_records > 0 else 0
    
    return {
        "target_quantity": target_quantity,
        "good_quantity": good_quantity,
        "total_quantity": total_quantity,
        "defect_quantity": defect_quantity,
        "yield_rate": round(yield_rate, 2),
        "delivery_rate": delivery_rate,
        "utilization": round(avg_utilization, 2),
        "data_reliability": round(data_reliability, 2),
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/trend/{metric}")
async def get_kpi_trend(
    metric: str,  # yield_rate, defect_quantity, utilization
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """
    특정 KPI의 24시간 트렌드 그래프 데이터
    """
    # 시간별 데이터 집계 로직
    # 실제 구현 시 시간별 집계 쿼리 작성
    
    return {
        "metric": metric,
        "data": [
            {"time": "00:00", "value": 95.2},
            {"time": "01:00", "value": 94.8},
            # ... 24개 데이터 포인트
        ]
    }

@router.get("/alerts")
async def get_recent_alerts(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    최근 알림 목록 (홈 화면 알림 패널용)
    """
    alerts = db.query(Anomaly).order_by(
        Anomaly.detected_at.desc()
    ).limit(limit).all()
    
    return {
        "alerts": [
            {
                "id": alert.id,
                "eq_id": alert.eq_id,
                "severity": alert.severity.value,
                "fault_code": alert.fault_code,
                "probability": alert.prediction_prob,
                "detected_at": alert.detected_at.isoformat(),
                "status": alert.status.value
            }
            for alert in alerts
        ]
    }

@router.get("/lots/status")
async def get_lot_status_distribution(db: Session = Depends(get_db)):
    """
    실시간 공정 현황 (진행/완료/실패/대기)
    """
    status_counts = db.query(
        Lot.status,
        func.count(Lot.id)
    ).group_by(Lot.status).all()
    
    result = {status.value: 0 for status in LotStatus}
    for status, count in status_counts:
        result[status.value] = count
    
    total = sum(result.values())
    
    return {
        "counts": result,
        "percentages": {
            key: round(val / total * 100, 1) if total > 0 else 0
            for key, val in result.items()
        },
        "total": total
    }