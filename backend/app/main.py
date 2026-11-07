from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.courses.router import router as courses_router

app = FastAPI(title="Roadmap de Cursos API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(courses_router)
