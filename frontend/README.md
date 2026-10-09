# Frontend SGR

Base en HTML, CSS y JavaScript, sin framework ni instalación de dependencias.

## Abrir

Abrir `index.html` en el navegador. También se puede servir esta carpeta con un servidor HTTP local, por ejemplo `python3 -m http.server 8080 --directory frontend` desde la raíz del repositorio, y visitar http://localhost:8080. El servidor de prueba se detiene con Ctrl+C.

## Organización

- `index.html`: inicio de la estructura.
- `pages/guia.html`: guía y demostraciones de mensajes.
- `assets/css/styles.css`: estilos compartidos y adaptación móvil.
- `assets/js/components/layout.js`: encabezado y navegación reutilizables.
- `assets/js/app.js`: montaje de componentes y mensajes de ejemplo.
- `assets/images/`: recursos municipales.
- `assets/vendor/sweetalert2.min.js`: SweetAlert2 local (MIT; aviso incluido en el archivo).

El escudo se reutiliza sin modificación desde los mockups, fuente municipal: https://framework.laserena.cl/img/escudo-blanco.svg. Estilos iniciales: Arial, rojo #AD0000 y fondo claro; revisar cada pantalla con las normas https://laserena.cl/conocenos/normas-graficas.

## Nueva pantalla

Copiar la estructura de `pages/guia.html`, conservar los elementos `site-header`, `site-sidebar` y `main-content`, y mantener el orden de scripts. En las páginas dentro de `pages/`, usar `data-base-path="../"`. Agregar un enlace en el componente de navegación cuando la pantalla exista. El contenido propio va dentro de `main`; los estilos comunes permanecen en styles.css.

## Alcance

Esta tarea solo crea la base compartida. No implementa login, recuperación, CRUD, autorización, persistencia ni AWS. Usuario, rol y delegación muestran valores vacíos explícitos hasta integrarse con Django. Los botones SweetAlert2 son demostraciones y no simulan guardados. Los permisos deben validarse en el backend; ocultar botones no constituye autorización.

El frontend consumirá la API de Django y nunca se conectará directamente a MySQL. Acordar endpoints, respuestas y manejo de sesión antes de esa integración. No incluir secretos ni datos personales reales.
