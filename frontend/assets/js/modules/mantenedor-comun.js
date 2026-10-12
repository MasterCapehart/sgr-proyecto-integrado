/**
 * Módulo reutilizable de lógica común para los Mantenedores CRUD
 * Conexión completa Frontend <-> Backend API REST (Tareas T04, T14, T15).
 * Controla: Carga en vivo desde API, búsqueda dinámica, filtro de estado, 
 * selectores dinámicos de catálogos padre, modal <dialog>, operaciones CRUD reales, 
 * manejo de errores y SweetAlert2.
 */
document.addEventListener('DOMContentLoaded', () => {
  const pageId = document.body.dataset.page;
  const searchInput = document.getElementById('search-input');
  const statusFilter = document.getElementById('status-filter');
  const tableBody = document.getElementById('table-body');
  const pageInfo = document.getElementById('page-info');
  const btnNuevo = document.getElementById('btn-nuevo');
  const btnExport = document.getElementById('btn-export');
  const modal = document.getElementById('modal-editor');
  const modalClose = document.getElementById('modal-close');
  const modalCancel = document.getElementById('modal-cancel');
  const formEditor = document.getElementById('form-editor');
  const modalTitle = document.getElementById('modal-title');

  // Mapeo de recursos REST por página
  const ENDPOINT_MAP = {
    'tipos-atencion': '/api/tipos-atencion/',
    'subatenciones': '/api/subatenciones/',
    'delegaciones': '/api/delegaciones/',
    'roles': '/api/roles/',
    'usuarios': '/api/usuarios/',
    'items-metas': '/api/items-metas/'
  };

  const endpointPath = ENDPOINT_MAP[pageId];
  const API_BASE = window.location.origin.includes(':8000') 
    ? '' 
    : 'http://127.0.0.1:8000';

  let currentEditId = null;
  let backendActive = false;

  // Cargar selector de catálogo padre (para Subatenciones)
  async function populateParentSelect(selectedId = null) {
    const selectPadre = document.getElementById('campo-padre');
    if (!selectPadre) return;
    try {
      const res = await fetch(`${API_BASE}/api/tipos-atencion/?estado=activos&page_size=100`);
      const data = await res.json();
      if (data.success && Array.isArray(data.results)) {
        selectPadre.innerHTML = '';
        if (data.results.length === 0) {
          selectPadre.innerHTML = '<option value="">(No hay tipos activos disponibles)</option>';
          return;
        }
        data.results.forEach(tipo => {
          const opt = document.createElement('option');
          opt.value = tipo.id;
          opt.textContent = `${tipo.codigo} · ${tipo.nombre}`;
          if (selectedId && (String(selectedId) === String(tipo.id) || selectedId === tipo.codigo)) {
            opt.selected = true;
          }
          selectPadre.appendChild(opt);
        });
      }
    } catch (e) {
      console.warn('No se pudieron cargar tipos de atención para el selector:', e);
    }
  }

  // 1. Carga de datos desde la API del Backend
  async function loadDataFromApi() {
    if (!endpointPath || !tableBody) return;

    const term = (searchInput ? searchInput.value.trim() : '');
    const rawStatus = (statusFilter ? statusFilter.value.toLowerCase() : 'todos');
    const estado = (rawStatus === 'activo' || rawStatus === 'activos') ? 'activos' 
      : (rawStatus === 'inactivo' || rawStatus === 'inactivos') ? 'inactivos' 
      : 'todos';

    const url = `${API_BASE}${endpointPath}?search=${encodeURIComponent(term)}&estado=${encodeURIComponent(estado)}&page_size=50`;

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      
      if (data.success && Array.isArray(data.results)) {
        backendActive = true;
        renderTableRows(data.results);
        if (pageInfo) {
          pageInfo.textContent = `Mostrando ${data.results.length} de ${data.count} registros`;
        }
      }
    } catch (err) {
      console.warn('API local no disponible, operando en modo frontend:', err.message);
      filterRowsFrontend();
    }
  }

  // Renderizar filas dinámicas obtenidas de la base de datos
  function renderTableRows(items) {
    if (!tableBody) return;
    tableBody.innerHTML = '';

    if (items.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="5" style="text-align: center; padding: 24px; color: var(--muted, #65717e);">
            No se encontraron registros coincidentes.
          </td>
        </tr>
      `;
      return;
    }

    items.forEach(item => {
      const tr = document.createElement('tr');
      const isActivo = item.estado === true;
      tr.dataset.status = isActivo ? 'activo' : 'inactivo';

      const badgeHtml = isActivo 
        ? '<span class="badge green">Activo</span>' 
        : '<span class="badge red">Inactivo</span>';

      const toggleActionText = isActivo ? 'Desactivar' : 'Activar';

      // Columna 3 varía según la entidad
      let col3Content = '';
      if (pageId === 'subatenciones') {
        col3Content = escapeHtml(item.tipo_padre_display || (item.tipo_atencion_codigo ? `${item.tipo_atencion_codigo} · ${item.tipo_atencion_nombre}` : '-'));
      } else {
        col3Content = escapeHtml(item.descripcion || item.direccion || '-');
      }

      tr.innerHTML = `
        <td><strong>${escapeHtml(item.codigo || '-')}</strong></td>
        <td>${escapeHtml(item.nombre || item.nombre_tipo || '-')}</td>
        <td>${col3Content}</td>
        <td>${badgeHtml}</td>
        <td>
          <button type="button" class="linkbtn" data-action="ver" data-id="${item.id}">Ver</button> · 
          <button type="button" class="linkbtn" data-action="editar" data-id="${item.id}">Editar</button> · 
          <button type="button" class="linkbtn" data-action="toggle-estado" data-id="${item.id}">${toggleActionText}</button>
        </td>
      `;
      tableBody.appendChild(tr);
    });
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, s => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[s]);
  }

  // Filtrado de respaldo (modo estático/offline)
  function filterRowsFrontend() {
    if (!tableBody) return;
    const term = (searchInput ? searchInput.value.toLowerCase().trim() : '');
    const status = (statusFilter ? statusFilter.value.toLowerCase() : 'todos');
    const rows = tableBody.querySelectorAll('tr');

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const rowStatus = (row.dataset.status || '').toLowerCase();
      const matchesSearch = !term || text.includes(term);
      const matchesStatus = status === 'todos' || rowStatus === status;
      row.style.display = (matchesSearch && matchesStatus) ? '' : 'none';
    });
  }

  // Eventos de búsqueda y filtros con debounce
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        if (backendActive) loadDataFromApi();
        else filterRowsFrontend();
      }, 300);
    });
  }

  if (statusFilter) {
    statusFilter.addEventListener('change', () => {
      if (backendActive) loadDataFromApi();
      else filterRowsFrontend();
    });
  }

  // 2. Control del Modal Dialog
  if (btnNuevo && modal) {
    btnNuevo.addEventListener('click', async () => {
      currentEditId = null;
      const singularName = pageId === 'subatenciones' ? 'Subatención' 
        : pageId === 'tipos-atencion' ? 'Tipo de Atención' 
        : 'registro';

      if (modalTitle) modalTitle.textContent = `Nueva ${singularName}`;
      if (formEditor) {
        formEditor.reset();
        const inputEstado = formEditor.elements['estado'];
        if (inputEstado) inputEstado.value = 'Activo';
      }

      if (pageId === 'subatenciones') {
        await populateParentSelect();
      }

      modal.showModal();
    });
  }

  function closeModal() {
    if (modal) modal.close();
    currentEditId = null;
  }

  if (modalClose) modalClose.addEventListener('click', closeModal);
  if (modalCancel) modalCancel.addEventListener('click', closeModal);

  // 3. Envío de Formulario conectado a la API
  if (formEditor) {
    formEditor.addEventListener('submit', async (e) => {
      e.preventDefault();

      const codigoVal = formEditor.elements['codigo']?.value?.trim();
      const nombreVal = formEditor.elements['nombre']?.value?.trim();
      const descVal = formEditor.elements['descripcion']?.value?.trim();
      const estadoVal = (formEditor.elements['estado']?.value || 'Activo').toLowerCase() === 'activo';

      if (!codigoVal || !nombreVal) {
        if (window.Swal) {
          window.Swal.fire({
            icon: 'warning',
            title: 'Campos requeridos',
            text: 'Por favor completa el código y el nombre.',
            confirmButtonColor: '#ad0000'
          });
        }
        return;
      }

      const payload = {
        codigo: codigoVal,
        nombre: nombreVal,
        estado: estadoVal
      };

      if (descVal !== undefined) payload.descripcion = descVal;

      // Asignar catálogo padre para Subatenciones
      if (pageId === 'subatenciones') {
        const parentVal = formEditor.elements['tipo_padre']?.value || formEditor.elements['tipo_atencion']?.value;
        if (!parentVal) {
          if (window.Swal) {
            window.Swal.fire({
              icon: 'warning',
              title: 'Catálogo padre requerido',
              text: 'Debe seleccionar un Tipo de Atención asociado.',
              confirmButtonColor: '#ad0000'
            });
          }
          return;
        }
        payload.tipo_atencion = parentVal;
      }

      if (!endpointPath) {
        closeModal();
        if (window.Swal) {
          window.Swal.fire({
            icon: 'success',
            title: 'Registro guardado',
            text: 'Operación frontend simulada.',
            confirmButtonColor: '#ad0000'
          });
        }
        return;
      }

      const isEditing = Boolean(currentEditId);
      const url = isEditing 
        ? `${API_BASE}${endpointPath}${currentEditId}/` 
        : `${API_BASE}${endpointPath}`;
      const method = isEditing ? 'PATCH' : 'POST';

      try {
        const res = await fetch(url, {
          method: method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok && data.success) {
          closeModal();
          if (window.Swal) {
            window.Swal.fire({
              icon: 'success',
              title: isEditing ? 'Registro actualizado' : 'Registro creado',
              text: data.message || 'La operación se guardó exitosamente en la base de datos.',
              confirmButtonColor: '#ad0000'
            });
          }
          await loadDataFromApi();
        } else {
          let msg = (data.error && data.error.message) || 'Error al guardar el registro.';
          if (data.error && data.error.details) {
            const detailMsgs = Object.values(data.error.details).flat().join('\n• ');
            if (detailMsgs) msg += `\n\n• ${detailMsgs}`;
          }
          if (window.Swal) {
            window.Swal.fire({
              icon: 'error',
              title: 'No se pudo guardar',
              text: msg,
              confirmButtonColor: '#ad0000'
            });
          }
        }
      } catch (err) {
        if (window.Swal) {
          window.Swal.fire({
            icon: 'error',
            title: 'Error de conexión',
            text: `No se pudo comunicar con el servidor backend: ${err.message}`,
            confirmButtonColor: '#ad0000'
          });
        }
      }
    });
  }

  // 4. Acciones de Tabla (Ver, Editar, Desactivar / Toggle)
  if (tableBody) {
    tableBody.addEventListener('click', async (e) => {
      const btn = e.target.closest('button[data-action]');
      if (!btn) return;
      const action = btn.dataset.action;
      const id = btn.dataset.id;

      if (action === 'toggle-estado' || action === 'desactivar' || action === 'activar') {
        if (!window.Swal) return;

        const row = btn.closest('tr');
        const isCurrentlyActive = (row && row.dataset.status === 'activo');
        const actionTitle = isCurrentlyActive ? '¿Confirmar desactivación?' : '¿Confirmar activación?';
        const actionDesc = isCurrentlyActive 
          ? `Se desactivará el registro #${id} para preservar el historial municipal.` 
          : `Se volverá a activar el registro #${id}.`;

        window.Swal.fire({
          title: actionTitle,
          text: actionDesc,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#ad0000',
          cancelButtonColor: '#65717e',
          confirmButtonText: isCurrentlyActive ? 'Sí, desactivar' : 'Sí, activar',
          cancelButtonText: 'Cancelar'
        }).then(async (result) => {
          if (result.isConfirmed) {
            if (endpointPath) {
              try {
                const res = await fetch(`${API_BASE}${endpointPath}${id}/toggle-estado/`, {
                  method: 'POST'
                });
                const data = await res.json();
                if (res.ok && data.success) {
                  window.Swal.fire({
                    title: 'Operación exitosa',
                    text: data.message || 'El estado ha sido modificado.',
                    icon: 'success',
                    confirmButtonColor: '#ad0000'
                  });
                  await loadDataFromApi();
                } else {
                  window.Swal.fire({
                    title: 'Acción bloqueada',
                    text: (data.error && data.error.message) || 'No se puede modificar el estado.',
                    icon: 'error',
                    confirmButtonColor: '#ad0000'
                  });
                }
              } catch (err) {
                window.Swal.fire({
                  title: 'Error',
                  text: 'Error de comunicación con el backend.',
                  icon: 'error',
                  confirmButtonColor: '#ad0000'
                });
              }
            }
          }
        });
      } else if (action === 'editar') {
        if (!endpointPath) {
          if (modalTitle) modalTitle.textContent = `Editar registro (${id})`;
          if (modal) modal.showModal();
          return;
        }

        try {
          const res = await fetch(`${API_BASE}${endpointPath}${id}/`);
          const data = await res.json();
          if (res.ok && data.success && data.data) {
            currentEditId = id;
            const singularName = pageId === 'subatenciones' ? 'Subatención' 
              : pageId === 'tipos-atencion' ? 'Tipo de Atención' 
              : 'registro';

            if (modalTitle) modalTitle.textContent = `Editar ${singularName} (${data.data.codigo})`;
            if (formEditor) {
              if (formEditor.elements['codigo']) formEditor.elements['codigo'].value = data.data.codigo || '';
              if (formEditor.elements['nombre']) formEditor.elements['nombre'].value = data.data.nombre || '';
              if (formEditor.elements['descripcion']) formEditor.elements['descripcion'].value = data.data.descripcion || '';
              if (formEditor.elements['estado']) formEditor.elements['estado'].value = data.data.estado ? 'Activo' : 'Inactivo';
            }

            if (pageId === 'subatenciones') {
              await populateParentSelect(data.data.tipo_atencion);
            }

            if (modal) modal.showModal();
          }
        } catch (err) {
          console.error('Error al obtener detalle para edición:', err);
        }
      } else if (action === 'ver') {
        if (endpointPath) {
          try {
            const res = await fetch(`${API_BASE}${endpointPath}${id}/`);
            const data = await res.json();
            if (res.ok && data.success && data.data) {
              const item = data.data;
              const extraField = pageId === 'subatenciones' 
                ? `<p><strong>Tipo Padre:</strong> ${escapeHtml(item.tipo_padre_display || '-')}</p>` 
                : '';

              if (window.Swal) {
                window.Swal.fire({
                  title: `Detalle: ${item.codigo}`,
                  html: `
                    <div style="text-align: left; line-height: 1.6;">
                      <p><strong>Nombre:</strong> ${escapeHtml(item.nombre)}</p>
                      ${extraField}
                      <p><strong>Descripción:</strong> ${escapeHtml(item.descripcion || 'Sin descripción')}</p>
                      <p><strong>Estado:</strong> ${item.estado ? '<span style="color: green; font-weight: bold;">Activo</span>' : '<span style="color: red; font-weight: bold;">Inactivo</span>'}</p>
                    </div>
                  `,
                  icon: 'info',
                  confirmButtonColor: '#ad0000'
                });
              }
              return;
            }
          } catch (e) {}
        }
        if (window.Swal) {
          window.Swal.fire({
            title: `Detalle del registro ${id}`,
            text: 'Visualización de solo lectura.',
            icon: 'info',
            confirmButtonColor: '#ad0000'
          });
        }
      }
    });
  }

  // 5. Botón Exportar a Excel
  if (btnExport) {
    btnExport.addEventListener('click', () => {
      if (endpointPath) {
        const term = (searchInput ? searchInput.value.trim() : '');
        const rawStatus = (statusFilter ? statusFilter.value.toLowerCase() : 'todos');
        const estado = (rawStatus === 'activo' || rawStatus === 'activos') ? 'activos' 
          : (rawStatus === 'inactivo' || rawStatus === 'inactivos') ? 'inactivos' 
          : 'todos';

        const downloadUrl = `${API_BASE}${endpointPath}export/?search=${encodeURIComponent(term)}&estado=${encodeURIComponent(estado)}`;
        window.location.href = downloadUrl;
      } else {
        if (window.Swal) {
          window.Swal.fire({
            icon: 'info',
            title: 'Exportación a Excel',
            text: 'Generando archivo con los registros visibles del listado.',
            confirmButtonColor: '#ad0000'
          });
        }
      }
    });
  }

  // Iniciar carga inicial
  loadDataFromApi();
});
