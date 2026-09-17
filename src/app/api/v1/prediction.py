from typing import Annotated

from catboost import CatBoostRegressor
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.v1.schemas import (
    BatchPredictionRequest,
    PredictionRequest,
)
from app.api.v1.service import PredictionService
from app.core.database import async_session, get_session
from app.core.dependencies import get_model
from app.prediction_repository import PredictionRepository

router = APIRouter(prefix="/api/v1", tags=["v1: Predictions"])


ModelDep = Annotated[CatBoostRegressor, Depends(get_model)]


def get_prediction_service(
    model: ModelDep,
) -> PredictionService:
    return PredictionService(model=model, session_factory=async_session)


ServiceDep = Annotated[PredictionService, Depends(get_prediction_service)]


@router.post("/predict")
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    service: ServiceDep,
):
    return await service.predict_single(request, background_tasks)


@router.post("/predict/batch")
async def predict_batch(
    request: BatchPredictionRequest,
    background_tasks: BackgroundTasks,
    service: PredictionService = Depends(get_prediction_service),
):
    return await service.predict_batch(request, background_tasks)
