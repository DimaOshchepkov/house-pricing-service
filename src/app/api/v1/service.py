import logging
import time
import uuid

from catboost import CatBoostRegressor
from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.v1.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.core.config import settings
from app.core.exceptions import DatabaseError, PredictionServiceError
from app.models import Prediction
from app.prediction_repository import PredictionRepository

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
    def __init__(
        self,
        model: CatBoostRegressor,
        session_factory: async_sessionmaker,
    ):
        self.model = model
        self.session_factory = session_factory
        self.model_version = settings.artifact_file_name

    async def predict_single(
        self,
        request: PredictionRequest,
        background_tasks: BackgroundTasks,
    ) -> PredictionResponse:
        """
        Raises:
            PredictionServiceError: _description_
        """
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

        prediction = Prediction(
            request_id=request_id,
            features=features_dict,
            score=score,
            churn=True,
            model_version=self.model_version,
            latency_ms=latency_ms,
        )

        background_tasks.add_task(
            self._save_prediction,
            prediction=prediction,
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
        """
        Raises:
            PredictionServiceError:
        """
        t0 = time.perf_counter()

        try:
            features_list = [self._features_to_list(item) for item in request.instances]
            scores = self.model.predict(features_list).tolist()
        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            raise PredictionServiceError(str(e))

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        request_id = str(uuid.uuid4())

        predictions = [
            Prediction(
                request_id=str(uuid.uuid4()),
                features=self._features_to_dict(item),
                score=float(score),
                churn=True,
                model_version=self.model_version,
                latency_ms=latency_ms,
            )
            for item, score in zip(request.instances, scores)
        ]

        background_tasks.add_task(
            self._save_batch,
            predictions=predictions,
        )

        return BatchPredictionResponse(
            scores=scores,
            request_id=request_id,
            latency_ms=latency_ms,
        )

    async def _save_prediction(self, prediction: Prediction) -> None:
        try:
            async with self.session_factory() as session:
                repository = PredictionRepository(session=session)
                await repository.save(prediction)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save prediction {prediction.request_id}: {e}")
            raise DatabaseError(str(e))

    async def _save_batch(self, predictions: list[Prediction]) -> None:
        try:
            async with self.session_factory() as session:
                repository = PredictionRepository(session=session)
                await repository.save_batch(predictions)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save batch: {e}")
            raise DatabaseError(str(e))

    def _features_to_list(self, instance) -> list[str]:
        return [getattr(instance, name) for name in FEATURE_NAMES]

    def _features_to_dict(self, instance) -> dict:
        return {name: getattr(instance, name) for name in FEATURE_NAMES}
