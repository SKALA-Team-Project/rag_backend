import sys
sys.path.append('.')

import numpy as np
import torch
import pickle
import os
from sklearn.ensemble import IsolationForest

from app.ml.lstm_model import LSTMAutoencoder

def train_dummy_models():
    """더미 ML 모델 학습 및 저장"""
    
    print("🤖 ML 모델 학습 중...")
    
    # 디렉토리 생성
    os.makedirs('./data/models', exist_ok=True)
    
    # 1. LSTM Autoencoder 학습
    print("\n1. LSTM Autoencoder 학습...")
    
    # 더미 데이터 생성 (실제로는 TEP 데이터 사용)
    dummy_data = np.random.randn(1000, 60, 52)  # (samples, sequence_length, features)
    
    model = LSTMAutoencoder(input_size=52)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = torch.nn.MSELoss()
    
    model.train()
    for epoch in range(10):
        total_loss = 0
        for i in range(0, len(dummy_data), 32):
            batch = torch.FloatTensor(dummy_data[i:i+32])
            
            optimizer.zero_grad()
            output = model(batch)
            loss = criterion(output, batch)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        print(f"  Epoch {epoch+1}/10, Loss: {total_loss/len(dummy_data):.6f}")
    
    # 모델 저장
    torch.save(model.state_dict(), './data/models/lstm_model.pt')
    print("✅ LSTM 모델 저장 완료")
    
    # 2. Isolation Forest 학습
    print("\n2. Isolation Forest 학습...")
    
    # 더미 데이터 생성
    dummy_data_2d = np.random.randn(1000, 52)
    
    iso_forest = IsolationForest(
        contamination=0.1,
        random_state=42,
        n_estimators=100
    )
    
    iso_forest.fit(dummy_data_2d)
    
    # 모델 저장
    with open('./data/models/isolation_forest.pkl', 'wb') as f:
        pickle.dump(iso_forest, f)
    
    print("✅ Isolation Forest 모델 저장 완료")
    
    print("\n🎉 모든 모델 학습 완료!")
    print("\n저장된 모델:")
    print("  - ./data/models/lstm_model.pt")
    print("  - ./data/models/isolation_forest.pkl")

if __name__ == "__main__":
    train_dummy_models()