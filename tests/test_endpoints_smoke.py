import pytest
from fastapi.testclient import TestClient

from app.main import app


pytestmark = pytest.mark.smoke


SAMPLE_PAYLOAD = {
    "MedInc": 8.32, "HouseAge": 41, "AveRooms": 6.98, "AveBedrms": 1.02,
    "Population": 322, "AveOccup": 2.55, "Latitude": 37.88, "Longitude": -122.23,
}


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


class TestPredictEndpoint:
    def test_predict_returns_200(self, client: TestClient) -> None:
        response = client.post("/api/v1/predict", json=SAMPLE_PAYLOAD)
        assert response.status_code == 200

        data = response.json()
        assert "score" in data
        assert "request_id" in data
        assert isinstance(data["score"], float)

    def test_invalid_payload_returns_422(self, client: TestClient) -> None:
        response = client.post("/api/v1/predict", json={"foo": "bar"})
        assert response.status_code == 422


class TestPredictBatchEndpoint:
    def test_predict_batch_returns_200(self, client: TestClient) -> None:
        payload = {"instances": [SAMPLE_PAYLOAD, SAMPLE_PAYLOAD]}
        response = client.post("/api/v1/predict/batch", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "scores" in data
        assert len(data["scores"]) == 2
