/**
 * Módulo de flujo de recuperación de contraseña:
 * - M-11: Solicitar código (recuperar-clave.html)
 * - M-12: Validar código (validar-codigo.html)
 * - M-13: Definir nueva clave (nueva-clave.html)
 * Sigue la sección 7 de la Guía de desarrollo del SGR.
 */
document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;

  // --- M-11: Solicitud de código ---
  if (page === 'recovery') {
    const form = document.getElementById('recovery-form');
    const emailInput = document.getElementById('email');
    const btn = document.getElementById('btn-recovery');

    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = emailInput.value.trim();

        if (!email || !email.includes('@')) {
          showModal('warning', 'Correo requerido', 'Ingresa un correo institucional válido.');
          emailInput.focus();
          return;
        }

        btn.disabled = true;
        btn.textContent = 'Enviando solicitud...';

        setTimeout(() => {
          btn.disabled = false;
          btn.textContent = 'Enviar código de verificación →';
          if (window.Swal) {
            window.Swal.fire({
              icon: 'success',
              title: 'Instrucciones enviadas',
              html: `<p>Si el correo <strong>${escapeHtml(email)}</strong> está registrado, se ha generado el código.</p><p style="font-size:13px;color:#65717e;margin-top:8px">Redirigiendo al paso de verificación...</p>`,
              confirmButtonColor: '#ad0000',
              confirmButtonText: 'Continuar'
            }).then(() => {
              window.location.href = 'validar-codigo.html';
            });
          } else {
            window.location.href = 'validar-codigo.html';
          }
        }, 600);
      });
    }
  }

  // --- M-12: Verificación de código ---
  if (page === 'validate-code') {
    const form = document.getElementById('validate-form');
    const codeInput = document.getElementById('code');
    const btn = document.getElementById('btn-validate');
    const resendBtn = document.getElementById('btn-resend');

    if (codeInput) {
      codeInput.addEventListener('input', () => {
        codeInput.value = codeInput.value.replace(/[^0-9]/g, '');
      });
    }

    if (resendBtn) {
      resendBtn.addEventListener('click', () => {
        showModal('info', 'Reenvío de código', 'Se ha solicitado un nuevo código de verificación. Revisa tu bandeja de entrada.');
      });
    }

    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const code = codeInput.value.trim();

        if (code.length !== 6) {
          showModal('warning', 'Código incompleto', 'Debes ingresar los 6 dígitos del código de verificación.');
          codeInput.focus();
          return;
        }

        btn.disabled = true;
        btn.textContent = 'Comprobando código...';

        setTimeout(() => {
          btn.disabled = false;
          btn.textContent = 'Validar código →';
          if (window.Swal) {
            window.Swal.fire({
              icon: 'success',
              title: 'Código verificado',
              text: 'Identidad validada con éxito. Ahora puedes crear tu nueva contraseña.',
              confirmButtonColor: '#ad0000',
              confirmButtonText: 'Continuar'
            }).then(() => {
              window.location.href = 'nueva-clave.html';
            });
          } else {
            window.location.href = 'nueva-clave.html';
          }
        }, 600);
      });
    }
  }

  // --- M-13: Creación de nueva clave ---
  if (page === 'new-password') {
    const form = document.getElementById('newpass-form');
    const newpassInput = document.getElementById('newpass');
    const confirmInput = document.getElementById('confirmpass');
    const toggleNew = document.getElementById('toggle-newpass');
    const toggleConf = document.getElementById('toggle-confirmpass');
    const btn = document.getElementById('btn-savepass');

    bindToggle(toggleNew, newpassInput);
    bindToggle(toggleConf, confirmInput);

    if (form) {
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const p1 = newpassInput.value;
        const p2 = confirmInput.value;

        if (!p1 || p1.length < 8) {
          showModal('warning', 'Contraseña insegura', 'La nueva contraseña debe tener al menos 8 caracteres.');
          newpassInput.focus();
          return;
        }

        if (p1 !== p2) {
          showModal('error', 'Contraseñas no coinciden', 'La confirmación no es idéntica a la nueva contraseña ingresada.');
          confirmInput.focus();
          return;
        }

        btn.disabled = true;
        btn.textContent = 'Actualizando contraseña...';

        setTimeout(() => {
          btn.disabled = false;
          btn.textContent = 'Guardar nueva contraseña →';
          if (window.Swal) {
            window.Swal.fire({
              icon: 'success',
              title: '¡Contraseña restablecida!',
              text: 'Tu acceso ha sido actualizado con éxito. Ahora puedes iniciar sesión.',
              confirmButtonColor: '#ad0000',
              confirmButtonText: 'Ir a Iniciar Sesión'
            }).then(() => {
              window.location.href = 'login.html';
            });
          } else {
            window.location.href = 'login.html';
          }
        }, 600);
      });
    }
  }

  function bindToggle(btn, input) {
    if (!btn || !input) return;
    btn.addEventListener('click', () => {
      const isPass = input.getAttribute('type') === 'password';
      input.setAttribute('type', isPass ? 'text' : 'password');
      btn.textContent = isPass ? 'Ocultar' : 'Mostrar';
    });
  }

  function showModal(icon, title, text) {
    if (window.Swal) {
      window.Swal.fire({ icon, title, text, confirmButtonColor: '#ad0000', confirmButtonText: 'Aceptar' });
    } else {
      alert(text);
    }
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
});
