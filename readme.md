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

### app/

- **models/** → SQLAlchemy ORM 모델 정의  
  *(equipment.py, lot.py, anomaly.py, prediction.py, report.py 등)*
  -> 데이터베이스 테이블 구조 정의 (SQLAlchemy ORM)

- **schemas/** → Pydantic 스키마 정의  
  *(API 요청/응답 데이터 유효성 검증용)*
  -> 요청(Request)·응답(Response) 데이터 검증용 Pydantic 모델

- **api/v1/** → FastAPI 엔드포인트 라우터 구성  
  *(각 기능별 API — KPI, Equipment, Anomaly, Prediction, Report 등)*
  -> FastAPI 라우터(API endpoint) 정의 (v1 버전 구조)

- **services/** → 비즈니스 로직 계층 분리  
  *(데이터베이스 접근 및 모델 예측 로직 처리)*
  -> 비즈니스 로직 처리 계층 — DB CRUD, 모델 호출 등

- **ml/** → 머신러닝 모델 관리  
  *LSTM, Isolation Forest 등 머신러닝 모델 관리 및 예측 기능

- **utils/** → 공통 유틸리티 함수  
  *(데이터 전처리, 로깅, TEP 데이터 로더 등)*
  -> 데이터 전처리, 로깅, TEP 데이터 로더 등 공통 유틸리티

- **main.py** → FastAPI 앱 초기화 및 DB 연결 설정
---
### app/models/
SQLAlchemy ORM 모델 정의 (DB 테이블 구조)

| 파일 | 주요 기능 |
|------|------------|
| **lot.py** | LOT(공정 단위) 정보 테이블 |
| **equipment.py** | 설비(equipment) 정보 테이블 |
| **timeseries.py** | 시계열 데이터 (태그, 시간, 값) 저장 |
| **anomaly.py** | 이상치 탐지 결과 저장 (z-score, isolation forest 결과 등) |
| **prediction.py** | LSTM 기반 예측 결과 저장 (job_id, 확률, 예측값 등) |
| **report.py** | 리포트 PDF 생성용 데이터 구조 정의 |

---

### app/api/v1/
FastAPI 엔드포인트 정의 (버전 관리된 REST API)

| 파일 | 주요 기능 |
|------|------------|
| **kpi.py** | 공정별 KPI(Key Performance Indicator) 조회 API |
| **equipment.py** | 설비 상태, 센서 데이터 조회 API |
| **anomaly.py** | 이상 감지 결과 조회 및 관리 API |
| **prediction.py** | LSTM 모델 기반 예측 결과 API |
| **report.py** | PDF 리포트 생성 및 다운로드 API |
| **health.py** | 시스템 및 설비의 실시간 건강 상태(Health Score) 조회 API |

---

### app/services/
비즈니스 로직 계층 — DB 쿼리, 모델 호출, 처리 로직 담당

| 파일 | 주요 기능 |
|------|------------|
| **kpi_service.py** | KPI 계산 로직 (평균, 효율, 수율 등) |
| **equipment_service.py** | 설비 데이터 CRUD 및 상태 분석 |
| **anomaly_service.py** | Isolation Forest 기반 이상 탐지 로직 |
| **prediction_service.py** | LSTM 예측 모델 호출 및 결과 저장 |
| **report_service.py** | ReportLab 기반 PDF 리포트 생성 기능 |

---

### app/ml/
머신러닝 관련 모듈 (예측 및 이상 감지)

| 파일 | 주요 기능 |
|------|------------|
| **lstm_model.py** | LSTM 예측 모델 로드 및 예측 수행 |
| **isolation_forest.py** | 이상치 감지용 Isolation Forest 모델 로드 |
| **predictor.py** | 입력 데이터 기반 통합 예측 처리 |
| **feature_importance.py** | 모델 피처 중요도 분석 및 시각화 |

---

### app/utils/
공통 기능 모음 (로깅, 데이터 처리 등)

| 파일 | 주요 기능 |
|------|------------|
| **logger.py** | FastAPI + DB 공통 로깅 설정 |
| **data_processor.py** | 전처리 및 정규화 함수 (MinMax, RMS 등) |
| **tep_loader.py** | TEP(Tennessee Eastman Process) 데이터 로드 유틸리티 |

---

### scripts/
개발 및 운영 보조 스크립트

| 파일 | 주요 기능 |
|------|------------|
| **init_db.py** | 초기 테이블 생성 및 기본 데이터 삽입 |
| **load_dummy_data.py** | 더미 시계열 데이터 로드 스크립트 |
| **train_models.py** | LSTM / Isolation Forest 학습 및 저장 |

---

### data/
머신러닝 모델 및 샘플 데이터 저장소

| 파일 | 주요 기능 |
|------|------------|
| **models/** | 학습된 모델 파일 저장 (예: `lstm_model.pt`, `isolation_forest.pkl`) |
| **tep_train.csv** | 공정 학습용 TEP 데이터 |
| **tep_test.csv** | 공정 테스트용 TEP 데이터 |

---

### tests/
테스트 코드 모음

| 파일 | 주요 기능 |
|------|------------|
| **test_api.py** | 주요 API 엔드포인트 유닛 테스트 |

---

### 루트 파일
| 파일 | 설명 |
|------|------|
| **requirements.txt** | Python 패키지 의존성 목록 |
| **Dockerfile** | FastAPI 백엔드 컨테이너 빌드 설정 |
| **docker-compose.yml** | Backend + MySQL 통합 실행 설정 |
| **.env** | 환경 변수 설정 파일 (DB URL, APP 설정 등) |

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

---
### Health
- **`v1/health` → 시스템 정상 작동 여부**
- **`equipment/{eq_id}/health` → 설비별 정상도(건강 점수)**
