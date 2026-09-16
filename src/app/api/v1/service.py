import logging
import time
import uuid

from catboost import CatBoostRegressor
from fastapi import BackgroundTasks

from app.api.v1.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.core.config import settings
from app.core.database import get_session
from app.core.exceptions import DatabaseError, PredictionServiceError
from app.models import Prediction

logger = logging.getLogger(__name__)

FEATURE_NAMES = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]


class PredictionService:
    def __init__(self, model: CatBoostRegressor):
        self.model = model
        self.model_version = settings.artifact_file_name

    async def predict_single(
        self,
        request: PredictionRequest,
        background_tasks: BackgroundTasks,
    ) -> PredictionResponse:
        t0 = time.perf_counter()

        try:
            features_list = [self._features_to_list(request)]
            score = float(self.model.predict(features_list)[0])
        except Exception as e:
            logger.error(f"Model prediction failed: {e}")
            raise PredictionServiceError(str(e))

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        request_id = str(uuid.uuid4())
        features_dict = self._features_to_dict(request)

        background_tasks.add_task(
            self._save_prediction_to_db,
            request_id=request_id,
            features=features_dict,
            score=score,
            latency_ms=latency_ms,
        )

        return PredictionResponse(
            score=score,
            request_id=request_id,
            latency_ms=latency_ms,
        )

    async def predict_batch(
        self,
        request: BatchPredictionRequest,
        background_tasks: BackgroundTasks,
    ) -> BatchPredictionResponse:
        t0 = time.perf_counter()

        try:
            features_list = [self._features_to_list(item) for item in request.instances]
            scores = self.model.predict(features_list).tolist()
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            raise PredictionServiceError(str(e))

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        request_id = str(uuid.uuid4())

        items = [
            (self._features_to_dict(item), float(score))
            for item, score in zip(request.instances, scores)
        ]

        background_tasks.add_task(
            self._save_batch_predictions_to_db,
            request_id=request_id,
            items=items,
            latency_ms=latency_ms,
        )

        return BatchPredictionResponse(
            scores=scores,
            request_id=request_id,
            latency_ms=latency_ms,
        )

    async def _save_prediction_to_db(
        self,
        request_id: str,
        features: dict,
        score: float,
        latency_ms: float,
    ):
        try:
            async with get_session() as session:
                session.add(
                    Prediction(
                        request_id=request_id,
                        features=features,
                        score=score,
                        churn=True,
                        model_version=self.model_version,
                        latency_ms=latency_ms,
                    )
                )
        except Exception as e:
            logger.error(f"Failed to save prediction {request_id}: {e}")
            raise DatabaseError(str(e))

    async def _save_batch_predictions_to_db(
        self,
        request_id: str,
        items: list[tuple[dict, float]],
        latency_ms: float,
    ):
        try:
            async with get_session() as session:
                records = [
                    Prediction(
                        request_id=str(uuid.uuid4()),
                        batch_id=request_id,
                        features=features,
                        score=score,
                        churn=True,
                        model_version=self.model_version,
                        latency_ms=latency_ms,
                    )
                    for features, score in items
                ]
                session.add_all(records)
        except Exception as e:
            logger.error(f"Failed to save batch {request_id}: {e}")
            raise DatabaseError(str(e))

    def _features_to_list(self, instance) -> list:
        return [getattr(instance, name) for name in FEATURE_NAMES]

    def _features_to_dict(self, instance) -> dict:
        return {name: getattr(instance, name) for name in FEATURE_NAMES}
