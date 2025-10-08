from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class LotStatus(enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Lot(Base):
    __tablename__ = "lots"
    
    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(String(50), unique=True, nullable=False, index=True)
    eq_id = Column(String(50), ForeignKey("equipments.eq_id"))
    line = Column(String(50))
    stage = Column(String(50))
    status = Column(SQLEnum(LotStatus), default=LotStatus.WAITING)
    defect_rate = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())