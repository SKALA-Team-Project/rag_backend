from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnomalyBase(BaseModel):
    eq_id: str
    fault_code: Optional[str] = None
    severity: str
    
class AnomalyCreate(AnomalyBase):
    lot_id: Optional[str] = None
    z_score: Optional[float] = None
    isolation_score: Optional[float] = None
    prediction_prob: Optional[float] = None
    feature_importance: Optional[str] = None

class AnomalyResponse(AnomalyBase):
    id: int
    lot_id: Optional[str]
    status: str
    z_score: Optional[float]
    isolation_score: Optional[float]
    prediction_prob: Optional[float]
    detected_at: datetime
    
    class Config:
        from_attributes = True

class AnomalyFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    eq_id: Optional[str] = None
    fault_codes: Optional[list[str]] = None
    severities: Optional[list[str]] = None
    statuses: Optional[list[str]] = None