# Roadmap de Cursos

Webapp comunitaria para descubrir cursos gratuitos, aportarlos al catálogo y
organizarlos en roadmaps personales.

## Cómo levantar

Requisitos: Docker y Docker Compose.

```bash
git clone <tu-repo>
cd Practica_20_10
cp .env.example .env
docker compose up --build
```

Servicios:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000/health
- PostgreSQL: localhost:5432 (credenciales en `.env`)

Verificación rápida:

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/courses
# {"items":[],"total":0,...}
```

Para detener los servicios:

```bash
docker compose down
```

Para borrar también los datos persistidos:

```bash
docker compose down -v
```

## Desarrollo local (sin Docker para la app)

```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (otra terminal)
cd frontend
pnpm install
pnpm dev
```

El proxy de Vite reenvía `/api/*` a `http://localhost:8000`. Para usar otro
destino, definí `VITE_PROXY_TARGET`.

## Variables de entorno

Están documentadas en [`.env.example`](.env.example). Las principales:

| Variable | Descripción |
| --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Credenciales de PostgreSQL |
| `DATABASE_URL` | URL de conexión usada por el backend fuera de Docker |
| `TEST_DATABASE_URL` | Base separada para tests de integración |
| `JWT_SECRET`, `JWT_EXPIRES_MINUTES` | Firma y expiración de tokens |
| `BACKEND_PORT`, `FRONTEND_PORT`, `POSTGRES_PORT` | Puertos expuestos |

## Estructura

```text
backend/    API FastAPI + uv
frontend/   React 19 + Vite + pnpm
docs/       Documentación de producto, diseño técnico y plan
```

## Documentación

- [SPEC](SPEC.md)
- [PRD](docs/PRD.md)
- [TRD](docs/TRD.md)
- [BackendSchema](docs/BackendSchema.md)
- [UX-UI](docs/UX-UI.md)
- [APPFlow](docs/APPFlow.md)
- [Plan de implementación](docs/IMPLEMENTATION_PLAN.md)
