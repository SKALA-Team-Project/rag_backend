from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReportRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    role: str  # operator, manager
    include_sections: Optional[list[str]] = None

class ReportResponse(BaseModel):
    job_id: str
    role: str
    start_date: datetime
    end_date: datetime
    file_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True