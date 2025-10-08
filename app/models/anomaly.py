from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from app.database import Base
import enum

class Severity(enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AnomalyStatus(enum.Enum):
    UNCONFIRMED = "unconfirmed"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(String(50), nullable=True)
    eq_id = Column(String(50), ForeignKey("equipments.eq_id"), nullable=False, index=True)
    fault_code = Column(String(20))
    severity = Column(SQLEnum(Severity), default=Severity.WARNING)
    status = Column(SQLEnum(AnomalyStatus), default=AnomalyStatus.UNCONFIRMED)
    z_score = Column(Float)
    isolation_score = Column(Float)
    prediction_prob = Column(Float)
    feature_importance = Column(Text)  # MySQL TEXT 타입
    detected_at = Column(DateTime, default=func.now(), index=True)
    resolved_at = Column(DateTime, nullable=True)