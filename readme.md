# Docker Compose 사용

1. Docker Compose로 MySQL + Backend 실행
docker-compose up -d

*# 2. 로그 확인*
docker-compose logs -f backend

*# 3. MySQL 접속 확인*
docker-compose exec db mysql -u user -p

*# password 입력: password# 4. API 문서 확인# http://localhost:8000/docs* 

# 데이터베이스 초기화

MySQL 실행 확인# Docker Compose 사용 시

docker-compose up -d db

# 테이블 생성*
python scripts/init_db.py

# 더미 데이터 생성*
python scripts/load_dummy_data.py

# ML 모델 학습 (선택사항)
python scripts/train_models.py

# Docker Compose로 전체 실행
docker-compose up -d

# 재배포
docker compose down

docker compose up -d --build

docker compose logs -f backend
