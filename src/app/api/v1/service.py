import logging
import time
import uuid

from catboost import CatBoostRegressor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.v1.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
)
from app.core.config import settings
from app.core.exceptions import PredictionServiceError
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
        session_factory: async_sessionmaker[AsyncSession],
        repository_class: type[PredictionRepository] = PredictionRepository,
    ):
        self.model = model
        self.model_version = settings.artifact_file_name
        self.session_factory = session_factory
        self.repository_class = repository_class

    def predict_single(
        self,
        request: PredictionRequest,
    ):
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
            raise PredictionServiceError(str(e)) from None

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

        response = PredictionResponse(
            score=score,
            request_id=request_id,
            latency_ms=latency_ms,
        )

        return response, prediction

    def predict_batch(self, request: BatchPredictionRequest):
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
            raise PredictionServiceError(str(e)) from None

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
            for item, score in zip(request.instances, scores, strict=True)
        ]

        response = BatchPredictionResponse(
            scores=scores,
            request_id=request_id,
            latency_ms=latency_ms,
        )

        return response, predictions

    def _features_to_list(self, instance) -> list[str]:
        return [getattr(instance, name) for name in FEATURE_NAMES]

    def _features_to_dict(self, instance) -> dict:
        return {name: getattr(instance, name) for name in FEATURE_NAMES}

    async def save_prediction_bg(self, prediction: Prediction) -> None:
        try:
            async with self.session_factory() as session:
                repository = self.repository_class(session=session)
                await repository.save(prediction)
                await session.commit()
        except Exception as e:
            logger.error(
                f"Failed to save prediction {prediction.request_id} in background: {e}"
            )

    async def save_batch_bg(self, predictions: list[Prediction]) -> None:
        try:
            async with self.session_factory() as session:
                repository = self.repository_class(session=session)
                await repository.save_batch(predictions)
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save batch in background: {e}")
