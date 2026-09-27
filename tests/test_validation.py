import pytest
from pydantic import ValidationError

from app.api.v1.schemas import BatchPredictionRequest, PredictionRequest


def valid_house_data(**overrides) -> dict:

    data = {
        "MedInc": 3.53,
        "HouseAge": 29,
        "AveRooms": 5.23,
        "AveBedrms": 1.05,
        "Population": 1166,
        "AveOccup": 2.82,
        "Latitude": 34.26,
        "Longitude": -118.49,
    }
    data.update(overrides)
    return data


class TestPredictionRequest:
    def test_valid_request(self) -> None:
        req = PredictionRequest(**valid_house_data())

        assert req.MedInc == 3.53
        assert req.HouseAge == 29
        assert req.AveRooms == 5.23
        assert req.AveBedrms == 1.05
        assert req.Population == 1166
        assert req.AveOccup == 2.82
        assert req.Latitude == 34.26
        assert req.Longitude == -118.49

    @pytest.mark.parametrize(
        "field,boundary_value",
        [
            ("MedInc", 0),
            ("AveRooms", 0),
            ("AveBedrms", 0),
            ("AveOccup", 0),
        ],
    )
    def test_gt_zero_rejects_zero(self, field: str, boundary_value: float) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(**{field: boundary_value}))

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == (field,)
        assert errors[0]["type"] == "greater_than"

    @pytest.mark.parametrize(
        "field,negative_value",
        [
            ("MedInc", -1.5),
            ("AveRooms", -0.5),
            ("AveBedrms", -0.1),
            ("AveOccup", -2.0),
        ],
    )
    def test_gt_zero_rejects_negative(self, field: str, negative_value: float) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(**{field: negative_value}))

        errors = exc_info.value.errors()
        assert errors[0]["type"] == "greater_than"

    @pytest.mark.parametrize(
        "field,boundary_value",
        [
            ("HouseAge", -1),
            ("Population", -1),
        ],
    )
    def test_ge_zero_rejects_negative(self, field: str, boundary_value: int) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(**{field: boundary_value}))

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == (field,)
        assert errors[0]["type"] == "greater_than_equal"

    @pytest.mark.parametrize(
        "field,zero_value",
        [
            ("HouseAge", 0),
            ("Population", 0),
        ],
    )
    def test_ge_zero_accepts_zero(self, field: str, zero_value: int) -> None:
        req = PredictionRequest(**valid_house_data(**{field: zero_value}))
        assert getattr(req, field) == zero_value

    def test_latitude_upper_boundary(self) -> None:
        req = PredictionRequest(**valid_house_data(Latitude=90.0))
        assert req.Latitude == 90.0

        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(Latitude=90.1))
        assert exc_info.value.errors()[0]["type"] == "less_than_equal"

    def test_latitude_lower_boundary(self) -> None:
        req = PredictionRequest(**valid_house_data(Latitude=-90.0))
        assert req.Latitude == -90.0

        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(Latitude=-90.1))
        assert exc_info.value.errors()[0]["type"] == "greater_than_equal"

    def test_longitude_upper_boundary(self) -> None:
        req = PredictionRequest(**valid_house_data(Longitude=180.0))
        assert req.Longitude == 180.0

        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(Longitude=180.1))
        assert exc_info.value.errors()[0]["type"] == "less_than_equal"

    def test_longitude_lower_boundary(self) -> None:
        """Longitude должна принимать значения от -180 включительно."""
        req = PredictionRequest(**valid_house_data(Longitude=-180.0))
        assert req.Longitude == -180.0

        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(Longitude=-180.1))
        assert exc_info.value.errors()[0]["type"] == "greater_than_equal"

    def test_wrong_type_string_instead_of_float(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(MedInc="not_a_number"))

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("MedInc",)
        assert (
            "float" in errors[0]["type"].lower()
            or "parsing" in errors[0]["type"].lower()
        )

    def test_wrong_type_string_instead_of_int(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(HouseAge="twenty"))

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("HouseAge",)

    @pytest.mark.parametrize(
        "missing_field",
        [
            "MedInc",
            "HouseAge",
            "AveRooms",
            "AveBedrms",
            "Population",
            "AveOccup",
            "Latitude",
            "Longitude",
        ],
    )
    def test_missing_required_field(self, missing_field: str) -> None:
        data = valid_house_data()
        del data[missing_field]

        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**data)

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == (missing_field,)
        assert errors[0]["type"] == "missing"

    def test_extra_field_is_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(unknown_field=42))

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("unknown_field",)
        assert errors[0]["type"] == "extra_forbidden"

    def test_multiple_extra_fields_are_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(extra1=1, extra2=2, extra3=3))

        errors = exc_info.value.errors()
        assert len(errors) == 3
        assert all(e["type"] == "extra_forbidden" for e in errors)

    def test_bedrooms_exceed_rooms_is_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            PredictionRequest(**valid_house_data(AveRooms=2.0, AveBedrms=3.0))

        errors = exc_info.value.errors()
        assert any(
            "Bedrooms" in str(e["msg"]) and "cannot exceed" in str(e["msg"])
            for e in errors
        )

    def test_bedrooms_equal_rooms_is_allowed(self) -> None:
        req = PredictionRequest(**valid_house_data(AveRooms=2.0, AveBedrms=2.0))
        assert req.AveBedrms == 2.0
        assert req.AveRooms == 2.0

    def test_bedrooms_less_than_rooms_is_allowed(self) -> None:
        req = PredictionRequest(**valid_house_data(AveRooms=5.0, AveBedrms=2.0))
        assert req.AveBedrms < req.AveRooms


class TestBatchPredictionRequest:
    def test_valid_batch_single_instance(self) -> None:
        batch = BatchPredictionRequest(
            instances=[PredictionRequest(**valid_house_data())]
        )

        assert len(batch.instances) == 1
        assert isinstance(batch.instances[0], PredictionRequest)

    def test_valid_batch_multiple_instances(self) -> None:
        instances = [
            PredictionRequest(**valid_house_data(MedInc=i)) for i in range(1, 6)
        ]
        batch = BatchPredictionRequest(instances=instances)

        assert len(batch.instances) == 5

    def test_empty_list_is_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            BatchPredictionRequest(instances=[])

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("instances",)
        assert errors[0]["type"] == "too_short"

    def test_max_length_exceeded(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            BatchPredictionRequest(
                instances=[PredictionRequest(**valid_house_data())] * 1001
            )

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("instances",)
        assert errors[0]["type"] == "too_long"

    def test_max_length_boundary(self) -> None:
        batch = BatchPredictionRequest(
            instances=[PredictionRequest(**valid_house_data())] * 1000
        )
        assert len(batch.instances) == 1000

    def test_extra_fields_in_batch_rejected(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            BatchPredictionRequest(
                instances=[PredictionRequest(**valid_house_data())],
                extra_field="bad",  # type: ignore
            )

        errors = exc_info.value.errors()
        assert errors[0]["loc"] == ("extra_field",)
        assert errors[0]["type"] == "extra_forbidden"
