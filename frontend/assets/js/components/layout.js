/**
 * Componentes compartidos del Sistema de Gestión de Resultados (SGR).
 * Tarea T19: Integrar cabecera y cambio de delegación activa con persistencia de contexto.
 */
(() => {
  const API_BASE = window.location.origin.includes(':8000') ? '' : 'http://127.0.0.1:8000';

  /**
   * Comprueba si el usuario tiene cambios pendientes o formularios sucios en la vista actual.
   * Evita pérdidas involuntarias de datos al cambiar de delegación activa en la cabecera.
   */
  function hasUnsavedChanges() {
    // 1. Detección en formulario de Registro de Atención Ciudadana (M-20)
    const sol = document.getElementById('solicitante');
    const desc = document.getElementById('descripcion-atencion');
    const caso = document.getElementById('codigo-caso-social');
    if ((sol && sol.value.trim().length > 0) ||
        (desc && desc.value.trim().length > 0) ||
        (caso && caso.value.trim().length > 0)) {
      return true;
    }

    // 2. Detección en modales CRUD abiertos (M-03, M-04, M-07, etc.)
    const modal = document.getElementById('modal-editor');
    if (modal && modal.open) {
      const form = document.getElementById('form-editor');
      if (form) {
        const inputs = form.querySelectorAll('input:not([type="hidden"]), textarea, select');
        for (const input of inputs) {
          if (input.value && input.value.trim().length > 0) {
            return true;
          }
        }
      }
      return true;
    }

    // 3. Bandera manual de control global para vistas específicas
    if (window.__sgrHasUnsavedChanges === true) {
      return true;
    }

    return false;
  }

  /**
   * Inicializa y mantiene el contexto institucional permanente en la cabecera (T19).
   * Carga funcionario real, rol y catálogo de delegaciones activas autorizadas.
   */
  async function initSessionContext() {
    const userEl = document.getElementById('session-user');
    const roleEl = document.getElementById('session-role');
    const selectEl = document.getElementById('session-delegation-select');

    if (!userEl || !roleEl || !selectEl) return;

    // 1. Restaurar desde sessionStorage para evitar parpadeos visuales al navegar
    try {
      const cachedRaw = sessionStorage.getItem('sgr_contexto');
      if (cachedRaw) {
        const cached = JSON.parse(cachedRaw);
        if (cached.usuario) {
          userEl.textContent = cached.usuario.display || `${cached.usuario.nombre_completo} (${cached.usuario.rut || ''})`;
          roleEl.textContent = cached.usuario.rol || 'Funcionario';
        }
        if (cached.delegaciones_autorizadas && Array.isArray(cached.delegaciones_autorizadas)) {
          renderDelegations(selectEl, cached.delegaciones_autorizadas, cached.delegacion_activa ? cached.delegacion_activa.id : null);
        }
      }
    } catch (_) {}

    // 2. Consultar contexto en vivo desde el backend Django
    try {
      const res = await fetch(`${API_BASE}/api/contexto/`);
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.data) {
          const d = json.data;
          // Guardar en sesión del navegador
          sessionStorage.setItem('sgr_contexto', JSON.stringify(d));

          // Actualizar datos del funcionario
          if (d.usuario) {
            userEl.textContent = d.usuario.display || `${d.usuario.nombre_completo} (${d.usuario.rut || ''})`;
            roleEl.textContent = d.usuario.rol || 'Funcionario Municipal';
          }

          // Actualizar selector de delegaciones autorizadas
          if (Array.isArray(d.delegaciones_autorizadas)) {
            const activeId = d.delegacion_activa ? d.delegacion_activa.id : null;
            renderDelegations(selectEl, d.delegaciones_autorizadas, activeId);
          }
        }
      }
    } catch (err) {
      console.warn('No se pudo sincronizar el contexto con el servidor:', err);
    }

    // 3. Manejar cambio interactivo de delegación activa
    if (!selectEl.dataset.initialized) {
      selectEl.dataset.initialized = 'true';
      selectEl.addEventListener('change', async () => {
        const previousId = selectEl.dataset.currentId;
        const newId = selectEl.value;

        if (!newId || newId === previousId) return;

        // Comprobar si hay cambios sin guardar
        if (hasUnsavedChanges()) {
          let proceed = false;
          if (window.Swal) {
            const result = await window.Swal.fire({
              title: '¿Cambiar ámbito territorial?',
              text: 'Hay datos sin guardar en el formulario actual. Al cambiar de delegación activa se actualizará el contexto institucional.',
              icon: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#ad0000',
              cancelButtonColor: '#65717e',
              confirmButtonText: 'Sí, cambiar delegación',
              cancelButtonText: 'Cancelar y mantener'
            });
            proceed = result.isConfirmed;
          } else {
            proceed = confirm('Hay datos sin guardar. ¿Deseas cambiar de delegación activa?');
          }

          if (!proceed) {
            selectEl.value = previousId;
            return;
          }
        }

        // Enviar cambio al servidor
        try {
          const res = await fetch(`${API_BASE}/api/contexto/cambiar-delegacion/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ delegacion_id: parseInt(newId, 10) })
          });
          const json = await res.json();

          if (res.ok && json.success) {
            selectEl.dataset.currentId = String(newId);

            // Actualizar sessionStorage
            try {
              const cached = JSON.parse(sessionStorage.getItem('sgr_contexto') || '{}');
              if (cached.delegacion_activa) {
                cached.delegacion_activa.id = json.data.id;
                cached.delegacion_activa.nombre = json.data.nombre;
                cached.delegacion_activa.display = json.data.display;
              }
              if (Array.isArray(cached.delegaciones_autorizadas)) {
                cached.delegaciones_autorizadas.forEach(del => {
                  del.activa = (del.id === json.data.id);
                });
              }
              sessionStorage.setItem('sgr_contexto', JSON.stringify(cached));
            } catch (_) {}

            // Notificar a las vistas que el ámbito territorial ha cambiado
            window.dispatchEvent(new CustomEvent('sgr:delegacion-cambiada', {
              detail: json.data
            }));

            if (window.Swal) {
              window.Swal.fire({
                icon: 'success',
                title: 'Ámbito territorial actualizado',
                text: `Delegación activa: ${json.data.nombre}`,
                timer: 2000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
              });
            }
          } else {
            const msg = (json.error && json.error.message) || 'No se pudo cambiar la delegación.';
            if (window.Swal) {
              window.Swal.fire({
                icon: 'error',
                title: 'No fue posible cambiar la delegación',
                text: msg,
                confirmButtonColor: '#ad0000'
              });
            } else {
              alert(msg);
            }
            selectEl.value = previousId;
          }
        } catch (err) {
          console.error('Error al comunicar cambio de delegación:', err);
          selectEl.value = previousId;
          if (window.Swal) {
            window.Swal.fire({
              icon: 'error',
              title: 'Error de conexión',
              text: 'No fue posible comunicar el cambio de delegación al servidor.',
              confirmButtonColor: '#ad0000'
            });
          }
        }
      });
    }
  }

  function renderDelegations(selectEl, delegations, activeId) {
    selectEl.innerHTML = '';
    if (!delegations || delegations.length === 0) {
      selectEl.innerHTML = '<option value="">Sin delegaciones</option>';
      return;
    }
    delegations.forEach(del => {
      const opt = document.createElement('option');
      opt.value = del.id;
      opt.textContent = del.nombre;
      if (activeId && String(del.id) === String(activeId)) {
        opt.selected = true;
      }
      selectEl.appendChild(opt);
    });
    if (activeId) {
      selectEl.dataset.currentId = String(activeId);
    }
  }

  window.SGRLayout = {
    hasUnsavedChanges,
    mount({ basePath, currentPage }) {
      const header = document.getElementById('site-header');
      const sidebar = document.getElementById('site-sidebar');
      if (header) {
        if (currentPage === 'login' || currentPage === 'recovery' || currentPage === 'validate-code' || currentPage === 'new-password') {
          header.innerHTML = `<a class="brand" href="${basePath}index.html"><img src="${basePath}assets/images/escudo-blanco.svg" alt="Escudo de la Municipalidad de La Serena"><span><strong>SGR</strong><small>Municipalidad de La Serena</small></span></a><div class="public-title">Sistema de Gestión de Resultados</div>`;
        } else {
          header.innerHTML = `<a class="brand" href="${basePath}index.html"><img src="${basePath}assets/images/escudo-blanco.svg" alt="Escudo de la Municipalidad de La Serena"><span><strong>SGR</strong><small>Municipalidad de La Serena</small></span></a><dl class="identity" aria-label="Contexto institucional de acceso"><div><dt>Usuario</dt><dd id="session-user">Cargando...</dd></div><div><dt>Rol</dt><dd id="session-role">Cargando...</dd></div><div><dt>Delegación activa</dt><dd id="session-delegation"><select id="session-delegation-select" class="delegation-select" aria-label="Cambiar delegación activa"><option value="">Cargando...</option></select></dd></div></dl>`;
          initSessionContext();
        }
      }
      if (sidebar) {
        sidebar.innerHTML = `<nav aria-label="Navegación principal">
          <a href="${basePath}index.html" ${currentPage === 'home' ? 'aria-current="page"' : ''}>Inicio</a>
          <a href="${basePath}pages/guia.html" ${currentPage === 'guide' ? 'aria-current="page"' : ''}>Guía de componentes</a>
          <p class="nav-heading">Operación</p>
          <a href="${basePath}pages/ingreso-atencion.html" ${currentPage === 'atencion' ? 'aria-current="page"' : ''}>Registrar atención</a>
          <p class="nav-heading">Administración</p>
          <a href="${basePath}pages/delegaciones.html" ${currentPage === 'delegaciones' ? 'aria-current="page"' : ''}>Delegaciones</a>
          <a href="${basePath}pages/roles.html" ${currentPage === 'roles' ? 'aria-current="page"' : ''}>Roles y permisos</a>
          <a href="${basePath}pages/usuarios.html" ${currentPage === 'usuarios' ? 'aria-current="page"' : ''}>Usuarios</a>
          <a href="${basePath}pages/items-metas.html" ${currentPage === 'items-metas' ? 'aria-current="page"' : ''}>Ítems y metas</a>
          <p class="nav-heading">Catálogos</p>
          <a href="${basePath}pages/tipos-atencion.html" ${currentPage === 'tipos-atencion' ? 'aria-current="page"' : ''}>Tipos de atención</a>
          <a href="${basePath}pages/subatenciones.html" ${currentPage === 'subatenciones' ? 'aria-current="page"' : ''}>Subatenciones</a>
          <p class="nav-heading">Acceso</p>
          <a href="${basePath}pages/login.html" ${currentPage === 'login' ? 'aria-current="page"' : ''}>Cerrar sesión / Login</a>
        </nav>`;
      }
    }
  };
})();
