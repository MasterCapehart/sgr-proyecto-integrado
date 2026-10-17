# Interfaz SGR

Pantallas HTML/CSS/JavaScript servidas por Django desde el mismo origen que /api/.

1. Iniciar el backend siguiendo backend/README.md.
2. Abrir http://127.0.0.1:8010/pages/login.html.
3. Ingresar con una cuenta de la base local.

No abrir index.html mediante file:// ni iniciar un servidor estático separado: las operaciones requieren sesión, CSRF y persistencia del backend. La navegación y las acciones visibles dependen del rol y la delegación autorizada; el servidor vuelve a validar cada operación.

Los catálogos y cuentas se configuran con información autorizada. No publicar credenciales, datos ciudadanos ni configuraciones personales.
