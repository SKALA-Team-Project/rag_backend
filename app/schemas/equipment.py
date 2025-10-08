from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EquipmentBase(BaseModel):
    eq_id: str
    name: str
    type: str

class EquipmentResponse(EquipmentBase):
    health_score: float
    utilization: float
    status: str
    last_updated: datetime
    
    class Config:
        from_attributes = True

class TimeSeriesData(BaseModel):
    timestamp: datetime
    value: float

class TimeSeriesResponse(BaseModel):
    eq_id: str
    tag_name: str
    unit: str
    data: list[TimeSeriesData]
    normal_range: dict