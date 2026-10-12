/**
 * Módulo de pantalla M-20: Ingreso de atención ciudadana (Tarea T17)
 * Conexión real con API REST Django y persistencia en MySQL sgr_prueba.
 * Controla:
 * - Contexto institucional de sesión (autor, delegación y fecha fija en servidor).
 * - Carga dinámica de catálogos activos (Tipos de Atención y Subatenciones compatibles).
 * - Prevención de inconsistencias y validación con SweetAlert2.
 * - Generación y confirmación con folio e ID reales desde la base de datos.
 * - Cancelar no persiste datos en el servidor.
 */
document.addEventListener('DOMContentLoaded', async () => {
  const form = document.getElementById('form-atencion');
  const tipoSelect = document.getElementById('tipo-atencion');
  const subtipoSelect = document.getElementById('subtipo-atencion');
  const solicitanteInput = document.getElementById('solicitante');
  const descInput = document.getElementById('descripcion-atencion');
  const socialCaseSection = document.getElementById('seccion-caso-social');
  const casoSocialInput = document.getElementById('codigo-caso-social');
  const delegacionInput = document.getElementById('delegacion-contexto');
  const responsableInput = document.getElementById('responsable-nombre');
  const fechaInput = document.getElementById('fecha-registro');
  const btnCancelar = document.getElementById('btn-cancelar');
  const btnGuardar = document.getElementById('btn-guardar');

  const API_BASE = window.location.origin.includes(':8000') ? '' : 'http://127.0.0.1:8000';

  // Caché de tipos cargados para evaluar caso social
  let activeTypesCache = [];

  // 1. Cargar contexto institucional de sesión del servidor
  async function loadServerContext() {
    try {
      const res = await fetch(`${API_BASE}/api/atenciones/contexto/`);
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.data) {
          const d = json.data;
          if (delegacionInput && d.delegacion) {
            delegacionInput.value = d.delegacion.display || d.delegacion.nombre || 'DEL01 · Las Compañías';
          }
          if (responsableInput && d.usuario) {
            responsableInput.value = d.usuario.display || `${d.usuario.nombre_completo} (${d.usuario.rol})`;
          }
          if (fechaInput) {
            fechaInput.value = `Fijada por el servidor al guardar (${d.fecha_display || 'Automática'})`;
          }
        }
      }
    } catch (err) {
      console.warn('No fue posible cargar el contexto de sesión desde el servidor:', err);
    }
  }

  // 2. Cargar catálogo activo de Tipos de Atención
  async function loadActiveTipos() {
    if (!tipoSelect) return;
    try {
      const res = await fetch(`${API_BASE}/api/tipos-atencion/?estado=activos&page_size=100`);
      if (res.ok) {
        const json = await res.json();
        const tipos = json.results || (json.data && json.data.results) || [];
        activeTypesCache = tipos;

        tipoSelect.innerHTML = '<option value="">-- Seleccionar tipo --</option>';
        tipos.forEach(t => {
          const opt = document.createElement('option');
          opt.value = t.id;
          opt.textContent = `${t.codigo} · ${t.nombre}`;
          opt.dataset.nombre = t.nombre;
          tipoSelect.appendChild(opt);
        });
      }
    } catch (err) {
      console.warn('Error al cargar Tipos de Atención desde API:', err);
    }
  }

  // 3. Cargar subatenciones compatibles al seleccionar un Tipo
  if (tipoSelect && subtipoSelect) {
    tipoSelect.addEventListener('change', async () => {
      const selectedTipoId = tipoSelect.value;
      subtipoSelect.innerHTML = '';

      if (!selectedTipoId) {
        subtipoSelect.disabled = true;
        subtipoSelect.innerHTML = '<option value="">-- Selecciona primero el tipo --</option>';
        if (socialCaseSection) socialCaseSection.style.display = 'none';
        if (casoSocialInput) casoSocialInput.value = '';
        return;
      }

      subtipoSelect.disabled = true;
      subtipoSelect.innerHTML = '<option value="">Cargando subatenciones disponibles...</option>';

      // Determinar si aplica Caso Social
      const selectedOption = tipoSelect.options[tipoSelect.selectedIndex];
      const tipoNombre = selectedOption ? (selectedOption.dataset.nombre || selectedOption.textContent) : '';
      const esSocial = tipoNombre.toLowerCase().includes('social');

      if (socialCaseSection) {
        socialCaseSection.style.display = esSocial ? 'block' : 'none';
        if (!esSocial && casoSocialInput) {
          casoSocialInput.value = '';
        }
      }

      try {
        const res = await fetch(`${API_BASE}/api/subatenciones/?tipo_atencion=${selectedTipoId}&estado=activos&page_size=100`);
        if (res.ok) {
          const json = await res.json();
          const subs = json.results || (json.data && json.data.results) || [];

          subtipoSelect.innerHTML = '';
          if (subs.length === 0) {
            subtipoSelect.innerHTML = '<option value="">-- No hay subatenciones activas para este tipo --</option>';
            subtipoSelect.disabled = true;
          } else {
            subtipoSelect.innerHTML = '<option value="">-- Seleccionar subatención --</option>';
            subs.forEach(s => {
              const opt = document.createElement('option');
              opt.value = s.id;
              opt.textContent = `${s.codigo} · ${s.nombre}`;
              subtipoSelect.appendChild(opt);
            });
            subtipoSelect.disabled = false;
          }
        } else {
          subtipoSelect.innerHTML = '<option value="">Error al cargar catálogo dependiente</option>';
        }
      } catch (err) {
        console.error('Error al consultar subatenciones compatibles:', err);
        subtipoSelect.innerHTML = '<option value="">Error de conexión con el servidor</option>';
      }
    });
  }

  // 4. Cancelar y limpiar (garantiza que cancelar NO guarda nada en base de datos)
  if (btnCancelar) {
    btnCancelar.addEventListener('click', () => {
      const tieneDatos = (solicitanteInput && solicitanteInput.value.trim()) ||
                         (descInput && descInput.value.trim()) ||
                         (casoSocialInput && casoSocialInput.value.trim());

      if (tieneDatos) {
        if (window.Swal) {
          window.Swal.fire({
            title: '¿Descartar cambios?',
            text: 'Tienes información ingresada que no se ha guardado en el servidor.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#ad0000',
            cancelButtonColor: '#65717e',
            confirmButtonText: 'Sí, limpiar formulario',
            cancelButtonText: 'Continuar editando'
          }).then((result) => {
            if (result.isConfirmed) {
              form.reset();
              if (tipoSelect) {
                tipoSelect.value = '';
                tipoSelect.dispatchEvent(new Event('change'));
              }
              loadServerContext();
            }
          });
        } else {
          form.reset();
        }
      } else {
        form.reset();
        if (tipoSelect) {
          tipoSelect.value = '';
          tipoSelect.dispatchEvent(new Event('change'));
        }
      }
    });
  }

  // 5. Envío y registro real en el backend con prevención de doble clic
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const solicitante = solicitanteInput ? solicitanteInput.value.trim() : '';
      const tipoId = tipoSelect ? tipoSelect.value : '';
      const subtipoId = subtipoSelect ? subtipoSelect.value : '';
      const desc = descInput ? descInput.value.trim() : '';
      const casoSocial = (casoSocialInput && socialCaseSection && socialCaseSection.style.display !== 'none') 
        ? casoSocialInput.value.trim() 
        : '';

      if (!solicitante || !tipoId || !subtipoId || !desc) {
        if (window.Swal) {
          window.Swal.fire({
            icon: 'warning',
            title: 'Formulario incompleto',
            text: 'Por favor, completa todos los campos obligatorios marcados con asterisco (*).',
            confirmButtonColor: '#ad0000',
            confirmButtonText: 'Entendido'
          });
        }
        return;
      }

      // Prevenir doble clic
      if (btnGuardar) {
        btnGuardar.disabled = true;
        btnGuardar.textContent = 'Guardando en servidor...';
      }

      const payload = {
        solicitante: solicitante,
        tipo_atencion: tipoId,
        sub_atencion: subtipoId,
        descripcion: desc,
        caso_social: casoSocial || null
      };

      try {
        const response = await fetch(`${API_BASE}/api/atenciones/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok && data.success) {
          const atencion = data.data;
          const folioGenerado = atencion.folio || atencion.codigo_atencion || 'AT-2026-XXXX';
          const delegacionNombre = atencion.delegacion ? atencion.delegacion.nombre : 'Delegación Las Compañías';
          const tipoDisplay = atencion.tipo_atencion ? atencion.tipo_atencion.nombre : '';
          const subDisplay = atencion.sub_atencion ? atencion.sub_atencion.nombre : '';

          if (window.Swal) {
            await window.Swal.fire({
              icon: 'success',
              title: '¡Atención registrada!',
              html: `
                <div style="text-align: left; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; margin-top: 10px;">
                  <p style="margin: 0 0 8px; font-size: 15px;">Folio Oficial: <strong style="color: #ad0000; font-size: 16px;">${escapeHtml(folioGenerado)}</strong></p>
                  <p style="margin: 0 0 4px; font-size: 13px; color: #475569;">ID Base de Datos: <strong>#${atencion.id}</strong></p>
                  <p style="margin: 0 0 4px; font-size: 13px; color: #475569;">Solicitante: <strong>${escapeHtml(atencion.solicitante)}</strong></p>
                  <p style="margin: 0 0 4px; font-size: 13px; color: #475569;">Tipo: <strong>${escapeHtml(tipoDisplay)}</strong> · ${escapeHtml(subDisplay)}</p>
                  <p style="margin: 0; font-size: 13px; color: #475569;">Origen: <strong>${escapeHtml(delegacionNombre)}</strong></p>
                </div>
              `,
              confirmButtonColor: '#ad0000',
              confirmButtonText: 'Aceptar'
            });
          }

          // Limpiar formulario tras registro exitoso
          form.reset();
          if (tipoSelect) {
            tipoSelect.value = '';
            tipoSelect.dispatchEvent(new Event('change'));
          }
          await loadServerContext();
        } else {
          // Manejo detallado de errores del servidor
          let errorMsg = data.message || (data.error && data.error.message) || 'No se pudo guardar la atención en el servidor.';
          const details = data.details || (data.error && data.error.details);
          if (details && typeof details === 'object') {
            const detailErrors = Object.entries(details).map(([f, msgs]) => Array.isArray(msgs) ? msgs.join(' ') : String(msgs)).join('<br>');
            if (detailErrors) errorMsg = detailErrors;
          }

          if (window.Swal) {
            window.Swal.fire({
              icon: 'error',
              title: 'Rechazo de Registro',
              html: `<p>${errorMsg}</p>`,
              confirmButtonColor: '#ad0000',
              confirmButtonText: 'Revisar'
            });
          }
        }
      } catch (err) {
        console.error('Error al registrar atención:', err);
        if (window.Swal) {
          window.Swal.fire({
            icon: 'error',
            title: 'Error de Conexión',
            text: 'No fue posible comunicar con el servidor Django. Verifica que el backend esté activo.',
            confirmButtonColor: '#ad0000',
            confirmButtonText: 'Entendido'
          });
        }
      } finally {
        if (btnGuardar) {
          btnGuardar.disabled = false;
          btnGuardar.textContent = 'Guardar atención ciudadana →';
        }
      }
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Inicializar contexto y catálogos en vivo
  await loadServerContext();
  await loadActiveTipos();
});
