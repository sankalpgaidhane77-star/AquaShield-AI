from fastapi import APIRouter, HTTPException
from backend.app.schemas import PredictRequest, PredictResponse
from backend.app.services.ml_service import ml_service

router = APIRouter(tags=["ML Prediction"])

@router.post("/predict", response_model=PredictResponse)
async def predict_water_quality(request: PredictRequest):
    """
    Classifies water quality into Safe, Moderate, or Dangerous using the trained Random Forest engine.
    Returns confidence score and actionable safety recommendations.
    """
    try:
        result = ml_service.predict_water_quality(
            ph=request.ph,
            turbidity=request.turbidity,
            tds=request.tds,
            temperature=request.temperature
        )
        return PredictResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
