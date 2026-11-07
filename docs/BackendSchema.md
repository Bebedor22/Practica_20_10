# BackendSchema.md — Schema de Base de Datos y API

Estado: implementado en `v0.2.0`. Los puntos marcados como pendientes no forman
parte del alcance actual.

## Modelos de datos (PostgreSQL 18.6)

### Tabla: users

| Columna | Tipo | Restricciones | Descripción |
| ------- | ---- | ------------- | ----------- |
| id | SERIAL | PK, not null | Identificador único |
| name | VARCHAR(100) | not null | Nombre completo del usuario |
| email | VARCHAR(255) | UNIQUE, not null | Email de login, normalizado a minúsculas por la API |
| password_hash | VARCHAR(255) | not null | Hash bcrypt (costo 12) |
| role | VARCHAR(20) | default 'user', CHECK (role IN ('user','instructor','admin')) | Rol de usuario |
| created_at | TIMESTAMPTZ | default NOW() | Cuándo se creó el registro |

La validación de formato de email se hace en la API (Pydantic), no con un CHECK
de base de datos.

### Tabla: courses

| Columna | Tipo | Restricciones | Descripción |
| ------- | ---- | ------------- | ----------- |
| id | SERIAL | PK, not null | Identificador único del curso |
| title | VARCHAR(200) | not null | Título del curso |
| version | VARCHAR(50) | not null | Ej. "v1.0", "2026 Update" |
| year | SMALLINT | not null, CHECK (year >= 2000) | Año de edición/publicación |
| category | VARCHAR(50) | not null, CHECK en categorías permitidas | Rubro/categoría |
| theme | VARCHAR(100) | not null | Tema específico (ej. "JavaScript", "UI/UX") |
| url | VARCHAR(500) | not null, UNIQUE | Enlace web activo |
| instructor | VARCHAR(200) | not null | Docente o disertante |
| has_quiz | BOOLEAN | default false | Si el curso tiene cuestionarios |
| requires_exam | BOOLEAN | default false | Si requiere examen final |
| extends_certificate | BOOLEAN | default false | Si extiende certificado |
| organization | VARCHAR(200) | nullable | Organización que lo avala (opcional) |
| status | VARCHAR(20) | default 'in_review', CHECK en estados permitidos | Estado de revisión |
| user_id | INTEGER | FK → users.id, not null, ON DELETE CASCADE | Quién aportó el curso |
| created_at | TIMESTAMPTZ | default NOW() | Cuándo fue añadido |

Categorías: Programación, Diseño, Marketing, Negocios, Artes, Ciencias, Otros.

Estados: `draft`, `in_review`, `published`, `rejected`.

`validated` no se persiste: la API lo expone como `status == 'published'` para
compatibilidad con el frontend.

### Tabla: roadmaps

| Columna | Tipo | Restricciones | Descripción |
| ------- | ---- | ------------- | ----------- |
| id | SERIAL | PK, not null | Identificador único |
| user_id | INTEGER | FK → users.id, not null, ON DELETE CASCADE | Dueño del roadmap |
| name | VARCHAR(100) | not null | Nombre del roadmap (ej. "Desarrollo Web") |
| course_id | INTEGER | FK → courses.id, not null, ON DELETE CASCADE | Curso en el roadmap |
| position | INTEGER | not null | Orden secuencial en el roadmap |
| created_at | TIMESTAMPTZ | default NOW() | Cuándo se añadió |

Restricción única `(user_id, course_id)`: un usuario no repite curso en sus
roadmaps. La persistencia y las reglas están implementadas; los endpoints HTTP
quedan pendientes.

## Endpoints de API FastAPI

### Auth

| Método | Endpoint | Body | Respuesta | Estado |
| ------ | -------- | ---- | --------- | ------ |
| POST | `/auth/register` | `{name, email, password}` | 201 `{id, name, email, role}` | Implementado |
| POST | `/auth/login` | `{email, password}` | 200 `{access_token, token_type, user}` | Implementado |
| GET | `/auth/me` | Bearer token | 200 `{id, name, email, role}` | Implementado |
| POST | `/auth/recovery` | `{email}` | 200 `{message}` | Pendiente |
| GET | `/auth/recovery/confirm/{token}` | token en URL | 200 formulario | Pendiente |
| POST | `/auth/recovery/confirm` | `{token, new_password}` | 200 `{message}` | Pendiente |

JWT HS256 con expiración de 24 horas (`JWT_EXPIRES_MINUTES=1440`). El token se
envía como `Authorization: Bearer <token>`.

