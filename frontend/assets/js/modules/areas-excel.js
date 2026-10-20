/* Incorporación explícita del catálogo de referencia; nunca asigna personas. */
document.addEventListener('DOMContentLoaded', async () => {
  if (document.body.dataset.page !== 'cargos') return;
  let session;
  try { session = await window.SGRSession; } catch { return; }
  if (!session.permisos.includes('cargos.crear') || !session.permisos.includes('cargos.ver')) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'button secondary';
  button.textContent = 'Incorporar áreas del Excel';
  document.getElementById('btn-nuevo').before(button);
  button.onclick = async () => {
    button.disabled = true;
    try {
      const plan = (await SGRApi.request('/api/cargos/referencia-excel/')).data;
      const content = document.createElement('div');
      content.style.maxHeight = '55vh';
      content.style.overflow = 'auto';
      const source = document.createElement('p');
      source.textContent = 'Referencia: ' + plan.source + ' · SEMAFORO B4:B15.';
      content.append(source);
      const wrapper = document.createElement('div');
      wrapper.className = 'tablewrap';
      const table = document.createElement('table');
      table.setAttribute('aria-label', 'Áreas operativas de referencia');
      const head = table.createTHead().insertRow();
      for (const label of ['Área operativa', 'Familia', 'Planilla', 'Resultado']) {
        const th = document.createElement('th'); th.scope = 'col'; th.textContent = label; head.append(th);
      }
      const body = table.createTBody();
      for (const row of plan.entries) {
        const tr = body.insertRow();
        for (const value of [row.nombre, row.area, row.planilla, row.detail]) tr.insertCell().textContent = value;
      }
      wrapper.append(table); content.append(wrapper);
      for (const text of plan.notes) {
        const note = document.createElement('p'); note.textContent = text; content.append(note);
      }
      const canApply = plan.summary.create > 0 && plan.summary.conflict === 0;
      const result = await Swal.fire({
        title: 'Áreas del Excel: revisar incorporación', html: content, width: 'min(1000px, 95vw)',
        footer: `${plan.summary.create} por incorporar · ${plan.summary.keep} conservadas · ${plan.summary.conflict} incompatibles`,
        showCancelButton: canApply, confirmButtonText: canApply ? 'Incorporar faltantes' : 'Cerrar',
        cancelButtonText: 'Cancelar', confirmButtonColor: '#AD0000'
      });
      if (!canApply || !result.isConfirmed) return;
      const applied = (await SGRApi.send('/api/cargos/referencia-excel/', {confirmar: true})).data;
      await SGRApi.message(`${applied.created} áreas incorporadas. Las cuentas existentes conservan su asignación. Para asignar un área, edita el usuario en Administración → Usuarios.`, 'success');
      location.reload();
    } catch (error) {
      await SGRApi.message(error.message);
    } finally { button.disabled = false; }
  };
});
