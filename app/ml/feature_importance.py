import numpy as np
from typing import Dict, List

class FeatureImportanceCalculator:
    """
    Feature Importance 계산 (SHAP 간소화 버전)
    """
    
    def __init__(self, feature_names: List[str]):
        self.feature_names = feature_names
    
    def calculate_importance(
        self,
        data: np.ndarray,
        anomaly_score: float
    ) -> Dict[str, float]:
        """
        간단한 Feature Importance 계산
        
        실제로는 SHAP를 사용하지만, 여기서는 간소화된 버전 사용
        """
        # 데이터의 표준편차 기반 중요도 계산
        std_devs = np.std(data, axis=0)
        
        # 정규화
        total = np.sum(std_devs)
        if total > 0:
            importances = std_devs / total
        else:
            importances = np.ones(len(std_devs)) / len(std_devs)
        
        # Dictionary로 변환
        importance_dict = {
            name: float(imp) * anomaly_score
            for name, imp in zip(self.feature_names, importances)
        }
        
        # 상위 10개만 반환
        sorted_importance = dict(
            sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return sorted_importance
    
    def get_top_features(
        self,
        importance_dict: Dict[str, float],
        top_k: int = 5
    ) -> List[tuple]:
        """
        상위 K개 중요 변수 반환
        
        Returns:
            List of (feature_name, importance_score)
        """
        sorted_items = sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_items[:top_k]