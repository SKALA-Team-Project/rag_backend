import sys
sys.path.append('.')

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Equipment, Lot, TimeSeriesTag, Anomaly, EquipmentType, LotStatus, Severity, AnomalyStatus
from datetime import datetime, timedelta
import random
import numpy as np

def load_dummy_data():
    """더미 데이터 로드"""
    db = SessionLocal()
    
    try:
        print("📊 더미 데이터 생성 중...")
        
        # 1. 설비 데이터
        equipments = [
            Equipment(eq_id="R-01", name="Reactor-01", type=EquipmentType.REACTOR, health_score=85.5, utilization=92.3),
            Equipment(eq_id="R-02", name="Reactor-02", type=EquipmentType.REACTOR, health_score=78.2, utilization=88.7),
            Equipment(eq_id="S-01", name="Stripper-01", type=EquipmentType.STRIPPER, health_score=92.1, utilization=95.2),
            Equipment(eq_id="S-02", name="Stripper-02", type=EquipmentType.STRIPPER, health_score=65.3, utilization=78.5),
            Equipment(eq_id="C-01", name="Compressor-01", type=EquipmentType.COMPRESSOR, health_score=95.8, utilization=91.2),
            Equipment(eq_id="C-02", name="Compressor-02", type=EquipmentType.COMPRESSOR, health_score=88.4, utilization=89.6),
            Equipment(eq_id="CD-01", name="Condenser-01", type=EquipmentType.CONDENSER, health_score=35.2, utilization=65.3),
            Equipment(eq_id="CL-01", name="Cooler-01", type=EquipmentType.COOLER, health_score=91.7, utilization=93.8),
        ]
        
        db.add_all(equipments)
        db.commit()
        print("✅ 설비 데이터 생성 완료 (8개)")
        
        # 2. LOT 데이터 (최근 24시간)
        lots = []
        now = datetime.utcnow()
        
        for i in range(1, 51):
            lot_id = f"LOT-{i:03d}"
            status = random.choice([LotStatus.COMPLETED, LotStatus.COMPLETED, LotStatus.COMPLETED, LotStatus.FAILED])
            defect_rate = random.uniform(0.5, 15.0) if status == LotStatus.FAILED else random.uniform(0.1, 4.5)
            
            started_at = now - timedelta(hours=random.randint(1, 24))
            completed_at = started_at + timedelta(hours=random.randint(1, 3)) if status == LotStatus.COMPLETED else None
            
            lot = Lot(
                lot_id=lot_id,
                eq_id=random.choice([e.eq_id for e in equipments]),
                line=random.choice(["Line-A", "Line-B"]),
                stage=random.choice(["Reaction", "Stripping", "Compression", "Condensation"]),
                status=status,
                defect_rate=defect_rate,
                started_at=started_at,
                completed_at=completed_at,
                created_at=started_at
            )
            lots.append(lot)
        
        db.add_all(lots)
        db.commit()
        print("✅ LOT 데이터 생성 완료 (50개)")
        
        # 3. 시계열 데이터 (최근 24시간, 1분 간격)
        print("📈 시계열 데이터 생성 중 (시간이 걸릴 수 있습니다)...")
        
        timeseries_data = []
        base_values = {
            "temperature": 450.0,
            "pressure": 1.0,
            "flow": 100.0,
            "level": 50.0
        }
        
        for eq in equipments[:4]:  # 처음 4개 설비만
            for minutes_ago in range(0, 1440, 5):  # 5분 간격, 24시간
                timestamp = now - timedelta(minutes=minutes_ago)
                
                for tag_name, base_value in base_values.items():
                    # 랜덤 노이즈 추가
                    value = base_value + np.random.normal(0, base_value * 0.05)
                    
                    # 가끔 이상치 추가
                    if random.random() < 0.02:  # 2% 확률
                        value += base_value * random.choice([0.2, -0.2])
                    
                    unit = {
                        "temperature": "°C",
                        "pressure": "Pa",
                        "flow": "m³/h",
                        "level": "%"
                    }[tag_name]
                    
                    ts_data = TimeSeriesTag(
                        timestamp=timestamp,
                        eq_id=eq.eq_id,
                        tag_name=tag_name,
                        value=value,
                        unit=unit
                    )
                    timeseries_data.append(ts_data)
        
        # 배치로 저장
        batch_size = 1000
        for i in range(0, len(timeseries_data), batch_size):
            db.add_all(timeseries_data[i:i+batch_size])
            db.commit()
            print(f"  - {i + batch_size}/{len(timeseries_data)} 저장됨")
        
        print("✅ 시계열 데이터 생성 완료")
        
        # 4. 이상 이벤트 데이터
        anomalies = []
        
        for i in range(1, 21):
            detected_at = now - timedelta(hours=random.randint(1, 168))
            is_resolved = random.random() < 0.6
            
            anomaly = Anomaly(
                lot_id=random.choice([l.lot_id for l in lots]) if random.random() < 0.7 else None,
                eq_id=random.choice([e.eq_id for e in equipments]),
                fault_code=f"F{random.randint(1, 21)}",
                severity=random.choice([Severity.CRITICAL, Severity.WARNING, Severity.INFO]),
                status=AnomalyStatus.RESOLVED if is_resolved else random.choice([AnomalyStatus.UNCONFIRMED, AnomalyStatus.IN_PROGRESS]),
                z_score=random.uniform(3.0, 8.0),
                isolation_score=random.uniform(0.6, 0.95),
                prediction_prob=random.uniform(0.5, 0.95),
                feature_importance='{"temperature": 0.85, "pressure": 0.65, "flow": 0.43, "level": 0.21}',
                detected_at=detected_at,
                resolved_at=detected_at + timedelta(hours=random.randint(1, 12)) if is_resolved else None
            )
            anomalies.append(anomaly)
        
        db.add_all(anomalies)
        db.commit()
        print("✅ 이상 이벤트 데이터 생성 완료 (20개)")
        
        print("\n🎉 모든 더미 데이터 생성 완료!")
        print("\n📊 데이터 요약:")
        print(f"  - 설비: {len(equipments)}개")
        print(f"  - LOT: {len(lots)}개")
        print(f"  - 시계열 데이터: {len(timeseries_data)}개")
        print(f"  - 이상 이벤트: {len(anomalies)}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_dummy_data()