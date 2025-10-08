import pandas as pd
import numpy as np
from typing import Tuple, Optional

class TEPDataProcessor:
    """Tennessee Eastman Process 데이터 전처리"""
    
    def __init__(self):
        self.feature_names = [f"XMEAS_{i}" for i in range(1, 42)] + [f"XMV_{i}" for i in range(1, 12)]
    
    def load_tep_data(self, file_path: str) -> pd.DataFrame:
        """TEP 데이터 로드"""
        df = pd.read_csv(file_path)
        return df
    
    def normalize_data(self, data: np.ndarray) -> Tuple[np.ndarray, dict]:
        """데이터 정규화"""
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        
        normalized = (data - mean) / (std + 1e-8)
        
        stats = {
            'mean': mean,
            'std': std
        }
        
        return normalized, stats
    
    def create_sequences(
        self,
        data: np.ndarray,
        sequence_length: int = 60
    ) -> np.ndarray:
        """시계열 시퀀스 생성"""
        sequences = []
        
        for i in range(len(data) - sequence_length + 1):
            sequences.append(data[i:i+sequence_length])
        
        return np.array(sequences)
    
    def detect_outliers(self, data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """이상치 탐지 (Z-score 방법)"""
        mean = np.mean(data, axis=0)
        std = np.std(data, axis=0)
        
        z_scores = np.abs((data - mean) / (std + 1e-8))
        
        outliers = np.any(z_scores > threshold, axis=1)
        
        return outliers