import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Prediction
from app.prediction_repository import PredictionRepository

pytestmark = pytest.mark.integration


class TestPredictionRepository:
    async def test_save_single_and_flush(
        self,
        db_session: AsyncSession,
    ) -> None:
        repository = PredictionRepository(session=db_session)
        prediction = Prediction(
            request_id="test-req-1",
            features={"MedInc": 8.32, "Latitude": 37.88},
            score=2.5,
            churn=True,
            model_version="v1",
            latency_ms=10.5,
        )

        await repository.save(prediction)

        result = await db_session.execute(
            select(Prediction).where(Prediction.request_id == "test-req-1")
        )
        saved_prediction = result.scalar_one_or_none()

        assert saved_prediction is not None
        assert saved_prediction.score == 2.5
        assert saved_prediction.features["MedInc"] == 8.32


    async def test_save_batch(
        self,
        db_session: AsyncSession,
    ) -> None:
        repository = PredictionRepository(session=db_session)
        predictions = [
            Prediction(
                request_id=f"batch-req-{i}",
                features={"MedInc": float(i)},
                score=float(i) * 1.5,
                churn=False,
                model_version="v2",
                latency_ms=5.0,
            )
            for i in range(3)
        ]

        await repository.save_batch(predictions)

        result = await db_session.execute(
            select(Prediction).where(
                Prediction.request_id.in_(["batch-req-0", "batch-req-1", "batch-req-2"])
            )
        )
        saved_predictions = result.scalars().all()

        assert len(saved_predictions) == 3

        scores = {p.score for p in saved_predictions}
        assert scores == {0.0, 1.5, 3.0}
