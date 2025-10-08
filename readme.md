# 프로젝트 디렉토리 구조

```bash
tep-dashboard-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── equipment.py
│   │   ├── lot.py
│   │   ├── timeseries.py
│   │   ├── anomaly.py
│   │   ├── prediction.py
│   │   └── report.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── equipment.py
│   │   ├── anomaly.py
│   │   ├── prediction.py
│   │   └── report.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── kpi.py
│   │       ├── equipment.py
│   │       ├── anomaly.py
│   │       ├── prediction.py
│   │       └── report.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── kpi_service.py
│   │   ├── equipment_service.py
│   │   ├── anomaly_service.py
│   │   ├── prediction_service.py
│   │   └── report_service.py
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── lstm_model.py
│   │   ├── isolation_forest.py
│   │   ├── predictor.py
│   │   └── feature_importance.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── data_processor.py
│       ├── logger.py
│       └── tep_loader.py
│
├── data/
│   ├── models/
│   │   ├── lstm_model.pt
│   │   └── isolation_forest.pkl
│   ├── tep_train.csv
│   └── tep_test.csv
│
├── scripts/
│   ├── init_db.py
│   ├── load_dummy_data.py
│   └── train_models.py
│
├── tests/
│   └── test_api.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env
```

## FastAPI 백엔드 프로젝트 구조 설계

`app/` 디렉토리 내 주요 모듈을 계층적으로 분리하여 유지보수성을 강화

###  디렉토리 구성

- **models/** → SQLAlchemy ORM 모델 정의  
  *(equipment.py, lot.py, anomaly.py, prediction.py, report.py 등)*

- **schemas/** → Pydantic 스키마 정의  
  *(API 요청/응답 데이터 유효성 검증용)*

- **api/v1/** → FastAPI 엔드포인트 라우터 구성  
  *(각 기능별 API — KPI, Equipment, Anomaly, Prediction, Report 등)*

- **services/** → 비즈니스 로직 계층 분리  
  *(데이터베이스 접근 및 모델 예측 로직 처리)*

- **ml/** → 머신러닝 모델 관리  
  *(LSTM, Isolation Forest 모델 로드 및 예측 수행)*

- **utils/** → 공통 유틸리티 함수  
  *(데이터 전처리, 로깅, TEP 데이터 로더 등)*

- **main.py** → FastAPI 앱 초기화 및 DB 연결 설정

환경 설정 및 DB 연동 
- **config.py**
 → .env 환경 변수를 기반으로 Pydantic Settings 구성 (APP_NAME, DATABASE_URL, DEBUG, CORS_ORIGINS 등) 
- **database.py** → SQLAlchemy 엔진 및 세션 구성
---

#### Docker Compose 사용

1. Docker Compose로 MySQL + Backend 실행
- docker-compose up -d

2. 로그 확인
- docker-compose logs -f backend

3. MySQL 접속 확인
- docker-compose exec db mysql -u user -p password 
- 입력: password

4. API 문서 확인: http://localhost:8000/docs

#### 데이터베이스 초기화

- MySQL 실행 확인# Docker Compose 사용 시

docker-compose up -d db

#### 테이블 생성
- python scripts/init_db.py

#### 더미 데이터 생성
- python scripts/load_dummy_data.py

#### ML 모델 학습 (선택사항)
- python scripts/train_models.py

#### Docker Compose로 전체 실행
- docker-compose up -d

#### 재배포
- docker compose down

- docker compose up -d --build

- docker compose logs -f backend
