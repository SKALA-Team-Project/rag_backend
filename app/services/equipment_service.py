from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import numpy as np

from app.models.equipment import Equipment
from app.models.timeseries import TimeSeriesTag

class EquipmentService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_equipment_list(self, eq_type: Optional[str] = None) -> List[Equipment]:
        """설비 목록 조회"""
        query = self.db.query(Equipment)
        
        if eq_type:
            query = query.filter(Equipment.type == eq_type)
        
        return query.all()
    
    def get_timeseries_data(
        self,
        eq_id: str,
        tag_name: str,
        hours: int = 24
    ) -> Dict:
        """시계열 데이터 조회"""
        time_ago = datetime.utcnow() - timedelta(hours=hours)
        
        data = self.db.query(TimeSeriesTag).filter(
            TimeSeriesTag.eq_id == eq_id,
            TimeSeriesTag.tag_name == tag_name,
            TimeSeriesTag.timestamp >= time_ago
        ).order_by(TimeSeriesTag.timestamp).all()
        
        if not data:
            return None
        
        # 정상 범위 계산
        values = [d.value for d in data]
        mean = np.mean(values)
        std = np.std(values)
        
        return {
            "eq_id": eq_id,
            "tag_name": tag_name,
            "unit": data[0].unit,
            "data": [
                {"timestamp": d.timestamp.isoformat(), "value": d.value}
                for d in data
            ],
            "normal_range": {
                "lower": float(mean - 3 * std),
                "upper": float(mean + 3 * std),
                "mean": float(mean),
                "std": float(std)
            }
        }