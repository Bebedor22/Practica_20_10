# IMPLEMENTATION_PLAN.md — Plan de Implementación

## Versión: 1.0 (Instancia A) / 1.1 (post-aprobado, Instancia B) / 1.2 (workflow de clase) / 1.3 (cierre v0.2.0)

### Flujo de Git documentado

- **Tipo de flujo**: integración con rama `dev` y releases taggeados en `main`.
- **Ramas**:
  - `main`: solo recibe `dev` al cerrar un release; cada release lleva tag `vX.Y.Z`.
  - `dev`: rama de integración; recibe los merges de todas las ramas de trabajo.
  - `feat/T{N}-descripcion-corta`: una feature o ticket, nace desde `dev`.
  - `fix/descripcion-corta`: un fix, nace desde `dev`.
- **Convención de commits**: Conventional Commits 100% (`feat:`, `fix:`, `docs:`,
  `docker:`, `chore:`, `test:`, `refactor:`). Sin `wip` ni mensajes vagos.
- **Merge flow**:
  1. Crear la rama de trabajo desde `dev`.
  2. Commits convencionales en la rama.
  3. Merge `--no-ff` de vuelta a `dev` y borrar la rama.
  4. Al cerrar release: actualizar CHANGELOG en `dev`, merge `dev → main` y tag anotado.
- **Versionado**:
  - `v0.y.z` mientras el producto es inestable.
  - MAJOR por cambios incompatibles, MINOR por features compatibles y PATCH por fixes.
- **Etiquetas**: `v0.1.0` (scaffold) y `v0.2.0` (testing, Docker multi-stage y cierre).

### Registro de tickets de clase — Scaffold (22/10/2026)

- [x] **T1 — Setup del workflow + scaffold del repo**
  - Rama: `feat/T1-scaffold-estructura` · Commit: `d995949`
- [x] **T2 — Backend mínimo (FastAPI + uv)**
  - Rama: `feat/T2-backend-minimo` · Commit: `3c1eb55`
- [x] **T3 — Frontend mínimo (React + Vite + pnpm)**
  - Rama: `feat/T3-frontend-minimo` · Commit: `18f6740`
- [x] **T4 — Docker Compose de desarrollo (simple)**
  - Rama: `feat/T4-docker-compose-dev` · Commit: `af7b66d`
- [x] **T5 — Release v0.1.0**
  - Merge `dev → main` · Tag: `v0.1.0`

### Registro de tickets de clase — Testing, Docker y cierre (27/10/2026)

- [x] **T6 — Tests unitarios de reglas de curso**
  - Rama: `feat/T6-tests-unitarios-curso`
  - Commits: `7c8df10`, `0b3ec4b`, `8637326` · Merge: `a73d49f`
- [x] **T7 — Tests unitarios de reglas de roadmap**
  - Rama: `feat/T7-tests-unitarios-roadmap`
  - Commits: `345abc0`, `8036952` · Merge: `d3a7a8d`
- [x] **T8 — Tests unitarios de validación de aportes**
  - Rama: `feat/T8-tests-unitarios-aportes`
  - Commits: `a8a6e7c`, `7f54369` · Merge: `c3f7818`
- [x] **T9 — Persistencia y tests de integración con PostgreSQL**
  - Rama: `feat/T9-integration-cursos`
  - Commit: `65fb991` · Merge: `71148e0`
- [x] **T10 — Autenticación JWT y endpoints de cursos**
  - Rama: `feat/T10-auth-endpoints`
  - Commit: `2cfdb16` · Merge: `3bebd6d`
- [x] **T11 — Tests del hook de catálogo con Vitest**
  - Rama: `feat/T11-tests-hook-cursos`
  - Commit: `3c36cba` · Merge: `9de2cb1`
- [x] **T12 — Docker multi-stage del backend**
  - Rama: `feat/T12-docker-backend-multistage`
  - Commit: `a752680` · Merge: `a528c59`
- [x] **T13 — Inicialización de base de datos y seed idempotente**
  - Rama: `feat/T13-seed-datos`
  - Commit: `1bc92cf` · Merge: `d28c1af`
