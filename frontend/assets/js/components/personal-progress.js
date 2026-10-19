/* Panel personal: la autorización y el alcance proceden del servidor. */
(() => {
  const node = (tag, cls, text) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  };
  const number = v => Number(v).toLocaleString('es-CL');
  const link = (title, url) => {
    const a = node('a', 'progress-link', title);
    // Solo enlaces locales a pantallas conocidas; nunca esquemas externos.
    if (/^pages\/[a-z-]+\.html(?:\?[a-z]+=[0-9]+)?$/.test(url)) a.href = url;
    return a;
  };
  function metric(title, value, help) {
    const card = node('article', 'personal-metric');
    card.append(node('h3', null, title), node('p', 'personal-number', value), node('p', 'progress-muted', help));
    return card;
  }
  function render(body, data) {
    body.replaceChildren();
    const pending = node('section', 'progress-panel personal-pending');
    pending.setAttribute('aria-label', 'Mis pendientes');
    const heading = node('div', 'progress-panel-heading');
    heading.append(node('h2', null, 'Mis pendientes'), node('span', 'progress-context', 'Primero lo que requiere tu atención'));
    pending.append(heading, node('p', 'progress-muted', 'Incluye registros abiertos de todo el historial, aunque cambies el mes del resumen.'));
    const badges = node('div', 'progress-counts');
    for (const [key, label] of [['overdue', 'compromisos vencidos'], ['commitments', 'compromisos abiertos'], ['correction', 'evidencias por corregir'], ['activity_correction', 'actividades por corregir'], ['drafts', 'actividades en borrador'], ['review', 'evidencias que debes revisar']]) {
      if (data.pending[key] !== null) badges.append(node('span', key === 'overdue' && data.pending[key] ? 'progress-count urgent' : 'progress-count', `${number(data.pending[key])} ${label}`));
    }
    pending.append(badges);
    const names = { commitment: 'Compromiso asignado', correction: 'Corregir evidencia', review: 'Revisar evidencia de otra persona', draft: 'Completar actividad en borrador', activity_correction: 'Corregir actividad' };
    const priorities = { overdue: 'Vencido', action: 'Requiere tu acción', soon: 'Vence dentro de 7 días', normal: 'Pendiente' };
    if (!data.tasks.length) pending.append(node('p', 'progress-empty', 'No tienes tareas pendientes para mostrar con tus permisos actuales.'));
    else {
      const list = node('ul', 'personal-task-list');
      for (const task of data.tasks) {
        const li = node('li', 'personal-task');
        const content = node('div', 'personal-task-content');
        content.append(node('span', 'progress-task-kind', names[task.kind] || 'Registro pendiente'), node('p', 'progress-task-title', task.title));
        content.querySelector('.progress-task-title').title = task.title;
        const meta = node('div', 'progress-task-meta');
        meta.append(node('span', task.priority === 'overdue' ? 'progress-status overdue' : 'progress-status', priorities[task.priority]));
        if (task.due) {
          const time = node('time', null, 'Plazo: ' + new Date(task.due + 'T12:00:00').toLocaleDateString('es-CL'));
          time.dateTime = task.due; meta.append(time);
        }
        content.append(meta);
        const action = link(task.kind === 'review' ? 'Ir a revisar →' : 'Abrir registro →', task.url);
        action.setAttribute('aria-label', (task.kind === 'review' ? 'Revisar: ' : 'Abrir: ') + task.title);
        li.append(content, action); list.append(li);
      }
      pending.append(list, node('p', 'progress-muted progress-list-note', 'Se muestran hasta 12 tareas priorizadas. Los contadores incluyen todos los resultados; consulta cada módulo para ver el listado completo.'));
    }
    if (data.pending.waiting !== null) pending.append(node('p', 'progress-waiting', `${number(data.pending.waiting)} evidencias tuyas están esperando revisión de otra persona. No son tareas que debas revisar tú.`));
    body.append(pending);

    const month = data.month;
    const grid = node('section', 'personal-metrics');
    grid.setAttribute('aria-label', 'Mi progreso del mes seleccionado');
    if (month.attentions !== null) grid.append(metric('Mis atenciones', number(month.attentions), 'Registradas por ti durante el mes.'));
    if (month.activities !== null) grid.append(metric('Mis actividades', number(month.activities), 'Creadas por ti durante el mes.'));
    if (month.commitments !== null) {
      const c = month.commitments;
      const card = metric('Mis compromisos', `${number(c.closed)} de ${number(c.total)}`, 'Asignados a ti y creados en el mes; estado actual.');
      if (c.percent !== null) {
        const bar = node('div', 'personal-meter');
        bar.setAttribute('role', 'progressbar'); bar.setAttribute('aria-label', 'Porcentaje de compromisos realizados');
        bar.setAttribute('aria-valuemin', '0'); bar.setAttribute('aria-valuemax', '100'); bar.setAttribute('aria-valuenow', String(c.percent));
        const fill = node('span'); fill.style.width = c.percent + '%'; bar.append(fill);
        card.append(bar, node('p', 'progress-muted', c.percent + ' % realizados'));
      } else card.append(node('p', 'progress-muted', 'Sin compromisos registrados en este mes.'));
      grid.append(card);
    }
    if (month.evidence !== null) grid.append(metric('Mis evidencias por revisar', number(month.evidence.waiting), 'Enviadas en el mes; esperan revisión de otra persona.'));
    body.append(grid);

    const charts = node('div', 'personal-charts');
    if (month.attentions !== null || month.activities !== null) {
      const chart = node('section', 'progress-panel');
      chart.append(node('h2', null, 'Mi actividad por semana'), node('p', 'progress-muted', 'Conteos de registros creados en cada tramo del mes.'));
      const legend = node('div', 'personal-legend');
      if (month.attentions !== null) legend.append(node('span', 'series-attentions', '■ Atenciones'));
      if (month.activities !== null) legend.append(node('span', 'series-activities', '■ Actividades'));
      chart.append(legend);
      const bars = node('div', 'personal-chart'); bars.setAttribute('aria-hidden', 'true');
      const max = Math.max(1, ...data.weeks.flatMap(w => [w.attentions || 0, w.activities || 0]));
      for (const week of data.weeks) {
        const column = node('div', 'personal-week'); const pair = node('div', 'personal-bar-pair');
        for (const [key, cls] of [['attentions', 'bar-attentions'], ['activities', 'bar-activities']]) {
          if (week[key] === null) continue;
          const bar = node('div', 'personal-bar ' + cls); bar.style.height = (week[key] / max * 100) + '%';
          bar.append(node('span', null, number(week[key]))); pair.append(bar);
        }
        column.append(pair, node('span', 'personal-week-label', week.label)); bars.append(column);
      }
      chart.append(bars);
      const details = node('details', 'personal-chart-data'); details.append(node('summary', null, 'Ver datos del gráfico'));
      const table = node('table'); const head = node('tr');
      head.append(node('th', null, 'Días del mes'));
      const keys = [['attentions', 'Atenciones'], ['activities', 'Actividades']].filter(([k]) => month[k] !== null);
      for (const [, label] of keys) { const th = node('th', null, label); th.scope = 'col'; head.append(th); }
      const thead = node('thead'); thead.append(head); table.append(thead); const tbody = node('tbody');
      for (const week of data.weeks) { const row = node('tr'); const th = node('th', null, week.label); th.scope = 'row'; row.append(th); for (const [key] of keys) row.append(node('td', null, number(week[key]))); tbody.append(row); }
      table.append(tbody); details.append(table); chart.append(details); charts.append(chart);
    }
    if (month.evidence !== null) {
      const panel = node('section', 'progress-panel'); panel.append(node('h2', null, 'Estado de mis evidencias'), node('p', 'progress-muted', 'Versiones vigentes creadas en el mes. No incluye anuladas ni versiones reemplazadas.'));
      const e = month.evidence, total = e.approved + e.waiting + e.correction;
      for (const [key, label] of [['approved', 'Aprobadas'], ['waiting', 'Esperando revisión'], ['correction', 'Corrección o rechazo']]) {
        const row = node('div', 'personal-evidence-row'); row.append(node('span', null, label), node('strong', null, `${number(e[key])} de ${number(total)}`));
        const meter = node('div', 'personal-evidence-meter'); const fill = node('span', key); fill.style.width = (total ? e[key] / total * 100 : 0) + '%'; meter.append(fill); panel.append(row, meter);
      }
      if (!total) panel.append(node('p', 'progress-empty', 'No tienes evidencias vigentes creadas en este mes.'));
      charts.append(panel);
    }
    body.append(charts, node('p', 'progress-caption', data.scope + ' Los porcentajes describen estados actuales; no calculan metas oficiales ni evalúan desempeño.'));
    if (data.generated_at) { const time = node('time', 'progress-updated', 'Actualizado ' + new Date(data.generated_at).toLocaleString('es-CL')); time.dateTime = data.generated_at; body.append(time); }
    if (!grid.children.length && !data.tasks.length) body.append(node('p', 'progress-empty', 'Tu perfil no dispone de permisos de consulta para estos módulos.'));
  }
  function mount(before) {
    const section = node('section', 'personal-progress'); section.setAttribute('aria-label', 'Mi progreso personal');
    const header = node('div', 'personal-progress-header'); const text = node('div');
    text.append(node('p', 'eyebrow', 'Tu gestión personal'), node('h2', 'personal-progress-title', 'Mi progreso'));
    const label = node('label', 'personal-period'); label.append(node('span', null, 'Mes del resumen'));
    const select = node('select'); label.append(select);
    const now = new Date();
    for (let i = 0; i < 12; i++) {
      const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
      const value = date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0');
      select.add(new Option(date.toLocaleDateString('es-CL', { month: 'long', year: 'numeric' }), value));
    }
    header.append(text, label); const body = node('div'); body.setAttribute('aria-live', 'polite'); section.append(header, body); before.before(section);
    let revision = 0;
    const load = async () => {
      const current = ++revision; body.setAttribute('aria-busy', 'true');
      body.replaceChildren(node('p', 'progress-loading', 'Cargando tus pendientes y progreso…'));
      try { const result = await SGRApi.request('/api/mi-progreso/?mes=' + encodeURIComponent(select.value)); if (current === revision) render(body, result.data); }
      catch (e) {
        if (current !== revision) return;
        const message = node('div', 'notice neutral'); message.append(node('p', null, 'No se pudo cargar tu progreso. No se muestran cifras incompletas.'));
        const retry = node('button', 'button secondary', 'Reintentar'); retry.type = 'button'; retry.onclick = load; message.append(retry); body.replaceChildren(message);
      } finally { if (current === revision) body.setAttribute('aria-busy', 'false'); }
    };
    select.onchange = load; load(); return section;
  }
  window.SGRProgress = { mount };
})();
