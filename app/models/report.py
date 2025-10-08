from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum

class ReportRole(enum.Enum):
    OPERATOR = "operator"
    MANAGER = "manager"

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, nullable=False)
    role = Column(SQLEnum(ReportRole), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    file_path = Column(String(500))
    sections = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())