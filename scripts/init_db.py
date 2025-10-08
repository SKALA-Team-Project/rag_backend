import sys
sys.path.append('.')

from app.database import engine, Base
from app.models import *

def init_database():
    """데이터베이스 초기화"""
    print("🗄️  데이터베이스 테이블 생성 중...")
    
    # 모든 테이블 삭제 (주의!)
    Base.metadata.drop_all(bind=engine)
    
    # 모든 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    print("✅ 테이블 생성 완료!")
    print("\n생성된 테이블:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")

if __name__ == "__main__":
    init_database()