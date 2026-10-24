# PRD — Product Requirements Document

## Público objetivo

Estudiantes de todos los niveles que desean descubrir, organizar y seguir cursos gratuitos en un entorno comunitario. El producto está diseñado para ser usado tanto en desktop como en dispositivos móviles, con énfasis en usabilidad móvil-first.

## Problema que resuelve

Los estudiantes a menudo pierden cursos útiles porque no tienen un sistema organizado para descubrirlos, guardarlos y trackear su progreso. Las plataformas existentes no permiten la colaboración comunitaria para construir un catálogo colectivo ni crear roadmaps de aprendizaje personalizados adaptados a objetivos individuales.

## Qué hace la aplicación

1. **Roadmap personal**: Cada usuario crea y gestiona su propio roadmap de cursos de aprendizaje. Un roadmap es una secuencia ordenada de cursos que el usuario sigue para alcanzar un objetivo de aprendizaje. Los usuarios pueden agregar cursos desde el catálogo comunitario, reordenarlos y marcarlos como completados.

2. **Aporte de cursos**: Los usuarios pueden cargar cursos gratuitos desde cualquier plataforma o proveedor, especificando:
   - Título del curso
   - Versión/actualización del contenido
   - Año de edición
   - Categoría/rubro (de lista definida: Programación, Diseño, Marketing, Negocios, Artes, Ciencias, Otros)
   - Tema específico (ej. JavaScript, UI/UX, Machine Learning, etc.)
   - Docentes o disertantes
   - Enlace web activo al curso
   - Atributos: cuenta con cuestionarios, requiere examen, extiende certificado, lo avala una organización

3. **Declaración de toma**: Al aportar un curso, el usuario declara si él o ella ya lo tomó o no. Esto ayuda a otros usuarios a evitar duplicados y a entender el nivel de experiencia previo.

4. **Catálogo comunitario**: Todos los cursos aportados y validados pasan al catálogo comunitario. Desde allí, cualquier usuario puede navegarlos, buscarlos e incluirlos en su roadmap personal. El catálogo incluye filtros por categoría, tema y atributos.

5. **Cuenta de usuario y autenticación**:
   - Registro de usuario con nombre, email y password (bcrypt mínimo)
   - Login con rate limiting en el endpoint de login
   - Recuperación completa de contraseña: solicitud → enlace/token → nueva contraseña
   - Perfil de usuario con roadmaps personales

## Qué NO hace la aplicación

- No gestiona pagos o transacciones monetarias (solo cursos gratuitos)
- No incluye reproducción de contenido de video o material del curso
- No tiene sistema de calificación o ranking de usuarios
- No soporta eliminación de cursos una vez validados (solo marcado como "retirado" si es necesario)
- No integra certificados reales ni emisión de credenciales oficiales
- No tiene sistema de mensajería entre usuarios

## Historias de usuario (P0)

1. **US-001**: Como usuario, puedo registrar una nueva cuenta con mi nombre, email y password.
2. **US-002**: Como usuario, puedo hacer login y mantener sesión activa.
3. **US-003**: Como usuario, puedo recuperar mi password mediante solicitud de enlace por email.
4. **US-004**: Como usuario, puedo ver el catálogo comunitario de cursos filtrados por categoría y búsqueda.
5. **US-005**: Como usuario, puedo agregar un curso al mi roadmap personal desde el catálogo comunitario.
6. **US-006**: Como usuario, puedo declarar si he tomado o no un curso que aporté.
7. **US-007**: Como usuario, puedo crear y editar mi roadmap personal de cursos.
8. **US-008**: Como usuario, puedo ver mis roadmaps anteriores y su progreso.

## Fuera de alcance (para futuras instancias)

- Autenticación social (Google, GitHub, etc.)
- Sistema de comentarios o reseñas de cursos
- Integración con plataformas externas de alojamiento de cursos
- Panel de administrador para validación masiva
- Notificaciones push o email de seguimiento