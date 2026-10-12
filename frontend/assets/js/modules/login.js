/**
 * Módulo de pantalla M-01: Inicio de sesión
 * Validación frontend accesible, toggle de contraseña y feedback con SweetAlert2.
 * Cumple con la Guía de desarrollo del SGR (Edición 11-10-2026).
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('login-form');
  const userInput = document.getElementById('username');
  const passInput = document.getElementById('password');
  const toggleBtn = document.getElementById('toggle-password');
  const submitBtn = document.getElementById('btn-submit');

  if (!form) return;

  // 1. Mostrar / Ocultar contraseña accesible
  if (toggleBtn && passInput) {
    toggleBtn.addEventListener('click', () => {
      const isPassword = passInput.getAttribute('type') === 'password';
      passInput.setAttribute('type', isPassword ? 'text' : 'password');
      toggleBtn.textContent = isPassword ? 'Ocultar' : 'Mostrar';
      toggleBtn.setAttribute('aria-label', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
    });
  }

  // 2. Validación de campos vacíos y envío
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const username = userInput.value.trim();
    const password = passInput.value;

    if (!username || !password) {
      if (window.Swal) {
        window.Swal.fire({
          icon: 'warning',
          title: 'Campos requeridos',
          text: 'Por favor, ingresa tu usuario/correo y contraseña para continuar.',
          confirmButtonColor: '#ad0000',
          confirmButtonText: 'Entendido'
        });
      } else {
        alert('Por favor, ingresa tu usuario y contraseña.');
      }
      if (!username) userInput.focus();
      else passInput.focus();
      return;
    }

    // Deshabilitar botón durante validación
    submitBtn.disabled = true;
    submitBtn.textContent = 'Verificando credenciales...';

    // Simulación de respuesta frontend (el backend se conectará en su fase respectiva)
    setTimeout(() => {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Ingresar al sistema →';

      if (window.Swal) {
        window.Swal.fire({
          icon: 'info',
          title: 'Módulo de acceso en frontend',
          html: `<p>Credenciales ingresadas para <strong>${escapeHtml(username)}</strong>.</p><p style="font-size:13px;color:#65717e;margin-top:8px">La autenticación real y validación de roles se conectará a la API de Django en la siguiente fase.</p>`,
          confirmButtonColor: '#ad0000',
          confirmButtonText: 'Aceptar'
        });
      }
    }, 600);
  });

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
});
