from contextlib import asynccontextmanager

from catboost import CatBoostRegressor
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import engine
from app.core.dependencies import get_model
from app.core.exceptions import AppError
from app.schemas import HealthResponse, ReadyResponse
from app.api.v1 import prediction as predictions_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    model = CatBoostRegressor()
    model.load_model("artifacts/" + settings.artifact_file_name)
    app.state.model = model
    yield
    await engine.dispose()


app = FastAPI(title="House pricing", version="0.1.0", lifespan=lifespan)

app.include_router(predictions_v1_router.router)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok"}


@app.get("/ready", response_model=ReadyResponse)
async def ready(model: CatBoostRegressor = Depends(get_model)):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {"status": "ready"}
