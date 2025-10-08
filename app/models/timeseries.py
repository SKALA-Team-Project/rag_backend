from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base

class TimeSeriesTag(Base):
    __tablename__ = "tags_timeseries"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)  # MySQL용 DateTime
    eq_id = Column(String(50), ForeignKey("equipments.eq_id"), nullable=False, index=True)
    tag_name = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    
    # MySQL 복합 인덱스
    __table_args__ = (
        Index('ix_timeseries_eq_tag_time', 'eq_id', 'tag_name', 'timestamp'),
    )