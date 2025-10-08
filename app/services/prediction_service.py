from sqlalchemy.orm import Session
from typing import Dict, Optional
import uuid
import json
import numpy as np
from datetime import datetime, timedelta

from app.models.prediction import Prediction
from app.models.timeseries import TimeSeriesTag
from app.schemas.prediction import PredictionRequest
from app.ml.predictor import IntegratedPredictor

class PredictionService:
    def __init__(self, db: Session):
        self.db = db
        self.predictor = IntegratedPredictor()
    
    def create_prediction(
        self,
        request: PredictionRequest
    ) -> Prediction:
        """
        예측 수행 및 결과 저장
        """
        # 최근 데이터 가져오기
        time_ago = datetime.utcnow() - timedelta(hours=2)
        
        timeseries_data = self.db.query(TimeSeriesTag).filter(
            TimeSeriesTag.eq_id == request.eq_id,
            TimeSeriesTag.timestamp >= time_ago
        ).order_by(TimeSeriesTag.timestamp).all()
        
        if len(timeseries_data) < 60:
            raise ValueError("충분한 데이터가 없습니다 (최소 60개 필요)")
        
        # 데이터 준비 (실제로는 52차원)
        # 여기서는 더미 데이터 사용
        dummy_data = np.random.randn(60, 52)
        
        # 예측 수행
        result = self.predictor.predict_fault(
            dummy_data,
            horizon=request.prediction_horizon
        )
        
        # 결과 저장
        job_id = str(uuid.uuid4())
        
        db_prediction = Prediction(
            job_id=job_id,
            eq_id=request.eq_id,
            prediction_target=request.prediction_target,
            prediction_horizon=request.prediction_horizon,
            predicted_value=result["predicted_value"],
            probability=result["probability"],
            confidence_lower=result["confidence_lower"],
            confidence_upper=result["confidence_upper"],
            feature_importance=json.dumps(result["feature_importance"]),
            interpretation=result["interpretation"]
        )
        
        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)
        
        return db_prediction
    
    def get_prediction_by_job_id(self, job_id: str) -> Optional[Prediction]:
        """예측 결과 조회"""
        return self.db.query(Prediction).filter(
            Prediction.job_id == job_id
        ).first()
    
    def get_prediction_history(
        self,
        eq_id: Optional[str] = None,
        limit: int = 10
    ) -> list[Prediction]:
        """예측 이력 조회"""
        query = self.db.query(Prediction).order_by(Prediction.created_at.desc())
        
        if eq_id:
            query = query.filter(Prediction.eq_id == eq_id)
        
        return query.limit(limit).all()