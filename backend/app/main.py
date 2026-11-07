from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.courses.router import router as courses_router
from app.db.init import init_db
from app.db.seed import seed_data


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    if get_settings().seed_data:
        seed_data()
    yield


app = FastAPI(
    title="Roadmap de Cursos API",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(courses_router)
