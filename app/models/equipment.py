from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class EquipmentType(enum.Enum):
    REACTOR = "reactor"
    STRIPPER = "stripper"
    COMPRESSOR = "compressor"
    CONDENSER = "condenser"
    COOLER = "cooler"

class Equipment(Base):
    __tablename__ = "equipments"
    
    id = Column(Integer, primary_key=True, index=True)
    eq_id = Column(String(50), unique=True, nullable=False, index=True)
    type = Column(SQLEnum(EquipmentType), nullable=False)
    name = Column(String(100), nullable=False)
    health_score = Column(Float, default=100.0)
    utilization = Column(Float, default=0.0)
    status = Column(String(20), default="normal")
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())  # MySQL용