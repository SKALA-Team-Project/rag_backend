import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, Optional
import os

class LSTMAutoencoder(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2):
        super(LSTMAutoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        
        # Decoder
        self.decoder = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True
        )
        
        # Output layer
        self.output_layer = nn.Linear(hidden_size, input_size)
        
    def forward(self, x):
        # Encode
        encoded, (hidden, cell) = self.encoder(x)
        
        # Decode
        decoded, _ = self.decoder(encoded)
        
        # Output
        output = self.output_layer(decoded)
        
        return output

class LSTMPredictor:
    def __init__(self, model_path: Optional[str] = None, input_size: int = 52):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = LSTMAutoencoder(input_size=input_size).to(self.device)
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        
        self.model.eval()
    
    def load_model(self, path: str):
        """저장된 모델 로드"""
        self.model.load_state_dict(torch.load(path, map_location=self.device))
        print(f"✅ LSTM 모델 로드 완료: {path}")
    
    def predict(self, data: np.ndarray, horizon: int = 30) -> Tuple[np.ndarray, float]:
        """
        예측 수행
        
        Args:
            data: 입력 데이터 (sequence_length, features)
            horizon: 예측 시간 (분)
            
        Returns:
            predicted_values: 예측값
            confidence: 신뢰도
        """
        with torch.no_grad():
            # Normalize
            data_tensor = torch.FloatTensor(data).unsqueeze(0).to(self.device)
            
            # Predict
            output = self.model(data_tensor)
            
            # Reconstruction error (이상 탐지용)
            error = torch.mean((data_tensor - output) ** 2).item()
            
            # Get last prediction
            predicted = output[0, -1, :].cpu().numpy()
            
            # Calculate confidence (1 - normalized error)
            confidence = max(0.0, min(1.0, 1.0 - error))
            
            return predicted, confidence
    
    def detect_anomaly(self, data: np.ndarray, threshold: float = 0.05) -> Tuple[bool, float]:
        """
        이상 탐지
        
        Returns:
            is_anomaly: 이상 여부
            score: 이상 점수
        """
        with torch.no_grad():
            data_tensor = torch.FloatTensor(data).unsqueeze(0).to(self.device)
            output = self.model(data_tensor)
            
            # Reconstruction error
            error = torch.mean((data_tensor - output) ** 2, dim=-1)
            anomaly_score = error.mean().item()
            
            is_anomaly = anomaly_score > threshold
            
            return is_anomaly, anomaly_score