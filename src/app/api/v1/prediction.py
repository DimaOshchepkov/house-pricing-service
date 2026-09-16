from catboost import CatBoostRegressor
from fastapi import APIRouter, BackgroundTasks, Depends

from app.api.v1.schemas import (
    BatchPredictionRequest,
    PredictionRequest,
)
from app.api.v1.service import PredictionService
from app.core.dependencies import get_model

router = APIRouter(prefix="/api/v1", tags=["v1: Predictions"])


def get_prediction_service(
    model: CatBoostRegressor = Depends(get_model),
) -> PredictionService:
    return PredictionService(model=model)


@router.post("/predict")
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    service: PredictionService = Depends(get_prediction_service),
):
    return await service.predict_single(request, background_tasks)


@router.post("/predict/batch")
async def predict_batch(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    service: PredictionService = Depends(get_prediction_service),
):
    return await service.predict_batch(request, background_tasks)
