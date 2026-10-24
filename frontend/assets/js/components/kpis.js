(() => {
  const node = (tag, cls, text) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text !== undefined) el.textContent = text;
    return el;
  };

  const KPI_ICONS = {
    atenciones: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
    actividades: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>`,
    compromisos_abiertos: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
    compromisos_vencidos: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`
  };

  function mount(before) {
    const section = node('section', 'operational-kpis');
    section.setAttribute('aria-label', 'Indicadores operativos');
    section.setAttribute('aria-busy', 'true');
    section.append(node('p', 'kpi-scope', 'Cargando indicadores…'));
    before.before(section);
    return section;
  }

  function update(section, data) {
    if (!section) return;
    section.replaceChildren();
    section.setAttribute('aria-busy', 'false');
    if (!data?.cards?.length) {
      section.hidden = true;
      return;
    }
    section.hidden = false;
    section.classList.toggle('has-tube-completion',Boolean(data.completion));

    const heading = node('div', 'kpi-heading');
    heading.append(node('h2', null, data.completion?'Avance del tubo':'Resumen operativo'), node('span', 'kpi-context', 'Datos reales · Delegación activa'));
    if(!data.completion)section.append(heading);

    if (data.completion) {
      const completion=data.completion;
      const panel=node('article','tube-completion');
      panel.setAttribute('aria-label','Avance de los compromisos');
      const header=node('div','tube-completion-header'),copy=node('div','tube-completion-copy');
      copy.append(node('h2',null,'Avance del tubo'));
      const hasResults=completion.porcentaje!==null;
      const text=hasResults?Number(completion.porcentaje).toLocaleString('es-CL',{maximumFractionDigits:2})+' %':'Sin compromisos';
      copy.append(node('p','tube-completion-detail',hasResults?completion.total+' compromisos en total':'No hay compromisos con los filtros actuales.'));
      const value=node('p','tube-completion-value',text);value.dataset.tubeProgress='';
      if(!hasResults)value.classList.add('is-empty');header.append(copy,value);panel.append(header);
      const breakdown=node('p','tube-completion-breakdown');
      const overdue=data.cards.find(metric=>metric.key==='vencidos')?.value??0;
      for(const [amount,label] of [[completion.realizados,'realizados'],[completion.por_completar,'por completar'],[overdue,'vencidos']]){const item=node('span');item.append(node('strong',null,Number(amount).toLocaleString('es-CL')),document.createTextNode(' '+label));breakdown.append(item);}
      if(hasResults)panel.append(breakdown);
      if(hasResults){
        const progress=node('progress','tube-completion-track');progress.max=100;progress.value=Number(completion.porcentaje_exacto);
        progress.setAttribute('aria-label','Porcentaje de compromisos completados');progress.setAttribute('aria-valuetext',text+' · '+completion.realizados+' de '+completion.total+' realizados');panel.append(progress);
      }
      panel.append(node('p','tube-completion-note','Según los filtros actuales · Avance operativo, sin puntaje.'));
      section.append(panel);
    }

    const grid = node('div', 'kpi-grid');
    for (const metric of data.cards) {
      const article = node('article', 'kpi-card kpi-' + (metric.tone || 'neutral'));
      
      const headWrapper = node('div', 'kpi-card-head');
      const label = node('h3', 'kpi-label', metric.label);
      const iconWrap = node('div', 'kpi-icon-wrap');
      iconWrap.innerHTML = KPI_ICONS[metric.key] || `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle></svg>`;
      headWrapper.append(label, iconWrap);

      const value = node('p', 'kpi-value', Number(metric.value).toLocaleString('es-CL'));
      value.dataset.kpi = metric.key;

      article.append(headWrapper, value);
      if (metric.help) article.append(node('p', 'kpi-help', metric.help));
      grid.append(article);
    }
    if(!data.completion)section.append(grid);

    const caption = node('p', 'kpi-scope', data.scope || '');
    if (data.generated_at) {
      const time = node('time', null, 'Actualizado ' + new Date(data.generated_at).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' }));
      time.dateTime = data.generated_at;
      caption.append(document.createTextNode(' · '), time);
    }
    section.append(caption);
  }

  function error(section) {
    if (!section) return;
    section.hidden = false;
    section.setAttribute('aria-busy', 'false');
    section.replaceChildren(node('p', 'notice neutral', 'Indicadores no disponibles. Vuelve a cargar los datos para actualizarlos.'));
  }

  window.SGRKpis = { mount, update, error };
})();
