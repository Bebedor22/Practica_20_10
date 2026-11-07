# IMPLEMENTATION_PLAN.md — Plan de Implementación

## Versión: 1.0 (Instancia A) / 1.1 (post-aprobado, Instancia B) / 1.2 (workflow de clase)

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
  - [ ] Modelos User en PostgreSQL (id, name, email, password_hash, role)
  - [ ] Endpoints FastAPI: register, login, recovery cycle completo
  - [ ] Password hashing con bcrypt mínimo costo 10
  - [ ] Rate limiting en endpoint login (máx 5 intentos/15min)
  - [ ] JWT tokens con expiración 24h
  - [ ] Middleware de protección de rutas (dependency FastAPI)
  - [ ] Login screen UX (mobile-first, form, link recovery)
- **Checklist "bien"**: auth flow end-to-end: register → login → protected route → recovery

#### Módulo 3: Catálogo de cursos comunitario (P0.3)
- **Tiempo estimado**: 6 horas (depende de P0.2)
- **Tareas**:
  - [ ] Modelo Course en PostgreSQL (todos los campos definidos en BackendSchema)
  - [ ] Endpoints GET /courses (paginado, filtros category/theme/validated)
  - [ ] Endpoint GET /courses/{id} detail
  - [ ] POST /courses para aportar nuevo curso
  - [ ] PUT /courses/{id}/validate endpoint
  - [ ] Lista de categorías/rubros definidas: Programación, Diseño, Marketing, Negocios, Artes, Ciencias, Otros
  - [ ] Tarjetas de curso con diseño Material (UX-UI.md)
  - [ ] Filtros y búsqueda en frontend
  - [ ] Paginación en listing y tables
- **Checklist "bien"**: listing con paginación, filtros functional, tarjetas con diseño visual

#### Módulo 4: Roadmap personal (P0.4)
- **Tiempo estimado**: 5 horas (depende de P0.3)
- **Tareas**:
  - [ ] Modelo Roadmap en PostgreSQL (user_id, course_id, position, nombre)
  - [ ] Endpoints GET /roadmaps (lista del usuario actual)
  - [ ] POST /roadmaps crear nuevo roadmap
  - [ ] PUT /roadmaps/{id}/reorder reordenar cursos
  - [ ] DELETE /roadmaps/{id}/courses/{course_id} remover curso
  - [ ] Visualización roadmap: secuencia de fichas de curso
  - [ ] Botón "Añadir a roadmap" en detail curso
  - [ ] Declaración "¿Has tomado este curso?" toggle
  - [ ] Roadmap screen con diseño Material
- **Checklist "bien"**: roadmap creation, add course flow, reorder functionality

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
  - [ ] README.md con comandos exactos verifiables
  - [ ] `docker compose up` → PostgreSQL + backend + frontend levantan
  - [ ] Instrucciones de setup: `pnpm install`, `uv sync`, variables de entorno
  - [ ] Datos de prueba/seed para testing manual
  - [ ] URLs de prueba y credenciales de usuario de test
  - [ ] .dockerignore configurado
  - [ ] IMPLEMENTATION_PLAN.md actualizado con tareas [x]/[ ] y referencia a ramas/commits
- **Checklist "bien"**: `docker compose up` levanta los 3 servicios, stories P0 funcionan

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

### Actualización del plan durante el desarrollo

- Cada tarea completada se marca en IMPLEMENTATION_PLAN.md con `[x]` y referencia:
  - Rama: `feature/nombre-tarea`
  - Commit: hash completo o corto
  - Fecha: YYYY-MM-DD
- Al mergear a main, el IMPLEMENTATION_PLAN.md se actualiza con el estado final
- Antes de solicitar aprobación (Instancia A): todo el docs/ debe estar committed y pushado
- Después de aprobación (Instancia B): código debe levantar en máquina limpia tal como especifica el DoD