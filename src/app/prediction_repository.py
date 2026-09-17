from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Prediction


class PredictionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, prediction: Prediction) -> None:
        self.session.add(prediction)
        await self.session.flush()

    async def save_batch(self, predictions: list[Prediction]) -> None:
        self.session.add_all(predictions)
        await self.session.flush()
