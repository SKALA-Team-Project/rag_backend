from sklearn.ensemble import IsolationForest
import numpy as np
import pickle
import os
from typing import Tuple, Optional

class IsolationForestDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def load_model(self, path: str):
        """저장된 모델 로드"""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
        print(f"✅ Isolation Forest 모델 로드 완료: {path}")
    
    def save_model(self, path: str):
        """모델 저장"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"✅ 모델 저장 완료: {path}")
    
    def fit(self, data: np.ndarray):
        """모델 학습"""
        self.model.fit(data)
        return self
    
    def detect(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        이상 탐지
        
        Returns:
            predictions: -1 (이상) or 1 (정상)
            scores: 이상 점수 (-1에 가까울수록 이상)
        """
        predictions = self.model.predict(data)
        scores = self.model.score_samples(data)
        
        return predictions, scores
    
    def detect_single(self, data: np.ndarray) -> Tuple[bool, float]:
        """
        단일 샘플 이상 탐지
        
        Returns:
            is_anomaly: 이상 여부
            score: 이상 점수 (0~1, 높을수록 이상)
        """
        pred, score = self.detect(data.reshape(1, -1))
        
        is_anomaly = pred[0] == -1
        
        # Score를 0~1로 정규화
        normalized_score = 1.0 / (1.0 + np.exp(score[0]))
        
        return is_anomaly, normalized_score