import numpy as np
from typing import Dict, Tuple, Optional
from app.ml.lstm_model import LSTMPredictor
from app.ml.isolation_forest import IsolationForestDetector
from app.ml.feature_importance import FeatureImportanceCalculator
from app.config import settings

class IntegratedPredictor:
    """
    LSTM + Isolation Forest 통합 예측기
    """
    
    def __init__(self):
        # 모델 초기화
        self.lstm = LSTMPredictor(
            model_path=settings.LSTM_MODEL_PATH,
            input_size=52  # TEP 52개 변수
        )
        
        self.isolation_forest = IsolationForestDetector(
            model_path=settings.ISOLATION_FOREST_PATH
        )
        
        # TEP 변수 이름
        self.feature_names = [
            f"XMEAS_{i}" for i in range(1, 42)
        ] + [
            f"XMV_{i}" for i in range(1, 12)
        ]
        
        self.feature_calc = FeatureImportanceCalculator(self.feature_names)
    
    def predict_fault(
        self,
        data: np.ndarray,
        horizon: int = 30
    ) -> Dict:
        """
        Fault 발생 예측
        
        Args:
            data: 최근 시계열 데이터 (sequence_length, 52)
            horizon: 예측 시간 (분)
            
        Returns:
            prediction_result: 예측 결과 딕셔너리
        """
        # LSTM 예측
        lstm_pred, lstm_conf = self.lstm.predict(data, horizon)
        
        # 이상 탐지
        is_anomaly_lstm, lstm_score = self.lstm.detect_anomaly(data)
        is_anomaly_if, if_score = self.isolation_forest.detect_single(data[-1])
        
        # 종합 이상 확률
        combined_prob = (lstm_score + if_score) / 2.0
        
        # Feature Importance 계산
        importance = self.feature_calc.calculate_importance(data, combined_prob)
        top_features = self.feature_calc.get_top_features(importance, top_k=5)
        
        # 해석 생성
        interpretation = self._generate_interpretation(
            combined_prob,
            top_features,
            horizon
        )
        
        # 신뢰구간 계산 (간단한 추정)
        confidence_interval = self._calculate_confidence_interval(
            combined_prob,
            lstm_conf
        )
        
        return {
            "probability": float(combined_prob),
            "predicted_value": float(np.mean(lstm_pred)),
            "confidence": float(lstm_conf),
            "confidence_lower": confidence_interval[0],
            "confidence_upper": confidence_interval[1],
            "feature_importance": importance,
            "top_features": top_features,
            "interpretation": interpretation,
            "is_anomaly": is_anomaly_lstm or is_anomaly_if
        }
    
    def _calculate_confidence_interval(
        self,
        prob: float,
        confidence: float
    ) -> Tuple[float, float]:
        """95% 신뢰구간 계산"""
        margin = (1 - confidence) * 0.1  # 간단한 추정
        
        lower = max(0.0, prob - margin)
        upper = min(1.0, prob + margin)
        
        return (lower, upper)
    
    def _generate_interpretation(
        self,
        prob: float,
        top_features: list,
        horizon: int
    ) -> str:
        """AI 해석 생성"""
        
        if prob > 0.8:
            risk_level = "높은"
            action = "즉시 점검이 필요합니다"
        elif prob > 0.5:
            risk_level = "중간"
            action = "모니터링을 강화하세요"
        else:
            risk_level = "낮은"
            action = "정상 운영 가능합니다"
        
        # 주요 변수
        top_var = top_features[0][0] if top_features else "알 수 없음"
        
        interpretation = (
            f"{horizon}분 내 Fault 발생 가능성이 {prob*100:.1f}%로 {risk_level} 수준입니다. "
            f"주요 영향 변수는 {top_var}입니다. {action}."
        )
        
        return interpretation