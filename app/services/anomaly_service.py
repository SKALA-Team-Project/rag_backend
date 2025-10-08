from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import json
import numpy as np

from app.models.anomaly import Anomaly, Severity, AnomalyStatus
from app.models.timeseries import TimeSeriesTag
from app.schemas.anomaly import AnomalyCreate, AnomalyFilter
from app.ml.predictor import IntegratedPredictor

class AnomalyService:
    def __init__(self, db: Session):
        self.db = db
        self.predictor = IntegratedPredictor()
    
    def create_anomaly(self, anomaly_data: AnomalyCreate) -> Anomaly:
        """이상 이벤트 생성"""
        db_anomaly = Anomaly(**anomaly_data.dict())
        self.db.add(db_anomaly)
        self.db.commit()
        self.db.refresh(db_anomaly)
        return db_anomaly
    
    def get_anomalies(
        self,
        filters: AnomalyFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[Anomaly]:
        """이상 이벤트 목록 조회"""
        query = self.db.query(Anomaly)
        
        # 필터 적용
        if filters.start_date:
            query = query.filter(Anomaly.detected_at >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Anomaly.detected_at <= filters.end_date)
        
        if filters.eq_id:
            query = query.filter(Anomaly.eq_id == filters.eq_id)
        
        if filters.fault_codes:
            query = query.filter(Anomaly.fault_code.in_(filters.fault_codes))
        
        if filters.severities:
            query = query.filter(Anomaly.severity.in_(filters.severities))
        
        if filters.statuses:
            query = query.filter(Anomaly.status.in_(filters.statuses))
        
        return query.order_by(Anomaly.detected_at.desc()).offset(skip).limit(limit).all()
    
    def get_anomaly_by_id(self, anomaly_id: int) -> Optional[Anomaly]:
        """특정 이상 이벤트 조회"""
        return self.db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    
    def update_anomaly_status(self, anomaly_id: int, status: AnomalyStatus) -> Anomaly:
        """이상 이벤트 상태 업데이트"""
        anomaly = self.get_anomaly_by_id(anomaly_id)
        if not anomaly:
            raise ValueError("Anomaly not found")
        
        anomaly.status = status
        if status == AnomalyStatus.RESOLVED:
            anomaly.resolved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(anomaly)
        return anomaly
    
    def detect_realtime_anomaly(self, eq_id: str) -> Optional[Dict]:
        """
        실시간 이상 탐지
        최근 데이터를 기반으로 이상 여부 판단
        """
        # 최근 1시간 데이터 가져오기
        time_ago = datetime.utcnow() - timedelta(hours=1)
        
        timeseries_data = self.db.query(TimeSeriesTag).filter(
            and_(
                TimeSeriesTag.eq_id == eq_id,
                TimeSeriesTag.timestamp >= time_ago
            )
        ).order_by(TimeSeriesTag.timestamp).all()
        
        if len(timeseries_data) < 10:
            return None
        
        # 데이터를 배열로 변환 (간단한 버전)
        # 실제로는 52개 변수를 모두 사용
        values = np.array([d.value for d in timeseries_data[-60:]])  # 최근 60개
        data_matrix = values.reshape(-1, 1)  # (60, 1)
        
        # 예측 수행 (실제로는 52차원 데이터 사용)
        # 여기서는 더미 데이터 생성
        dummy_data = np.random.randn(60, 52)
        
        result = self.predictor.predict_fault(dummy_data, horizon=30)
        
        if result["is_anomaly"]:
            # 이상 이벤트 생성
            anomaly_create = AnomalyCreate(
                eq_id=eq_id,
                severity="critical" if result["probability"] > 0.8 else "warning",
                z_score=None,
                isolation_score=result["probability"],
                prediction_prob=result["probability"],
                feature_importance=json.dumps(result["feature_importance"])
            )
            
            anomaly = self.create_anomaly(anomaly_create)
            
            return {
                "anomaly_id": anomaly.id,
                **result
            }
        
        return None
    
    def get_top_anomaly_equipments(self, top_k: int = 5) -> List[Dict]:
        """이상 발생 빈도 Top K 설비"""
        last_week = datetime.utcnow() - timedelta(days=7)
        
        results = self.db.query(
            Anomaly.eq_id,
            func.count(Anomaly.id).label('count')
        ).filter(
            Anomaly.detected_at >= last_week
        ).group_by(Anomaly.eq_id).order_by(
            func.count(Anomaly.id).desc()
        ).limit(top_k).all()
        
        return [
            {"eq_id": eq_id, "count": count}
            for eq_id, count in results
        ]
    
    def get_heatmap_data(self, days: int = 7) -> Dict:
        """
        시간대별 이상 발생 히트맵 데이터
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        anomalies = self.db.query(Anomaly).filter(
            Anomaly.detected_at >= start_date
        ).all()
        
        # 요일별, 시간대별 집계
        heatmap = {}
        for anomaly in anomalies:
            day = anomaly.detected_at.strftime('%A')  # Monday, Tuesday, ...
            hour_block = f"{anomaly.detected_at.hour:02d}-{(anomaly.detected_at.hour+8) % 24:02d}"
            
            key = f"{day}_{hour_block}"
            heatmap[key] = heatmap.get(key, 0) + 1
        
        return heatmap