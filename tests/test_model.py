import numpy as np
import pytest
from catboost import CatBoostRegressor

from app.core.config import settings


@pytest.fixture
def real_model():
    """Загружаем реальную модель из артефакта"""
    model = CatBoostRegressor()
    model.load_model("artifacts/" + settings.artifact_file_name)
    return model


class TestModelDeterminism:
    def test_model_produces_same_output_for_same_input(
        self, real_model: CatBoostRegressor
    ):

        features = np.array(
            [
                [8.32, 41, 6.98, 1.02, 322, 2.55, 37.88, -122.23],
                [5.0, 20, 4.0, 1.0, 200, 2.0, 34.0, -118.0],
            ]
        )

        predictions_1 = real_model.predict(features)
        predictions_2 = real_model.predict(features)
        predictions_3 = real_model.predict(features)

        np.testing.assert_array_equal(predictions_1, predictions_2)
        np.testing.assert_array_equal(predictions_2, predictions_3)

