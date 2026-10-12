/**
 * Módulo reutilizable de lógica común para los 6 Mantenedores CRUD (M-14 al M-19)
 * Controla: Búsqueda dinámica, filtro de estado, modal <dialog>, acciones y SweetAlert2.
 * Cumple con el Patrón Común para los seis CRUD (Sección 8 de la Guía de desarrollo).
 */
document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search-input');
  const statusFilter = document.getElementById('status-filter');
  const tableBody = document.getElementById('table-body');
  const btnNuevo = document.getElementById('btn-nuevo');
  const btnExport = document.getElementById('btn-export');
  const modal = document.getElementById('modal-editor');
  const modalClose = document.getElementById('modal-close');
  const modalCancel = document.getElementById('modal-cancel');
  const formEditor = document.getElementById('form-editor');
  const modalTitle = document.getElementById('modal-title');

  // 1. Filtrado dinámico en frontend
  function filterRows() {
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

  if (searchInput) searchInput.addEventListener('input', filterRows);
  if (statusFilter) statusFilter.addEventListener('change', filterRows);

  // 2. Control del Modal Dialog
  if (btnNuevo && modal) {
    btnNuevo.addEventListener('click', () => {
      if (modalTitle) modalTitle.textContent = 'Nuevo registro';
      if (formEditor) formEditor.reset();
      modal.showModal();
    });
  }

  function closeModal() {
    if (modal) modal.close();
  }

  if (modalClose) modalClose.addEventListener('click', closeModal);
  if (modalCancel) modalCancel.addEventListener('click', closeModal);

  // 3. Envío de Formulario con SweetAlert2
  if (formEditor) {
    formEditor.addEventListener('submit', (e) => {
      e.preventDefault();
      closeModal();
      if (window.Swal) {
        window.Swal.fire({
          icon: 'success',
          title: 'Registro guardado',
          text: 'La operación frontend se completó exitosamente.',
          confirmButtonColor: '#ad0000',
          confirmButtonText: 'Aceptar'
        });
      }
    });
  }

  // 4. Acciones de Tabla (Ver, Editar, Desactivar)
  if (tableBody) {
    tableBody.addEventListener('click', (e) => {
      const btn = e.target.closest('button[data-action]');
      if (!btn) return;
      const action = btn.dataset.action;
      const id = btn.dataset.id || 'registro';

      if (action === 'desactivar') {
        if (window.Swal) {
          window.Swal.fire({
            title: '¿Confirmar desactivación?',
            text: `Se desactivará el registro ${id} para conservar el historial.`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#ad0000',
            cancelButtonColor: '#65717e',
            confirmButtonText: 'Sí, desactivar',
            cancelButtonText: 'Cancelar'
          }).then((result) => {
            if (result.isConfirmed) {
              window.Swal.fire({
                title: 'Desactivado',
                text: `El registro ${id} ha sido desactivado.`,
                icon: 'success',
                confirmButtonColor: '#ad0000'
              });
            }
          });
        }
      } else if (action === 'editar') {
        if (modalTitle) modalTitle.textContent = `Editar registro (${id})`;
        if (modal) modal.showModal();
      } else if (action === 'ver') {
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
      if (window.Swal) {
        window.Swal.fire({
          icon: 'info',
          title: 'Exportación a Excel',
          text: 'Generando archivo con los registros visibles del listado.',
          confirmButtonColor: '#ad0000'
        });
      }
    });
  }
});
