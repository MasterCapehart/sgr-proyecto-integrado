document.addEventListener('DOMContentLoaded', async () => {
  try {
    const c = await SGRSession;
    const target = document.getElementById('home-modules');
    const actions = document.createElement('div');
    actions.className = 'primary-actions';

    const ACTION_ICONS = {
      'ingreso-atencion': `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>`,
      'desempeno': `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>`,
      'tubo-trabajo': `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
      'validacion': `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`
    };

    for (const [perm, file, label] of [
      ['atenciones.crear', 'ingreso-atencion', 'Registrar atención'],
      ['actividades.crear', 'desempeno', 'Abrir mi planilla'],
      ['compromisos.ver', 'tubo-trabajo', 'Consultar tubo de trabajo'],
      ['evidencias.revisar', 'validacion', 'Revisar evidencias']
    ]) {
      if (c.permisos.includes(perm)) {
        const link = document.createElement('a');
        link.href = 'pages/' + file + '.html';
        const isPrimary = actions.children.length === 0;
        link.className = 'button ' + (isPrimary ? 'primary' : 'secondary');
        const iconSvg = ACTION_ICONS[file] || '';
        link.innerHTML = `${iconSvg} <span>${label}</span>`;
        actions.append(link);
      }
    }
    target.before(actions);

    SGRProgress.mount(target);

    const indicators = SGRKpis.mount(target);
    SGRApi.request('/api/indicadores/')
      .then(r => SGRKpis.update(indicators, r.data))
      .catch(() => SGRKpis.error(indicators));

    const CARD_ICONS = {
      desempeno: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>`,
      evidencias: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>`,
      'tubo-trabajo': `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
      validacion: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
      'ingreso-atencion': `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>`,
      reportes: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`
    };

    const cards = [
      ['actividades.ver', 'desempeno', 'Mi planilla de trabajo', 'Registra solicitudes, acciones de terreno y el ítem asociado.'],
      ['evidencias.ver', 'evidencias', 'Evidencias', 'Adjunta archivos y consulta el historial de revisión.'],
      ['compromisos.ver', 'tubo-trabajo', 'Tubo de trabajo', 'Responsables, fechas, seguimiento y conversación.'],
      ['evidencias.revisar', 'validacion', 'Validación', 'Revisa y devuelve respaldos con observaciones.'],
      ['atenciones.crear', 'ingreso-atencion', 'Atención ciudadana', 'Ingresa atenciones con sus tipos y subatenciones.'],
      ['reportes.ver', 'reportes', 'Reportes operativos', 'Filtra y exporta los registros autorizados.']
    ];

    for (const [perm, path, title, text] of cards) {
      if (!c.permisos.includes(perm)) continue;
      const a = document.createElement('a');
      a.href = 'pages/' + path + '.html';
      a.className = 'card module-card';
      const b = document.createElement('div');
      b.className = 'body';

      const iconDiv = document.createElement('div');
      iconDiv.className = 'module-icon';
      iconDiv.innerHTML = CARD_ICONS[path] || '';

      const h = document.createElement('h2');
      h.textContent = title;
      const p = document.createElement('p');
      p.textContent = text;

      b.append(iconDiv, h, p);
      a.append(b);
      target.append(a);
    }
  } catch (e) {
    console.error(e);
  }
});