- [x] **T14 — Docker multi-stage del frontend con Nginx**
  - Rama: `feat/T14-docker-frontend`
  - Commit: `af48ae5` · Merge: `d910770`
- [x] **T15 — Healthchecks de Compose y README verificable**
  - Rama: `feat/T15-healthchecks-readme`
  - Commit: `3469deb` · Merge: `2ecfeea`
- [x] **T16 — Release v0.2.0**
  - Merge `dev → main` · Tag: `v0.2.0`

### Módulos P0 (orden de dependencia)

#### Módulo 1: Configuración y estructura base (P0.1)
- **Tiempo estimado**: 2 horas
- **Estado**: completado en el release `v0.1.0` (tickets T1–T5)
- **Tareas**:
  - [x] Configurar repositorio con estructura inicial
  - [x] `git init`, `.gitignore` para React/Vite/pnpm + FastAPI/uv
  - [x] `README.md` con instrucciones de setup inicial
  - [x] Estructura de carpetas `src/` con arquitectura screaming
  - [x] Configurar Vite + React 19 + TypeScript
  - [x] Configurar FastAPI + uv con entorno virtual
  - [x] Docker Compose básico (servicios: db, backend, frontend)
- **Checklist "bien"**: repo con historia git, estructura de carpetas, README verifiable

#### Módulo 2: Autenticación básica (P0.2)
- **Tiempo estimado**: 4 horas (depende de P0.1)
- **Tareas**:
  - [x] Modelos User en PostgreSQL (id, name, email, password_hash, role)
  - [x] Endpoints FastAPI: register, login
  - [x] Password hashing con bcrypt costo 12
  - [ ] Rate limiting en endpoint login (máx 5 intentos/15min)
  - [x] JWT tokens con expiración 24h
  - [x] Middleware de protección de rutas (dependency FastAPI)
  - [ ] Login screen UX (mobile-first, form, link recovery)
  - [ ] Ciclo de recuperación de contraseña
- **Checklist "bien"**: register → login → ruta protegida implementado; recovery y rate limiting quedan pendientes.

#### Módulo 3: Catálogo de cursos comunitario (P0.3)
- **Tiempo estimado**: 6 horas (depende de P0.2)
- **Tareas**:
  - [x] Modelo Course en PostgreSQL con estado y `validated` calculado
  - [x] Endpoints GET /courses (paginado, filtros category/q)
  - [x] Endpoint GET /courses/{id} detail
  - [x] POST /courses para aportar nuevo curso
  - [x] PUT /courses/{id}/validate endpoint
  - [x] Lista de categorías/rubros definidas: Programación, Diseño, Marketing, Negocios, Artes, Ciencias, Otros
  - [x] Tarjetas de curso con diseño Material (UX-UI.md)
  - [x] Filtros y búsqueda en frontend
  - [x] Paginación en listing
  - [ ] Filtros por theme/validated y pantalla de detalle de curso
- **Checklist "bien"**: listing con paginación, filtros category/q y tarjetas visuales implementados.

#### Módulo 4: Roadmap personal (P0.4)
- **Tiempo estimado**: 5 horas (depende de P0.3)
- **Tareas**:
  - [x] Modelo Roadmap y repositorio en PostgreSQL (user_id, course_id, position, nombre)
  - [ ] Endpoints GET /roadmaps (lista del usuario actual)
  - [ ] POST /roadmaps crear nuevo roadmap
  - [ ] PUT /roadmaps/{id}/reorder reordenar cursos
  - [ ] DELETE /roadmaps/{id}/courses/{course_id} remover curso
  - [ ] Visualización roadmap: secuencia de fichas de curso
  - [ ] Botón "Añadir a roadmap" en detail curso
  - [ ] Declaración "¿Has tomado este curso?" toggle
  - [ ] Roadmap screen con diseño Material
- **Checklist "bien"**: modelo y reglas listos; endpoints y UI quedan pendientes.

