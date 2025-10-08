from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/prediction", tags=["Prediction"])

@router.post("/create", response_model=PredictionResponse)
async def create_prediction(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    예측 수행
    
    - **eq_id**: 설비 ID
    - **prediction_target**: fault, defect_rate, yield, utilization
    - **prediction_horizon**: 30, 60, 120 (분)
    """
    service = PredictionService(db)
    
    try:
        prediction = service.create_prediction(request)
        
        # feature_importance를 dict로 변환
        import json
        feature_importance = json.loads(prediction.feature_importance)
        
        return {
            "job_id": prediction.job_id,
            "eq_id": prediction.eq_id,
            "prediction_target": prediction.prediction_target,
            "prediction_horizon": prediction.prediction_horizon,
            "predicted_value": prediction.predicted_value,
            "probability": prediction.probability,
            "confidence_lower": prediction.confidence_lower,
            "confidence_upper": prediction.confidence_upper,
            "feature_importance": feature_importance,
            "interpretation": prediction.interpretation,
            "created_at": prediction.created_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/{job_id}", response_model=PredictionResponse)
async def get_prediction(
    job_id: str,
    db: Session = Depends(get_db)
):
    """예측 결과 조회"""
    service = PredictionService(db)
    prediction = service.get_prediction_by_job_id(job_id)
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    import json
    feature_importance = json.loads(prediction.feature_importance)
    
    return {
        "job_id": prediction.job_id,
        "eq_id": prediction.eq_id,
        "prediction_target": prediction.prediction_target,
        "prediction_horizon": prediction.prediction_horizon,
        "predicted_value": prediction.predicted_value,
        "probability": prediction.probability,
        "confidence_lower": prediction.confidence_lower,
        "confidence_upper": prediction.confidence_upper,
        "feature_importance": feature_importance,
        "interpretation": prediction.interpretation,
        "created_at": prediction.created_at
    }

@router.get("/history/{eq_id}")
async def get_prediction_history(
    eq_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """예측 이력 조회"""
    service = PredictionService(db)
    history = service.get_prediction_history(eq_id, limit)
    
    return {
        "eq_id": eq_id,
        "total": len(history),
        "predictions": [
            {
                "job_id": p.job_id,
                "prediction_target": p.prediction_target,
                "probability": p.probability,
                "created_at": p.created_at.isoformat()
            }
            for p in history
        ]
    }