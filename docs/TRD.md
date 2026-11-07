# TRD — Technical Requirements Document

## Stack tecnológico

- **Frontend**: React 19 + Vite 8 + pnpm 11 + TypeScript 7
- **Servidor de frontend**: Nginx (build de producción)
- **Backend**: FastAPI 0.162 + uv
- **Base de datos**: PostgreSQL 18.6
- **Infraestructura**: Docker + Docker Compose con healthchecks
- **Lenguaje backend**: Python 3.14
- **Lenguaje frontend**: TypeScript + React; Node 24 para desarrollo y build

## Mobile-first con mejora progresiva

- Estilos base **sin media queries** en los estilosglobals
- A partir de la capa base, usar `@media (min-width: ...)` **únicamente** para agregar o mejorar estilos a medida que la pantalla crece
- Nunca usar media queries para "arreglar" el diseño base en pantallas más pequeñas
- Breakpoints recomendados: `min-width: 640px` (mobile small), `min-width: 768px` (tablet), `min-width: 1024px` (desktop)

## Paginación

- Todas las consultas de listado (catalogo de courses, roadmaps usuario) deben estar paginadas
- Parámetros de API: `page` (número), `limit` (items por página, máximo 50)
- Respuesta de API debe incluir: `items`, `total`, `page`, `totalPages`, `hasNext`, `hasPrev`
- Links de navegación: URL con parámetros de página para navegación client-side y server-side

## Screaming Architecture

- Estructura de carpetas por dominio de negocio, no por tipo de archivo
- Ejemplo de estructura:
  ```
  src/
  ├── courses/          # dominio course
  │   ├── components/
  │   ├── hooks/
  │   ├── api/
  │   └── types.ts
  ├── roadmaps/         # dominio roadmap
  │   ├── components/
  │   ├── hooks/
  │   └── api/
  ├── auth/             # dominio authentication
  │   ├── components/
  │   └── api/
  └── shared/           # componentes y utils compartidos
- Cada dominio contiene todo lo necesario (UI, lógica, API, tipos)

## Apariencia y experiencia (Google Material)

- Azul primario: `#4285F4` (Google Blue)
- Espaciado base: 8px system (8, 16, 24, 32, 40, 48, 64)
- Tipografía: Inter o Roboto, jerarquía clara H1-H6
- Sombras: `0 2px 4px rgba(0,0,0,0.1)` para componentes elevados
- Bordes redondeados: `4px` para componentes, `2px` para inputs
- Estados de componente definidos: hover, focus, active, disabled, error
- Consistencia visual en todos los formularios y tarjetas de curso

## Seguridad de autenticación

- **Password hashing**: bcrypt costo 12 (implementado)
- **Rate limiting**: en el endpoint de login, máximo 5 intentos por 15 minutos por IP (pendiente)
- **Headers de seguridad**: CSP, X-Content-Type-Options, X-Frame-Options (pendiente)
- **HTTPS** obligatorio en producción (pendiente de despliegue)
- **Tokens**: JWT HS256 firmados con secret key, expiración 24h (implementado)

## Endpoints de API (FastAPI)

### Auth

- `POST /auth/register` {name, email, password} → 201 user created (implementado)
- `POST /auth/login` {email, password} → 200 {access_token, token_type, user} (implementado)
- `GET /auth/me` → 200 user data, requiere Bearer token (implementado)
- `POST /auth/recovery` {email} → 200 {sent link} (pendiente)
- `GET /auth/recovery/confirm/{token}` → 200 formulario (pendiente)
- `POST /auth/recovery/confirm` {token, new_password} → 200 updated (pendiente)

### Courses (catálogo comunitario)

- `GET /courses` → lista paginada con filtros `q` y `category` (implementado)
- `GET /courses/{id}` → 200 detalle de curso publicado (implementado)
- `POST /courses` → 201 curso en `in_review`, requiere Bearer token (implementado)
- `PUT /courses/{id}/validate` {approved} → 200 curso aprobado/rechazado; solo instructor/admin y no autor (implementado)
- Filtros `theme`/`validated` y baja/edición de cursos (pendientes)

### Roadmaps (personales)

- Modelo, reglas y repositorio persistente (implementado)
- `GET /roadmaps`, `POST /roadmaps`, `PUT /roadmaps/{id}/reorder` y
  `DELETE /roadmaps/{id}/courses/{course_id}` (pendientes)

## Modelos de datos (PostgreSQL)

### Table: users

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| id | SERIAL PK | not null |
| name | VARCHAR(100) | not null |
| email | VARCHAR(255) | unique, not null; normalizado y validado por la API |
| password_hash | VARCHAR(255) | not null (bcrypt) |
| created_at | TIMESTAMP | default now() |
| role | VARCHAR(20) | default 'user' (user, instructor, admin) |

### Table: courses

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| id | SERIAL PK | not null |
| title | VARCHAR(200) | not null |
| version | VARCHAR(50) | not null |
| year | SMALLINT | not null, check(year >= 2000) |
| category | VARCHAR(50) | not null, enum: Programación, Diseño, Marketing, Negocios, Artes, Ciencias, Otros |
| theme | VARCHAR(100) | not null (ej. JavaScript, UI/UX, etc.) |
| url | VARCHAR(500) | not null, valid URL |
| instructor | VARCHAR(200) | not null |
| has_quiz | BOOLEAN | default false |
| requires_exam | BOOLEAN | default false |
| extends_certificate | BOOLEAN | default false |
| organization | VARCHAR(200) | nullable (quién lo avala) |
| status | VARCHAR(20) | default 'in_review'; draft, in_review, published, rejected |
| user_id | INTEGER FK → users | not null (quien aportó) |
| created_at | TIMESTAMP | default now() |

`validated` no se persiste: se calcula como `status == 'published'` y se expone
en la API por compatibilidad con el contrato del frontend.

### Table: roadmaps

| Campo | Tipo | Restricciones |
|-------|------|---------------|
| id | SERIAL PK | not null |
| user_id | INTEGER FK → users | not null |
| name | VARCHAR(100) | not null |
| course_id | INTEGER FK → courses | not null |
| position | INTEGER | not null (orden en el roadmap) |
| created_at | TIMESTAMP | default now() |
| PRIMARY KEY (id, user_id, course_id) | | | (un usuario puede tener un curso una vez en su roadmap)

## Versionado y dependencias

- FastAPI con uv para gestor de dependencias
- React 19 con TypeScript, Vite 8, pnpm 11 y Vitest 5
- PostgreSQL 18.6 como versión stable documentada en TRD
- Docker Compose con servicios `postgres`, `backend` y `frontend`, healthchecks
  y dependencias por estado saludable
- Imágenes multi-stage: Python slim para la API y Nginx para el frontend
- `.dockerignore` en backend y frontend para excluir `.venv`, `node_modules`,
  `dist`, cachés y tests