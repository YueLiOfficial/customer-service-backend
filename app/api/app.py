from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router
from app.infra.http_util import init_http_client, close_http_client
from app.infra.database import init_db_engine, close_db_engine

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_http_client()
    init_db_engine()
    yield
    await close_http_client()
    await close_db_engine()

app = FastAPI(lifespan=lifespan)

app.include_router(router)