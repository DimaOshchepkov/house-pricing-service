from pydantic import BaseModel, Field, model_validator


class PredictionRequest(BaseModel):
    MedInc: float = Field(
        description="Median income in block group (in $10,000)",
        examples=[3.53],
        gt=0,
    )

    HouseAge: int = Field(
        description="Median house age in block group (years)",
        examples=[29],
        ge=0,
    )

    AveRooms: float = Field(
        description="Average number of rooms per household",
        examples=[5.23],
        gt=0,
    )

    AveBedrms: float = Field(
        description="Average number of bedrooms per household",
        examples=[1.05],
        gt=0,
    )

    Population: int = Field(
        description="Block group population",
        examples=[1166],
        ge=0,
    )

    AveOccup: float = Field(
        description="Average number of household members",
        examples=[2.82],
        gt=0,
    )

    Latitude: float = Field(
        description="Latitude coordinate (degrees)",
        examples=[34.26],
        ge=-90.0,
        le=90.0,
    )

    Longitude: float = Field(
        description="Longitude coordinate (degrees)",
        examples=[-118.49],
        ge=-180.0,
        le=180.0,
    )

    @model_validator(mode="after")
    def check_logical_consistency(self):
        if self.AveBedrms > self.AveRooms:
            raise ValueError(
                f"Bedrooms ({self.AveBedrms}) cannot exceed rooms ({self.AveRooms})"
            )
        return self


class BatchPredictionRequest(BaseModel):
    instances: list[PredictionRequest] = Field(
        description="List of houses to predict",
        min_length=1,
        max_length=1000,
    )


class PredictionResponse(BaseModel):
    score: float = Field(description="Predicted house value (in $100,000)")
    request_id: str = Field(description="Unique request identifier")
    latency_ms: float = Field(description="Processing time in milliseconds")


class BatchPredictionResponse(BaseModel):
    scores: list[float] = Field(description="List of predicted values")
    request_id: str = Field(description="Unique request identifier")
    latency_ms: float = Field(description="Batch processing time in milliseconds")
