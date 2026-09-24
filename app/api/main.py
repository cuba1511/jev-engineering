from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import documents, health, tickets
from app.jev import Jev


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with Jev() as jev:
        app.state.jev = jev
        yield


app = FastAPI(title="Jev Engineering", lifespan=lifespan)
app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(documents.router)
