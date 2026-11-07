# Roadmap de Cursos

Webapp comunitaria para descubrir cursos gratuitos, aportarlos al catálogo y
organizarlos en roadmaps personales.

## Requisitos

- Docker + Docker Compose v2 (también funciona con Podman y el provider de
  Compose).
- Para desarrollo local sin Docker: Python 3.12+, [uv](https://docs.astral.sh/uv/)
  y Node 24 + pnpm.

## Levantar con Docker

```bash
git clone <tu-repo>
cd Practica_20_10
cp .env.example .env
docker compose up --build
```

Servicios:

| Servicio | URL | Descripción |
| --- | --- | --- |
| Frontend | http://localhost:5173 | Build de React servido por Nginx |
| API | http://localhost:8000/health | FastAPI |
| Swagger | http://localhost:8000/docs | Documentación interactiva |
| PostgreSQL | localhost:5432 | Credenciales en `.env` |

El frontend consume la API a través de `/api/*`; Nginx hace el proxy hacia el
backend. Los contenedores esperan los healthchecks: verificá el estado con
`docker compose ps`.

Si el puerto `5432` ya está ocupado, cambiá `POSTGRES_PORT` en `.env` y
actualizá `DATABASE_URL` y `TEST_DATABASE_URL` con el mismo puerto.

### Datos de prueba

Al arrancar, el backend crea las tablas y carga datos idempotentes si
`SEED_DATA=true` (valor por defecto):

| Rol | Email | Contraseña |
| --- | --- | --- |
| Admin | `admin@roadmap.local` | `Admin123!` |
| Instructor | `instructor@roadmap.local` | `Instructor123!` |
| Usuario | `user@roadmap.local` | `User123!` |

También se cargan seis cursos publicados y un aporte pendiente de validación.

### Verificación rápida

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl "http://localhost:8000/courses?limit=2"
# {"items":[...],"total":6,"page":1,"limit":2,...}

curl "http://localhost:5173/api/courses?limit=1"
# La misma respuesta, a través del proxy de Nginx
```

Login y ruta protegida:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@roadmap.local","password":"Admin123!"}'
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

Levantá solo PostgreSQL:

```bash
docker compose up -d postgres
```

Backend:

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend, en otra terminal:

```bash
cd frontend
pnpm install
pnpm dev
```

El proxy de Vite reenvía `/api/*` a `http://localhost:8000`. Para usar otro
destino, definí `VITE_PROXY_TARGET`.

## Tests

Backend (requiere PostgreSQL levantado; usa `TEST_DATABASE_URL`):

```bash
cd backend
uv run pytest
```

Frontend:

```bash
cd frontend
pnpm test
```

Calidad del frontend:

```bash
cd frontend
pnpm lint
pnpm build
```

## Variables de entorno

Están documentadas en [`.env.example`](.env.example). Las principales:

| Variable | Descripción |
| --- | --- |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Credenciales de PostgreSQL |
| `DATABASE_URL` | URL de conexión usada por el backend fuera de Docker |
| `TEST_DATABASE_URL` | Base separada para tests de integración |
| `JWT_SECRET`, `JWT_EXPIRES_MINUTES` | Firma y expiración de tokens |
| `SEED_DATA` | Carga datos de prueba al iniciar (`true`/`false`) |
| `BACKEND_PORT`, `FRONTEND_PORT`, `POSTGRES_PORT` | Puertos expuestos |

## Estructura

```text
backend/    API FastAPI + uv, tests unitarios y de integración
frontend/   React 19 + Vite + pnpm, tests con Vitest
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
