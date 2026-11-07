# Changelog

Todas las entradas siguen [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el versionado semántico.

## [Unreleased]

## [v0.1.0] - 2026-10-27

### Added

- Scaffold del proyecto: estructura `backend/`, `frontend/`, documentación,
  `.gitignore`, `.env.example` y `docker-compose.yml`.
- Backend mínimo con FastAPI + uv: `GET /health` y `GET /courses` paginado.
- Frontend mínimo con React 19 + Vite + pnpm: pantalla de catálogo con estados
  de carga, error y lista vacía, consumiendo `/api/courses`.
- Docker Compose de desarrollo con PostgreSQL 18.6, backend y frontend.
- README con instrucciones verificables de levantamiento.
