from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionRequest(BaseModel):
    eq_id: str
    prediction_target: str  # fault, defect_rate, yield, utilization
    prediction_horizon: int  # 30, 60, 120 (분)
    
class PredictionResponse(BaseModel):
    job_id: str
    eq_id: str
    prediction_target: str
    prediction_horizon: int
    predicted_value: float
    probability: float
    confidence_lower: float
    confidence_upper: float
    feature_importance: dict
    interpretation: str
    created_at: datetime
    
    class Config:
        from_attributes = True