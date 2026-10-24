# BackendSchema.md — Schema de Base de Datos y API

## Modelos de datos (PostgreSQL 18.6)

### Tabla: users

| Columna | Tipo | Restricciones | Descripción |
| ------- | ---- | ------------- | ----------- |
| id | SERIAL | PK, not null | Identificador único |
| name | VARCHAR(100) | not null | Nombre completo del usuario |
| email | VARCHAR(255) | UNIQUE, not null, CHECK (position('@' IN email) > 0) | Email de login |
| password_hash | VARCHAR(255) | not null | Hash bcrypt (costo >= 10) |
| role | VARCHAR(20) | default 'user', CHECK (role IN ('user','instructor','admin')) | Rol de usuario |
| created_at | TIMESTAMP | default NOW() | Cuándo se creó el registro |

### Tabla: courses

| Columna | Tipo | Restricciones | Descripción |
| ------- | ---- | ------------- | ----------- |
| id | SERIAL | PK, not null | Identificador único del curso |
| title | VARCHAR(200) | not null | Título del curso |
| version | VARCHAR(50) | not null | Ej. "v1.0", "2024 Update" |
| year | SMALLINT | not null, CHECK (year >= 2000) | Año de edición/publicación |
| category | VARCHAR(50) | not null, CHECK (category IN ('Programación','Diseño','Marketing','Negocios','Artes','Ciencias','Otros')) | Rubro/categoría |
| theme | VARCHAR(100) | not null | Tema específico (ej. "JavaScript", "UI/UX") |
| url | VARCHAR(500) | not null, CHECK (url LIKE 'http%%' OR url LIKE 'https%%') | Enlace web activo |
| instructor | VARCHAR(200) | not null | Docente o disertante |
| has_quiz | BOOLEAN | default false | Si el curso tiene cuestionarios |
| requires_exam | BOOLEAN | default false | Si requiere examen final |
| extends_certificate | BOOLEAN | default false | Si extiende certificado |
| organization | VARCHAR(200) | nullable | Organización que lo avala (opcional) |
| validated | BOOLEAN | default false | Si pasó validación comunitaria |
| user_id | INTEGER | FK → users.id, not null | Quién aportó el curso |
| created_at | TIMESTAMP | default NOW() | Cuándo fue añadido |

### Tabla: roadmaps

| Columna | Tipo | Restricciones | Descripción |
| ------- | ---- | ------------- | ----------- |
| id | SERIAL | PK, not null | Identificador único |
| user_id | INTEGER | FK → users.id, not null | Dueño del roadmap |
| name | VARCHAR(100) | not null | Nombre del roadmap (ej. "Desarrollo Web") |
| course_id | INTEGER | FK → courses.id, not null | Curso en el roadmap |
| position | INTEGER | not null | Orden secuencial en el roadmap |
| created_at | TIMESTAMP | default NOW() | Cuándo se añadió |
| PRIMARY KEY (id, user_id, course_id) | | | Un usuario no repite curso en su roadmap |

## Endpoints de API FastAPI

### Auth (todos requieren los headers apropiados)

| Método | Endpoint | Body | Respuesta | Descripción |
| ------ | -------- | ---- | -------- | ----------- |
| POST | `/auth/register` | `{name, email, password}` | 201 `{user_id, name, email}` | Registrar nuevo usuario |
| POST | `/auth/login` | `{email, password}` | 200 `{access_token, token_type, user}` | Login con sesión |
| POST | `/auth/recovery` | `{email}` | 200 `{message: "email sent"}` | Solicitar recuperación |
| GET | `/auth/recovery/confirm/{token}` | token en URL | 200 `{form: true}` | Formulario nueva password |
| POST | `/auth/recovery/confirm` | `{token, new_password}` | 200 `{message: "updated"}` | Confirmar nueva password |
| GET | `/auth/me` | headers auth | 200 `{user data}` | Datos del usuario actual |

### Courses — Catálogo Comunitario

| Método | Endpoint | Query/Body | Respuesta | Descripción |
| ------ | -------- | -------- | -------- | ----------- |
| GET | `/courses` | `{page, limit, category, theme, validated?}` | 200 `{items, total, page, totalPages}` | Listar cursos con paginación y filtros |
| GET | `/courses/{id}` | path id | 200 `{course}` | Detalle de un curso específico |
| POST | `/courses` | `{title, version, year, category, theme, url, instructor, has_quiz, requires_exam, extends_certificate, organization, user_id}` | 201 `{course}` | Aportar nuevo curso (pending validation) |
| PUT | `/courses/{id}/validate` | sin body o `{validated: true}` | 200 `{validated}` | Validar curso (admin/peer) |

### Roadmaps — Personales

| Método | Endpoint | Body | Respuesta | Descripción |
| ------ | -------- | ---- | -------- | ----------- |
| GET | `/roadmaps` | headers auth | 200 `{roadmaps list}` | Listar roadmaps del usuario actual |
| POST | `/roadmaps` | `{name, course_ids[], order[]}` | 201 `{roadmap}` | Crear nuevo roadmap |
| PUT | `/roadmaps/{id}/reorder` | `{course_ids[]}` | 200 `{reordered}` | Reordenar cursos en roadmap |
| DELETE | `/roadmaps/{id}` | headers auth | 200 `{deleted}` | Eliminar roadmap |

## Rate limiting

- Endpoint `POST /auth/login`: máximo 5 intentos por 15 minutos por IP
- Endpoint `POST /auth/register`: máximo 10 intentos por hora por IP
- Respuesta 429 con header `Retry-After` y body `{error: "too many attempts"}`
- Almacenamiento: in-memory con Redis opcional o solo IP tracking en PostgreSQL

## Validaciones de negocio

### Validaciones de curso (POST /courses)

- title: requerido, mínimo 3 caracteres, máximo 200
- version: requerido, formato sugiere versión semántica o text
- year: requerido, entero, rango 2000-actual año
- category: obligatorio, debe ser uno de los valores enumerados
- theme: requerido, mínimo 2 caracteres
- url: obligatorio, URL válida con http:// o https://
- instructor: requerido, mínimo 2 caracteres
- has_quiz, requires_exam, extends_certificate: booleanos
- organization: opcional, máximo 200 caracteres si se provee
- user_id: debe existir en tabla users

### Validaciones de roadmap (POST /roadmaps)

- name: requerido, mínimo 3 caracteres
- course_ids: array no vacío, cada ID debe existir en courses
- order: array opcional, si se provee debe tener misma longitud que course_ids
- user_id: debe ser el usuario autenticado actual

## Respuestas de error estándar

| Código | Estructura JSON | Escenario |
| ------ | --------------- | ---------|
| 400 | `{error: "validation failed", details: [...]}` | Datos inválidos en body/query |
| 401 | `{error: "unauthorized", code: "AUTH_001"}` | Token faltante/inválido |
| 403 | `{error: "forbidden", code: "AUTH_002"}` | Usuario sin permiso |
| 404 | `{error: "not found", code: "COURSE_001"}` | Recurso no existe |
| 429 | `{error: "rate limited", retry_after: 60}` | Demasiadas solicitudes |
| 500 | `{error: "internal server error", code: "SERVER_001"}` | Error inesperado |