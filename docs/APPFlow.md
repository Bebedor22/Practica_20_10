# APPFlow.md — Application Flow y Navegación

## Pantallas de la aplicación

### 1. Pantalla de Login (Auth)

- Ubicación: `/auth/login` o raíz `/` si no hay sesión
- Elementos: formulario email/password, link "¿Olvidaste tu password?", botón login
- Estado: si ya hay sesión activa, redirige al dashboard/catalog inmediatamente

### 2. Pantalla de Registro (Auth)

- Ubicación: `/auth/register`
- Elementos: form name, email, password, confirm password, términos y condiciones
- Validación en tiempo real email format, passwords match
- Botón "Crear cuenta" → redirigir a login o dashboard

### 3. Pantalla de Recuperación de Password (Auth)

- Ubicación: `/auth/recovery`
- Elementos: form email, botón "Enviar enlace"
- Flujo: usuario ingresa email → si existe, se envía enlace con token → redirige a mensaje de éxito
- Token URL: `/auth/recovery/confirm/{token}` con formulario nueva password

### 4. Pantalla de Catálogo Comunitario (Home)

- Ubicación: `/courses` (protected, requiere login)
- Elementos:
  - Header con: nombre usuario, menú hamburguesa (mobile), notificaciones
  - Filters: select categoría, input búsqueda por título/tema, tags categoría
  - Paginación: bottom o top pagination controls
  - Grid de tarjetas de curso (1 columna mobile, 2-4 columnas desktop)
  - Estado vacío: mensaje "No hay cursos aún" con CTA "Añadir tu primer curso"
- Navegación: pagination numbers o scroll infinite load

### 5. Pantalla de Detalle de Curso

- Ubicación: `/courses/{id}` (protected)
- Elementos:
  - Información completa del curso: título, versión, año, categoría tag, tema, instructor
  - Descripción breve o puntos clave
  - Atributos: iconos quiz ✓/✗, examen ✓/✗, certificado ✓/✗, organización
  - Botón: "Añadir a mi roadmap" (si no está ya) o "Quitar de roadmap"
  - Botón: "Ya lo tomé" / "Declaration de toma" (toggle switch)
- Related: otros cursos de misma categoría o tema al final

### 6. Pantalla de Roadmap Personal

- Ubicación: `/roadmaps` o `/roadmaps/{id}` (protected)
- Elementos:
  - Header: título "Mi Roadmap", botón "Crear nuevo roadmap"
  - Lista de roadmaps existentes (si hay varios) o el roadmap actual
  - Visualización del roadmap actual: secuencia horizontal o vertical de fichas de curso
  - Cada ficha: título del curso, posición, botón "Remover", indicador completado/pendiente
  - Botones de acción: "Añadir curso desde catálogo", "Reordenar por drag & drop"
  - Progreso general: porcentaje de cursos completados vs total

### 7. Pantalla de "Añadir Curso" (Protected)

- Ubicación: `/courses/add` o `/roadmaps/{id}/add`
- Elementos:
  - Formulario con todos los campos requeridos de curso:
    - Título (input obligatorio)
    - Categoría (select con lista definida)
    - Tema (input obligatorio)
    - Versión (input text)
    - Año edición (number input, min 2000)
    - Docentes/instructores (input text)
    - URL web activa (input URL, validación)
    - ¿Cuenta con cuestionarios? (switch/toggle)
    - ¿Requiere examen? (switch/toggle)
    - ¿Extiende certificado? (switch/toggle)
    - ¿Lo avala una organización? (input text, opcional)
  - Botón "Guardar curso" → valida campos, crea curso en base de datos, validadción comunitaria
  - Estado: loading mientras se guarda, success toast, error messages

## Flujos de navegación principales

### Flujo 1: Onboarding → Catálogo → Roadmap

1. Usuario entra a la app (sin sesión) → vista Login
2. Usuario se registra → redirigido a catálogo comunitario
3. Usuario navega/curso filtra busca
4. Usuario hace click "Añadir a mi roadmap" en un curso detail
5. Si no tiene roadmap, se crea automáticamente o se le pide nombre
6. Curso añadido a roadmap personal, puede reordenar
7. Usuario puede seguir añadiendo más cursos al roadmap

### Flujo 2: Declaración de toma

1. Usuario aporta un nuevo curso (screen Add Course)
2. Al guardar, se le pregunta "¿Has tomado este curso?" (toggle Yes/No)
3. Si YES, se marca en el curso `declared_taken: true` y se muestra badge en detail
4. Si NO, se muestra curso como "pending" en catálogo
5. En roadmap, el curso tomado muestra indicador visual distinto
6. Otros usuarios ven el badge al navegar el catálogo

### Flujo 3: Recuperación de acceso

1. Usuario en login hace click "¿Olvidaste tu password?"
2. Pantalla recovery: ingresa email → envía enlace
3. Usuario recibe email con token único (válido 24h)
4. Hace click en enlace → formulario nueva password
5. Ingresa nueva password → login automático con nueva credencial
6. Redirigido a catálogo con sesión activa

### Flujo 4: Mobile vs Desktop navigation

- **Mobile** (<640px):
  - Header: logo a la izquierda, menú hamburguesa a la derecha, usuario profile icono a la derecha
  - Menú despliega verticalmente sobre el contenido
  - Paginación: flechas prev/next o números bottom

- **Desktop** (>=1024px):
  - Header: navegación horizontal con enlaces principales: Inicio, Catálogo, Roadmaps, Perfil
  - Menú hamburguesa oculto (solo para compatibilidad)
  - Paginación: numbers inline o sidebar de navegación

## Estados de página y transiciones

- **Skeleton loading**: todos los componentes que fetch data deben mostrar skeleton durante el carga
- **Empty states**: mensajes orientados con CTA (call to action) claro en cada sección vacía
- **Error boundaries**: captura de errores en componentes hijos, muestra fallback UI con botón retry
- **Transitions**: fade-in 200ms para cambios de vista, slide-in para mobile menus