# Changelog

Todas las entradas siguen [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el versionado semántico.

## [Unreleased]

## [v0.2.0] - 2026-10-27

### Added

- Persistencia con SQLAlchemy: modelos `User`, `Course` y `Roadmap`, sesión de
  base de datos y repositorios de cursos y roadmaps.
- Autenticación mínima con JWT de 24 horas: registro, login y `GET /auth/me`.
- Endpoints de catálogo: listado paginado con búsqueda y categoría, detalle,
  aporte autenticado y validación por instructor/admin.
- Validaciones de dominio para cursos, aportes y roadmaps, con códigos de error
  estables.
- Tests unitarios, de integración con PostgreSQL y del hook `useCourses` con
  Vitest.
- Datos de prueba idempotentes y credenciales de admin, instructor y usuario.
- Healthchecks de PostgreSQL, backend y frontend en Docker Compose.

### Changed

- El estado del curso pasa de `validated` booleano a `status`
  (`draft`, `in_review`, `published`, `rejected`); `validated` se expone como
  valor calculado en la API.
- Las imágenes de backend y frontend usan builds multi-stage; el frontend de
  producción se sirve con Nginx y hace proxy de `/api`.
- El README documenta Docker, desarrollo local, tests y datos de prueba.

### Security

- Passwords con bcrypt (costo 12) y JWT firmados con expiración configurable.

## [v0.1.0] - 2026-10-27

### Added

- Scaffold del proyecto: estructura `backend/`, `frontend/`, documentación,
  `.gitignore`, `.env.example` y `docker-compose.yml`.
- Backend mínimo con FastAPI + uv: `GET /health` y `GET /courses` paginado.
- Frontend mínimo con React 19 + Vite + pnpm: pantalla de catálogo con estados
  de carga, error y lista vacía, consumiendo `/api/courses`.
- Docker Compose de desarrollo con PostgreSQL 18.6, backend y frontend.
- README con instrucciones verificables de levantamiento.
