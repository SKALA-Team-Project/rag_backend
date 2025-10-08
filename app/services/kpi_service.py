from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from datetime import datetime, timedelta

from app.models.lot import Lot, LotStatus
from app.models.equipment import Equipment
from app.models.anomaly import Anomaly

class KPIService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_kpi_summary(self, hours: int = 24) -> Dict:
        """KPI 요약 데이터"""
        time_ago = datetime.utcnow() - timedelta(hours=hours)
        
        # 목표량
        target_quantity = 1200
        
        # 양품량
        good_quantity = self.db.query(func.count(Lot.id)).filter(
            Lot.status == LotStatus.COMPLETED,
            Lot.defect_rate < 5.0,
            Lot.completed_at >= time_ago
        ).scalar() or 0
        
        # 총 생산량
        total_quantity = self.db.query(func.count(Lot.id)).filter(
            Lot.status == LotStatus.COMPLETED,
            Lot.completed_at >= time_ago
        ).scalar() or 0
        
        # 불량량
        defect_quantity = total_quantity - good_quantity
        
        # 생산수율
        yield_rate = (good_quantity / target_quantity * 100) if target_quantity > 0 else 0
        
        # 설비 가동률
        avg_utilization = self.db.query(func.avg(Equipment.utilization)).scalar() or 0
        
        # 데이터 신뢰도
        total_records = self.db.query(func.count(Lot.id)).scalar() or 1
        valid_records = self.db.query(func.count(Lot.id)).filter(
            Lot.defect_rate.isnot(None)
        ).scalar() or 0
        data_reliability = (valid_records / total_records * 100) if total_records > 0 else 0
        
        return {
            "target_quantity": target_quantity,
            "good_quantity": good_quantity,
            "total_quantity": total_quantity,
            "defect_quantity": defect_quantity,
            "yield_rate": round(yield_rate, 2),
            "delivery_rate": 98.5,
            "utilization": round(avg_utilization, 2),
            "data_reliability": round(data_reliability, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_kpi_correlation(self) -> Dict:
        """KPI 상관 분석"""
        lots = self.db.query(Lot).filter(
            Lot.status == LotStatus.COMPLETED
        ).all()
        
        if not lots:
            return {"yield_vs_defect": []}
        
        data_points = [
            {
                "yield": 100 - lot.defect_rate,
                "defect": lot.defect_rate,
                "lot_id": lot.lot_id
            }
            for lot in lots if lot.defect_rate is not None
        ]
        
        return {
            "yield_vs_defect": data_points
        }