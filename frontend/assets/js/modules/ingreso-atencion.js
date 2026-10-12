/**
 * Módulo de pantalla M-20: Ingreso de atención ciudadana
 * Maneja la dependencia dinámica Tipo -> Subtipo, visibilidad de Caso Social y validación con SweetAlert2.
 * Cumple con la Sección 12 de la Guía de desarrollo del SGR.
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-atencion');
  const tipoSelect = document.getElementById('tipo-atencion');
  const subtipoSelect = document.getElementById('subtipo-atencion');
  const solicitanteInput = document.getElementById('solicitante');
  const descInput = document.getElementById('descripcion-atencion');
  const socialCaseSection = document.getElementById('seccion-caso-social');
  const btnCancelar = document.getElementById('btn-cancelar');
  const btnGuardar = document.getElementById('btn-guardar');

  // Catálogo hijo dependiente
  const subatencionesMap = {
    'Social': [
      'Orientación y Asistencia Social Directa',
      'Subsidios y Beneficios Municipales',
      'Entrega de Ayudas Técnicas'
    ],
    'Territorial': [
      'Solicitud de Operativo Territorial',
      'Audiencia con Junta de Vecinos',
      'Inspección de Espacio Público'
    ],
    'Orientación Jurídica': [
      'Asesoría Jurídica Vecinal',
      'Mediación Comunitaria',
      'Derivación a Corporación de Asistencia Judicial'
    ]
  };

  // 1. Carga dependiente de subtipos
  if (tipoSelect && subtipoSelect) {
    tipoSelect.addEventListener('change', () => {
      const selectedTipo = tipoSelect.value;
      subtipoSelect.innerHTML = '';

      if (!selectedTipo || !subatencionesMap[selectedTipo]) {
        subtipoSelect.disabled = true;
        subtipoSelect.innerHTML = '<option value="">-- Selecciona primero el tipo --</option>';
        if (socialCaseSection) socialCaseSection.style.display = 'none';
        return;
      }

      subtipoSelect.disabled = false;
      subtipoSelect.innerHTML = '<option value="">-- Seleccionar subatención --</option>';

      subatencionesMap[selectedTipo].forEach(sub => {
        const opt = document.createElement('option');
        opt.value = sub;
        opt.textContent = sub;
        subtipoSelect.appendChild(opt);
      });

      // Mostrar u ocultar sección de Caso Social
      if (socialCaseSection) {
        socialCaseSection.style.display = (selectedTipo === 'Social') ? 'block' : 'none';
      }
    });
  }

  // 2. Cancelar y advertir cambios sin guardar
  if (btnCancelar) {
    btnCancelar.addEventListener('click', () => {
      if (solicitanteInput.value.trim() || descInput.value.trim()) {
        if (window.Swal) {
          window.Swal.fire({
            title: '¿Descartar cambios?',
            text: 'Tienes información ingresada que no se ha guardado.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#ad0000',
            cancelButtonColor: '#65717e',
            confirmButtonText: 'Sí, limpiar formulario',
            cancelButtonText: 'Continuar editando'
          }).then((result) => {
            if (result.isConfirmed) {
              form.reset();
              if (tipoSelect) tipoSelect.dispatchEvent(new Event('change'));
            }
          });
        }
      } else {
        form.reset();
      }
    });
  }

  // 3. Envío y validación con prevención de doble clic
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();

      const solicitante = solicitanteInput.value.trim();
      const tipo = tipoSelect.value;
      const subtipo = subtipoSelect.value;
      const desc = descInput.value.trim();

      if (!solicitante || !tipo || !subtipo || !desc) {
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
      btnGuardar.disabled = true;
      btnGuardar.textContent = 'Registrando atención...';

      setTimeout(() => {
        btnGuardar.disabled = false;
        btnGuardar.textContent = 'Guardar atención ciudadana →';

        const folioGenerado = 'AT-2026-' + Math.floor(1000 + Math.random() * 9000);

        if (window.Swal) {
          window.Swal.fire({
            icon: 'success',
            title: '¡Atención registrada!',
            html: `<p>Se ha generado la atención con folio <strong>${folioGenerado}</strong>.</p><p style="font-size:13px;color:#65717e;margin-top:8px">Solicitante: <strong>${escapeHtml(solicitante)}</strong><br>Delegación: DEL01 · Las Compañías</p>`,
            confirmButtonColor: '#ad0000',
            confirmButtonText: 'Aceptar'
          }).then(() => {
            form.reset();
            if (tipoSelect) tipoSelect.dispatchEvent(new Event('change'));
          });
        }
      }, 700);
    });
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }
});
