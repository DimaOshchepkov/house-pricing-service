from catboost import CatBoostRegressor
from fastapi import HTTPException, Request

async def get_model(request: Request) -> CatBoostRegressor:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded yet. Service is not ready.",
        )
    
    return model

