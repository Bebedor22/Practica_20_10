# IMPLEMENTATION_PLAN.md — Plan de Implementación

## Versión: 1.0 (Instancia A) / 1.1 (post-aprobado, Instancia B)

### Flujo de Git documentado

- **Tipo de flujo**: GitHub Flow (rama corta sobre main, PRs revisados)
- **Ramas por instancia**:
  - `main`: siempre estable, solo código probado y aprobado
  - `docs-instancia-a`: rama para todos los 7 documentos de documentación
  - `feature/*`: ramas por funcionalidad P0 (ej. `feature/auth-login`, `feature/courses-catalog`)
  - `release/instancia-b`: rama creada tras aprobación del T1 (correo APROBADO)
- **Convención de commits**: Conventional Commits 100%
  - `docs: add PRD user stories` (nunca `docs: cambios` o `wip`)
  - `feat: add course model` (nueva funcionalidad)
  - `fix: rate limit login endpoint` (bug fix)
  - `style: format TRD.md` (formato, no lógica)
  - `refactor: reorganize folder structure` (arquitectura screaming)
- **Merge flow**:
  1. Commits en rama feature/*
  2. Push a origin
  3. Crear Pull Request contra main (o release/instancia-b)
  4. Revisión requerida (mínimo 1 approval)
  5. Merge con squash o merge commit preservando historia
- **Etiquetas**: `v0.1-instancia-a` tras aprobación docs, `v1.0-instancia-b` tras MVP completo

### Módulos P0 (orden de dependencia)

#### Módulo 1: Configuración y estructura base (P0.1)
- **Tiempo estimado**: 2 horas
- **Tareas**:
  - [ ] Configurar repositorio con estructura inicial
  - [ ] `git init`, `.gitignore` para React/Vite/pnpm + FastAPI/uv
  - [ ] `README.md` con instrucciones de setup inicial
  - [ ] Estructura de carpetas `src/` con arquitectura screaming
  - [ ] Configurar Vite + React 19 + TypeScript
  - [ ] Configurar FastAPI + uv con entorno virtual
  - [ ] Docker Compose básico (servicios: db, backend, frontend)
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