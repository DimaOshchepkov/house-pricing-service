import logging
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
from pytest_mock import MockerFixture

from app.api.v1.schemas import BatchPredictionRequest, PredictionRequest
from app.api.v1.service import PredictionService
from app.models import Prediction


@pytest.fixture(autouse=True)
def _mock_settings(mocker: MockerFixture) -> None:
    mocker.patch("app.api.v1.service.settings.artifact_file_name", "model_v1.cbm")


@pytest.fixture
def service(
    mock_model: MagicMock,
    mock_session_factory: MagicMock,
    mock_repository_class: MagicMock,
) -> PredictionService:
    return PredictionService(
        model=mock_model,
        session_factory=mock_session_factory,
        repository_class=mock_repository_class,  # type: ignore
    )


class TestPredictBatch:
    async def test_success(
        self, service: PredictionService, mock_model: MagicMock
    ) -> None:
        mock_model.predict.return_value = np.array([2.5, 1.8])

        batch = BatchPredictionRequest(
            instances=[
                PredictionRequest(
                    MedInc=8.32,
                    HouseAge=41,
                    AveRooms=6.98,
                    AveBedrms=1.02,
                    Population=322,
                    AveOccup=2.55,
                    Latitude=37.88,
                    Longitude=-122.23,
                ),
                PredictionRequest(
                    MedInc=5.0,
                    HouseAge=20,
                    AveRooms=4.0,
                    AveBedrms=1.0,
                    Population=200,
                    AveOccup=2.0,
                    Latitude=34.0,
                    Longitude=-118.0,
                ),
            ]
        )

        response, predictions = await service.predict_batch(batch)

        assert response.scores == [2.5, 1.8]
        assert len(predictions) == 2
        assert predictions[0].score == 2.5
        assert predictions[1].score == 1.8


class TestSavePredictionBg:
    async def test_success(
        self,
        service: PredictionService,
        mock_session: AsyncMock,
        mock_repository_class: MagicMock,
    ) -> None:
        prediction = Prediction(
            request_id="id-1",
            features={},
            score=1.0,
            churn=True,
            model_version="v1",
            latency_ms=5.0,
        )

        await service.save_prediction_bg(prediction)

        mock_repository_class.assert_called_once_with(session=mock_session)

        repo_instance = mock_repository_class.return_value
        repo_instance.save.assert_awaited_once_with(prediction)
        mock_session.commit.assert_awaited_once()

    async def test_error_is_logged_not_raised(
        self,
        service: PredictionService,
        mock_repository_class: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        repo_instance = mock_repository_class.return_value
        repo_instance.save = AsyncMock(side_effect=Exception("DB down"))

        prediction = Prediction(
            request_id="id-2",
            features={},
            score=1.0,
            churn=True,
            model_version="v1",
            latency_ms=5.0,
        )

        with caplog.at_level(logging.ERROR, logger="app.api.v1.service"):
            await service.save_prediction_bg(prediction)

        assert "Failed to save prediction id-2" in caplog.text
        assert "DB down" in caplog.text
