/**
 * Módulo reutilizable de lógica común para los Mantenedores CRUD (Consolidado T11, T12, T09)
 * Conexión completa Frontend <-> Backend API REST
 * Controla: Paginación real del servidor, búsqueda dinámica, CSRF Token para seguridad,
 * y renderizado adaptativo de columnas (Roles usa 4 columnas, el resto 5).
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
  
  // Botones de paginación
  const btnPrev = document.querySelector('.pagebuttons button:first-child');
  const btnNext = document.querySelector('.pagebuttons button:last-child');
  const pageNumberDisplay = document.querySelector('.pagebuttons button:nth-child(2)');

  const ENDPOINT_MAP = {
    'tipos-atencion': '/api/tipos-atencion/',
    'subatenciones': '/api/subatenciones/',
    'delegaciones': '/api/delegaciones/',
    'roles': '/api/roles/',
    'usuarios': '/api/usuarios/',
    'items-metas': '/api/items-metas/'
  };

  const endpointPath = ENDPOINT_MAP[pageId];
  const API_BASE = window.location.origin.includes(':8000') ? '' : 'http://127.0.0.1:8000';

  let currentEditId = null;
  let backendActive = false;
  
  // Control de paginación T11
  let currentPage = 1;
  let hasNextPage = false;
  let hasPrevPage = false;

  // Función para obtener el CSRF Token de Django
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  async function populateParentSelect(selectedId = null) {
    const selectPadre = document.getElementById('campo-padre');
    if (!selectPadre) return;
    try {
      const res = await fetch(`${API_BASE}/api/tipos-atencion/?estado=activos&page_size=100`, { credentials: "include" });
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
          if (selectedId && (String(selectedId) === String(tipo.id) || selectedId === tipo.codigo)) opt.selected = true;
          selectPadre.appendChild(opt);
        });
      }
    } catch (e) {
      console.warn('Error al cargar catálogo padre:', e);
    }
  }

  // 1. Carga de datos con Paginación (T11)
  async function loadDataFromApi() {
    if (!endpointPath || !tableBody) return;

    const term = (searchInput ? searchInput.value.trim() : '');
    const rawStatus = (statusFilter ? statusFilter.value.toLowerCase() : 'todos');
    const estado = (rawStatus === 'activo' || rawStatus === 'activos') ? 'activos' 
      : (rawStatus === 'inactivo' || rawStatus === 'inactivos') ? 'inactivos' : 'todos';

    // Agregamos page_size y page actual
    const url = `${API_BASE}${endpointPath}?search=${encodeURIComponent(term)}&estado=${encodeURIComponent(estado)}&page_size=50&page=${currentPage}`;

    try {
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      
      if (data.success && Array.isArray(data.results)) {
        backendActive = true;
        
        // Actualizar variables de paginación según la respuesta de Django
        hasNextPage = data.next !== null;
        hasPrevPage = data.previous !== null;
        updatePaginationUI();

        renderTableRows(data.results);
        if (pageInfo) {
          pageInfo.textContent = `Mostrando ${data.results.length} de ${data.count} registros (Página ${currentPage})`;
        }
      }
    } catch (err) {
      console.warn('Modo offline o error:', err.message);
      filterRowsFrontend();
    }
  }

  function updatePaginationUI() {
    if (btnPrev) btnPrev.disabled = !hasPrevPage;
    if (btnNext) btnNext.disabled = !hasNextPage;
    if (pageNumberDisplay) pageNumberDisplay.textContent = currentPage;
  }

  // Eventos de Paginación
  if (btnPrev) {
    btnPrev.addEventListener('click', () => {
      if (hasPrevPage) { currentPage--; loadDataFromApi(); }
    });
  }
  if (btnNext) {
    btnNext.addEventListener('click', () => {
      if (hasNextPage) { currentPage++; loadDataFromApi(); }
    });
  }

  // Al escribir en buscar o cambiar estado, volvemos a la página 1
  let searchTimeout = null;
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        currentPage = 1;
        if (backendActive) loadDataFromApi(); else filterRowsFrontend();
      }, 300);
    });
  }

  if (statusFilter) {
    statusFilter.addEventListener('change', () => {
      currentPage = 1;
      if (backendActive) loadDataFromApi(); else filterRowsFrontend();
    });
  }

  // RENDERIZADO CONDICIONAL DE FILAS (Ajustado para Roles)
  function renderTableRows(items) {
    if (!tableBody) return;
    tableBody.innerHTML = '';

    if (items.length === 0) {
      const colSpan = (pageId === 'roles') ? "4" : "5";
      tableBody.innerHTML = `<tr><td colspan="${colSpan}" style="text-align: center; padding: 24px; color: var(--muted);">No se encontraron registros.</td></tr>`;
      return;
    }

    items.forEach(item => {
      const tr = document.createElement('tr');
      const isActivo = item.estado === true;
      tr.dataset.status = isActivo ? 'activo' : 'inactivo';

      const badgeHtml = isActivo ? '<span class="badge green">Activo</span>' : '<span class="badge red">Inactivo</span>';
      const toggleActionText = isActivo ? 'Desactivar' : 'Activar';

      // --- RENDERIZADO EXCLUSIVO PARA ROLES (4 COLUMNAS) ---
      if (pageId === 'roles') {
        tr.innerHTML = `
          <td><strong>${escapeHtml(item.nombre || '-')}</strong></td>
          <td>${escapeHtml(item.descripcion || '-')}</td>
          <td>${badgeHtml}</td>
          <td>
            <button type="button" class="linkbtn" data-action="ver" data-id="${item.id}">Ver</button> · 
            <button type="button" class="linkbtn" data-action="editar" data-id="${item.id}">Editar</button> · 
            <button type="button" class="linkbtn" data-action="toggle-estado" data-id="${item.id}">${toggleActionText}</button>
          </td>
        `;
      } 
      // --- RENDERIZADO ESTÁNDAR (5 COLUMNAS) ---
      else {
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
      }
      tableBody.appendChild(tr);
    });
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, s => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[s]);
  }

  function filterRowsFrontend() {
    if (!tableBody) return;
    const term = (searchInput ? searchInput.value.toLowerCase().trim() : '');
    const status = (statusFilter ? statusFilter.value.toLowerCase() : 'todos');
    const rows = tableBody.querySelectorAll('tr');

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const rowStatus = (row.dataset.status || '').toLowerCase();
      row.style.display = ((!term || text.includes(term)) && (status === 'todos' || rowStatus === status)) ? '' : 'none';
    });
  }

  // 2. Control del Modal Dialog
  if (btnNuevo && modal) {
    btnNuevo.addEventListener('click', async () => {
      currentEditId = null;
      const isMasculine = (pageId === 'items-metas');
      const singularName = pageId === 'subatenciones' ? 'Subatención' 
         : pageId === 'tipos-atencion' ? 'Tipo de Atención' 
         : pageId === 'items-metas' ? 'Ítem' 
         : pageId === 'roles' ? 'Rol' : 'registro';

      if (modalTitle) modalTitle.textContent = `${isMasculine ? 'Nuevo' : 'Nueva'} ${singularName}`;
      if (formEditor) {
        formEditor.reset();
        const inputEstado = formEditor.elements['estado'];
        if (inputEstado) inputEstado.value = 'Activo';
      }

      if (pageId === 'subatenciones') await populateParentSelect();
      modal.showModal();
    });
  }

  function closeModal() { if (modal) modal.close(); currentEditId = null; }
  if (modalClose) modalClose.addEventListener('click', closeModal);
  if (modalCancel) modalCancel.addEventListener('click', closeModal);

  // 3. Envío de Formulario Seguro
  if (formEditor) {
    formEditor.addEventListener('submit', async (e) => {
      e.preventDefault();

      const payload = {
        nombre: formEditor.elements['nombre']?.value?.trim(),
        estado: (formEditor.elements['estado']?.value || 'Activo').toLowerCase() === 'activo'
      };
      
      const codigoVal = formEditor.elements['codigo']?.value?.trim();
      if (codigoVal !== undefined) payload.codigo = codigoVal;

      const descVal = formEditor.elements['descripcion']?.value?.trim();
      if (descVal !== undefined) payload.descripcion = descVal;

      if (pageId === 'subatenciones') {
        const parentVal = formEditor.elements['tipo_padre']?.value || formEditor.elements['tipo_atencion']?.value;
        if (!parentVal) { window.Swal?.fire({icon: 'warning', title: 'Requerido', text: 'Seleccione un Tipo de Atención'}); return; }
        payload.tipo_atencion = parentVal;
      }

      const url = currentEditId ? `${API_BASE}${endpointPath}${currentEditId}/` : `${API_BASE}${endpointPath}`;
      
      try {
        const res = await fetch(url, {
          method: currentEditId ? 'PATCH' : 'POST',
          headers: { 
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken') || ''
          },
          credentials: "include",
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (res.ok && data.success) {
          closeModal();
          window.Swal?.fire({icon: 'success', title: 'Éxito', text: data.message});
          await loadDataFromApi();
        } else {
          window.Swal?.fire({icon: 'error', title: 'Error', text: data.error?.message || 'No se pudo guardar'});
        }
      } catch (err) {
        window.Swal?.fire({icon: 'error', title: 'Error', text: 'Error de conexión.'});
      }
    });
  }

  // 4. Acciones de Tabla Seguras
  if (tableBody) {
    tableBody.addEventListener('click', async (e) => {
      const btn = e.target.closest('button[data-action]');
      if (!btn) return;
      const { action, id } = btn.dataset;

      if (action === 'toggle-estado') {
        window.Swal?.fire({
          title: '¿Cambiar estado?',
          icon: 'warning',
          showCancelButton: true,
          confirmButtonColor: '#ad0000',
          confirmButtonText: 'Sí, cambiar',
        }).then(async (result) => {
          if (result.isConfirmed) {
            try {
              const res = await fetch(`${API_BASE}${endpointPath}${id}/toggle-estado/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') || '' },
                credentials: "include"
              });
              const data = await res.json();
              if (res.ok && data.success) {
                window.Swal.fire('Éxito', data.message, 'success');
                await loadDataFromApi();
              } else {
                window.Swal.fire('Error', data.error?.message || 'Error al cambiar estado.', 'error');
              }
            } catch (err) {
              window.Swal.fire('Error', 'Error de comunicación', 'error');
            }
          }
        });
      } else if (action === 'editar' || action === 'ver') {
        try {
          const res = await fetch(`${API_BASE}${endpointPath}${id}/`, { credentials: "include" });
          const data = await res.json();
          if (res.ok && data.success && data.data) {
            const item = data.data;
            if (action === 'ver') {
                window.Swal?.fire({
                  title: `Detalle: ${escapeHtml(item.codigo || item.nombre || '')}`,
                  html: `<div style="text-align: left;"><p><strong>Nombre:</strong> ${escapeHtml(item.nombre || '-')}</p><p><strong>Estado:</strong> ${item.estado ? 'Activo' : 'Inactivo'}</p></div>`,
                  icon: 'info',
                  confirmButtonColor: '#ad0000'
                });
            } else {
                currentEditId = id;
                if (modalTitle) modalTitle.textContent = `Editar (${item.codigo || item.nombre})`;
                if (formEditor) {
                  if (formEditor.elements['codigo']) formEditor.elements['codigo'].value = item.codigo || '';
                  if (formEditor.elements['nombre']) formEditor.elements['nombre'].value = item.nombre || '';
                  if (formEditor.elements['descripcion']) formEditor.elements['descripcion'].value = item.descripcion || '';
                  if (formEditor.elements['estado']) formEditor.elements['estado'].value = item.estado ? 'Activo' : 'Inactivo';
                }
                if (pageId === 'subatenciones') await populateParentSelect(item.tipo_atencion);
                modal.showModal();
            }
          }
        } catch (err) { console.error(err); }
      }
    });
  }

  if (btnExport) {
    btnExport.addEventListener('click', () => {
      const term = (searchInput ? searchInput.value.trim() : '');
      const rawStatus = (statusFilter ? statusFilter.value.toLowerCase() : 'todos');
      const estado = (rawStatus === 'activo' || rawStatus === 'activos') ? 'activos' 
        : (rawStatus === 'inactivo' || rawStatus === 'inactivos') ? 'inactivos' : 'todos';
      window.location.href = `${API_BASE}${endpointPath}export/?search=${encodeURIComponent(term)}&estado=${encodeURIComponent(estado)}`;
    });
  }

  // Recargar datos cuando se cambia el ámbito territorial desde la cabecera
  window.addEventListener('sgr:delegacion-cambiada', () => {
    loadDataFromApi();
  });

  loadDataFromApi();
});