#### Módulo 5: Integración end-to-end (P0.5)
- **Tiempo estimado**: 4 horas (depende de P0.3 + P0.4)
- **Tareas**:
  - [ ] Flujo completo: login → browse catalog → add course → add to roadmap
  - [ ] Declaración de toma en roadmap
  - [ ] Persistencia correcta en base de datos
  - [ ] Estados de loading y error en todas las UI
  - [ ] Mobile-first: verificar en viewport <640px
  - [ ] Paginación funcionando en listing y roadmap
- **Checklist "bien"**: historia de usuario US-001 a US-008 funcionando end-to-end

#### Módulo 6: README y documentación verificable (P0.6)
- **Tiempo estimado**: 3 horas (paralelo o después de P0.5)
- **Tareas**:
  - [x] README.md con comandos exactos verifiables
  - [x] `docker compose up` → PostgreSQL + backend + frontend levantan
  - [x] Instrucciones de setup: `pnpm install`, `uv sync`, variables de entorno
  - [x] Datos de prueba/seed para testing manual
  - [x] URLs de prueba y credenciales de usuario de test
  - [x] .dockerignore configurado en backend y frontend
  - [x] IMPLEMENTATION_PLAN.md actualizado con tareas [x]/[ ] y referencia a ramas/commits
- **Checklist "bien"**: `docker compose up` levanta los 3 servicios con healthchecks; las historias P0 completas quedan para el próximo release.

### Definition of Done (Instancia B)

Hecho (Definition of Done de la Instancia B) cuando, en una máquina limpia:

```
git clone <tu-repo>
# seguir tu README
docker compose up
# → PostgreSQL + backend + frontend levantan
# → las historias P0 del PRD funcionan end-to-end desde la UI
```

Criterios adicionales de Done:

1. **README verificable**: `docker compose up` levanta los 3 servicios sin errores
2. **Historias P0 completadas**: US-001 a US-008 funcionando desde la UI
3. **Git history observable**: commits con convencional commits, flujo documentado visible
4. **IMPLEMENTATION_PLAN actualizado**: tareas marcadas con [x]/[ ] y referencias a ramas/commits
5. **Mobile-first verificado**: UI correcta en viewport <640px, sin media queries base
6. **Paginación verificada**: listing de cursos y roadmaps con paginación funcional
7. **Screaming Architecture**: estructura de carpetas comunica dominio del negocio
8. **Error handling**: todos los endpoints devuelven errores estructurados apropiados
9. **bcrypt passwords**: todos los passwords en base de datos tienen hash bcrypt costo >= 10
10. **Rate limiting**: endpoint login protegido máximo 5 intentos/15min

### Alcance de v0.2.0

Implementado en este release:

- Persistencia PostgreSQL, migración por `create_all` y seed idempotente.
- Auth mínima con bcrypt costo 12, JWT de 24h y protección de rutas.
- Catálogo: listado paginado, búsqueda, categoría, detalle, aporte y validación.
- Reglas y repositorio de roadmaps con tests.
- Docker multi-stage, Nginx con proxy `/api`, healthchecks y README verificable.
- Tests unitarios, integración con PostgreSQL y hook `useCourses`.

Pendiente para el próximo release (fuera del alcance de la clase):

- Recuperación de contraseña, rate limiting y pantalla de login.
- Endpoints y UI de roadmaps, alta de curso desde la UI y detalle de curso.
- Filtros por `theme`/`validated` y flujo end-to-end de US-001 a US-008.
- Migraciones versionadas (Alembic) y headers de seguridad/HTTPS.

### Actualización del plan durante el desarrollo

- Cada tarea completada se marca en IMPLEMENTATION_PLAN.md con `[x]` y referencia:
  - Rama: `feature/nombre-tarea`
  - Commit: hash completo o corto
  - Fecha: YYYY-MM-DD
- Al mergear a main, el IMPLEMENTATION_PLAN.md se actualiza con el estado final
- Antes de solicitar aprobación (Instancia A): todo el docs/ debe estar committed y pushado
- Después de aprobación (Instancia B): código debe levantar en máquina limpia tal como especifica el DoD