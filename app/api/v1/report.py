from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import get_db
from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/report", tags=["Report"])

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db)
):
    """
    보고서 생성
    
    - **start_date**: 시작 날짜
    - **end_date**: 종료 날짜
    - **role**: operator (현장 엔지니어) or manager (관리자)
    """
    service = ReportService(db)
    
    try:
        report = service.generate_report(request)
        
        return {
            "job_id": report.job_id,
            "role": report.role.value,
            "start_date": report.start_date,
            "end_date": report.end_date,
            "file_path": report.file_path,
            "created_at": report.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.get("/{job_id}", response_model=ReportResponse)
async def get_report_info(
    job_id: str,
    db: Session = Depends(get_db)
):
    """보고서 정보 조회"""
    service = ReportService(db)
    report = service.get_report_by_job_id(job_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "job_id": report.job_id,
        "role": report.role.value,
        "start_date": report.start_date,
        "end_date": report.end_date,
        "file_path": report.file_path,
        "created_at": report.created_at
    }

@router.get("/{job_id}/download")
async def download_report(
    job_id: str,
    db: Session = Depends(get_db)
):
    """보고서 다운로드"""
    service = ReportService(db)
    report = service.get_report_by_job_id(job_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    return FileResponse(
        path=report.file_path,
        filename=os.path.basename(report.file_path),
        media_type='application/pdf'
    )

@router.get("/list/all")
async def get_report_list(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """보고서 목록 조회"""
    service = ReportService(db)
    reports = service.get_report_list(limit)
    
    return {
        "total": len(reports),
        "reports": [
            {
                "job_id": r.job_id,
                "role": r.role.value,
                "start_date": r.start_date.isoformat(),
                "end_date": r.end_date.isoformat(),
                "created_at": r.created_at.isoformat()
            }
            for r in reports
        ]
    }