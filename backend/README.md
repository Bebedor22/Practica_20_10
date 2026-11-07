# Backend — Roadmap de Cursos

API FastAPI gestionada con `uv`.

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- `GET /health` → `{"status": "ok"}`
- `GET /courses` → listado paginado del catálogo
