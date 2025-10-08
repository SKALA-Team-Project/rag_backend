from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, nullable=False)
    eq_id = Column(String(50), ForeignKey("equipments.eq_id"), nullable=False)
    prediction_target = Column(String(50))
    prediction_horizon = Column(Integer)
    predicted_value = Column(Float)
    probability = Column(Float)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    feature_importance = Column(Text)  # MySQL TEXT
    interpretation = Column(String(500))
    created_at = Column(DateTime, default=func.now())