### Courses — Catálogo comunitario

| Método | Endpoint | Query/Body | Respuesta | Estado |
| ------ | -------- | ---------- | --------- | ------ |
| GET | `/courses` | `page`, `limit`, `q`, `category` | 200 `Page<Course>` | Implementado |
| GET | `/courses/{id}` | path id | 200 `Course` publicado | Implementado |
| POST | `/courses` | datos del curso + Bearer token | 201 `Course` en `in_review` | Implementado |
| PUT | `/courses/{id}/validate` | `{approved: boolean}` + Bearer token | 200 `Course` actualizado | Implementado |

`GET /courses` solo devuelve cursos `published`. La respuesta paginada incluye
`items`, `total`, `page`, `limit`, `totalPages`, `hasNext` y `hasPrev`.

`POST /courses` requiere autenticación, valida las reglas de negocio, verifica
URL duplicada y asigna `user_id` del token. `PUT /courses/{id}/validate` solo
permite instructores/admin, prohíbe la autovalidación y exige estado
`in_review`.

### Roadmaps — Personales

Modelo, reglas y repositorio implementados. Endpoints `GET`, `POST`, `PUT` y
`DELETE` pendientes para el próximo release.

## Validaciones de negocio

### Curso (`POST /courses`)

- title: requerido, 3–200 caracteres
- version: requerido, máximo 50 caracteres
- year: requerido, entre 2000 y el año actual
- category: obligatoria y dentro de las categorías permitidas
- theme: requerido, 2–100 caracteres
- url: requerida, http/https válida, única (case-insensitive y sin `/` final)
- instructor: requerido, 2–200 caracteres
- organization: opcional, máximo 200 caracteres
- booleanos: `has_quiz`, `requires_exam`, `extends_certificate`
- `user_id` se toma del usuario autenticado, no del body

Códigos de violación: `TITLE_*`, `VERSION_*`, `YEAR_*`, `CATEGORY_*`,
`THEME_*`, `URL_*`, `INSTRUCTOR_*`, `ORGANIZATION_TOO_LONG`.

### Validación de aportes

- Rol permitido: `instructor` o `admin` (`ROLE_NOT_ALLOWED`)
- El autor no puede validar su propio aporte (`SELF_VALIDATION_FORBIDDEN`)
- El curso debe estar `in_review` (`COURSE_NOT_IN_REVIEW`)

### Roadmap (reglas de repositorio)

- Solo cursos `published` (`COURSE_NOT_PUBLISHED`)
- Curso inexistente (`COURSE_NOT_FOUND`)
- Curso repetido (`COURSE_ALREADY_IN_ROADMAP`)
- Reordenamiento inválido (`INVALID_REORDER`)
- Curso ausente al remover (`COURSE_NOT_IN_ROADMAP`)

## Respuestas de error

FastAPI devuelve los errores de negocio dentro de `detail`, con un código
estable:

```json
{
  "detail": {
    "error": "forbidden",
    "code": "SELF_VALIDATION_FORBIDDEN"
  }
}
```

Las violaciones de reglas de curso devuelven `422`:

```json
{
  "detail": {
    "error": "validation failed",
    "details": [
      {"field": "year", "code": "YEAR_BEFORE_2000", "message": "..."}
    ]
  }
}
```

| Código HTTP | Escenario |
| ----------- | --------- |
| 401 | Token faltante/inválido (`AUTH_001`) o credenciales inválidas (`INVALID_CREDENTIALS`) |
| 403 | Rol sin permiso o autovalidación (`ROLE_NOT_ALLOWED`, `SELF_VALIDATION_FORBIDDEN`) |
| 404 | Curso inexistente (`COURSE_NOT_FOUND`) |
| 409 | Email ya registrado (`EMAIL_ALREADY_REGISTERED`) o URL duplicada en carrera (`URL_DUPLICATE`) |
| 422 | Body inválido o violaciones de reglas de curso |

## Rate limiting

Pendiente para el próximo release: `POST /auth/login` máximo 5 intentos por 15
minutos por IP y `POST /auth/register` máximo 10 por hora.

## Datos de prueba

Con `SEED_DATA=true`, el arranque crea de forma idempotente:

- `admin@roadmap.local` / `Admin123!` (admin)
- `instructor@roadmap.local` / `Instructor123!` (instructor)
- `user@roadmap.local` / `User123!` (usuario)
- Seis cursos publicados y un aporte pendiente de validación
