# UX-UI.md — Diseño de Interfaz y Experiencia de Usuario

## Estética visual (estilo Google Material)

- **Paleta de colores**:
  - Primary: `#4285F4` (Google Blue)
  - Secondary: `#34A853` (Google Green)
  - Error: `#EA4335` (Google Red)
  - Warning: `#FBBC05` (Google Yellow)
  - Superficie: `#FFFFFF` (blanco)
  - Fondo: `#F8F9FA` (gray lightest)
  - Texto principal: `#202124` (gray darkest)
  - Texto secundario: `#5F6368` (gray medium)

- **Tipografía**:
  - Familia: Inter, fallback: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
  - Tamaños: xs: 12px, sm: 14px, md: 16px, lg: 20px, xl: 24px, 2xl: 32px
  - Peso: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)
  - Altura de línea: 1.5 base, escalado proporcionalmente

- **Espaciado**: sistema de 8px
  - Espaciado base: 8px, 16px, 24px, 32px, 40px, 48px, 64px
  - Margen interno de componentes: 16px mínimo
  - Radio de borde: 4px componentes, 2px inputs y campos de form

- **Sombras**:
  - Elevación baja: `0 1px 2px rgba(0,0,0,0.1)`
  - Elevación media: `0 4px 12px rgba(0,0,0,0.1)`
  - Elevación alta: `0 8px 24px rgba(0,0,0,0.15)`
  - Focus ring: `0 0 0 3px rgba(66, 133, 244, 0.4)`

## Componentes definidos

### Botón (Button)

- Estilo base: bordes redondeados 4px, padding horizontal 12px 24px, padding vertical 8px 16px
- Fondo: primary color en estado normal, hover con opacity 0.9
- Texto: white en primary, dark text en secondary
- Estados: default, hover, active, disabled
- Tamaños: default, sm (8px padding), lg (16px padding)

### Tarjeta de curso (Course Card)

- Fondo: white o superficie ligeramente elevadas
- Padding: 16px
- Imagen/curso: altura máxima 200px, objeto cover, border-radius 4px
- Contenido: título (h3), categoría tag, instructor, atributos (quiz/examen/certificado)
- Hover: sombra elevation media, transform translateY(-2px)
- Acciones: botón "Añadir al roadmap" en hover o focus

### Formularios

- Inputs: border 1px solid #D2D2D6, border-radius 4px, padding 12px 16px
- Focus: border-color #4285F4, box-shadow focus ring
- Labels: arriba del input o floating placeholder
- Errores: texto rojo #EA4335, borde input rojo
- Select: apariencia nativa con estilo minimal, focus ring

### Menú hamburguesa (Mobile)

- Icono: 3 líneas horizontales 24px, color texto principal
- Animación: transform a X o cierre dependiendo estado
- Panel: full-width mobile, fondo blanco, sombra elevation, items con padding 16px
- Cierre: click en item o fuera del panel, overlay semi-transparente

### Roadmap View

- Visualización horizontal o vertical de cursos en secuencia
- Cada "ficha" de curso: misma altura, border-radius 4px, padding 12px
- Botón "Remover" en cada ficha, hover con estado definido
- Arrastre y reordenamiento (drag & drop) para reorganizar el roadmap
- Indicador de progreso: cursos completados vs pending

## Mobile-first con mejora progresiva

- **Layout base (mobile, <640px)**:
  - Columna única en todos los screens
  - Menú hamburguesa siempre visible en header
  - Tarjetas de curso se apilan verticalmente
  - Formularios en columna única

- **Mejora progresiva (>=640px)**:
  - Grid de 2 columnas para catálogo de cursos
  - Header con menú visible + logo
  - Tarjetas de curso con más información visible
  - Sidebars opcionales en roadmaps largos

- **>=768px (tablet)**:
  - Grid de 3 columnas en catálogo
  - Layouts más amplios con espacio blanco adicional

- **>=1024px (desktop)**:
  - Grid de 4 columnas máximo
  - Sidebar para navegación principal
  - Panels divididos en pantallas amplias

## Interacciones y feedback

- **Loading states**: skeleton loaders o spinners en todos los fetches async
- **Error states**: mensajes claros con acción de retry
- **Success states**: toast notifications o snackbar en bottom
- **Hover/focus**: todos los componentes interactivos deben tener estado visual definido
- **Disabled state**: opacity 0.5, cursor not-allowed, estilo consistente

## Accesibilidad (a nivel mínimo)

- Contraste mínimo 4.5:1 para texto normal, 3:1 para grande
- Todos los inputs y botones focusable con keyboard navigation
- Atributos aria-label en componentes iconos y acciones
- Colores no son la única forma de comunicar información (ej. errores con texto + ícono)
- Tamaño toque mínimo: 44px x 44px en elementos táctiles