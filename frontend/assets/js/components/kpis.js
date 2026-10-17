/* Indicadores de conteo recibidos del servidor: sin datos de ejemplo ni cálculos de metas. */
(() => {
 const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
 function mount(before){const section=node('section','operational-kpis');section.setAttribute('aria-label','Indicadores operativos');section.setAttribute('aria-busy','true');section.append(node('p','kpi-scope','Cargando indicadores…'));before.before(section);return section;}
 function update(section,data){if(!section)return;section.replaceChildren();section.setAttribute('aria-busy','false');if(!data?.cards?.length){section.hidden=true;return;}section.hidden=false;
  const heading=node('div','kpi-heading');heading.append(node('h2',null,'Resumen operativo'),node('span','kpi-context','Datos reales · Delegación activa'));section.append(heading);
  const grid=node('div','kpi-grid');for(const metric of data.cards){const article=node('article','kpi-card kpi-'+(metric.tone||'neutral'));const label=node('h3','kpi-label',metric.label);const value=node('p','kpi-value',Number(metric.value).toLocaleString('es-CL'));value.dataset.kpi=metric.key;article.append(label,value);if(metric.help)article.append(node('p','kpi-help',metric.help));grid.append(article);}section.append(grid);
  const caption=node('p','kpi-scope',data.scope||'');if(data.generated_at){const time=node('time',null,'Actualizado '+new Date(data.generated_at).toLocaleTimeString('es-CL',{hour:'2-digit',minute:'2-digit'}));time.dateTime=data.generated_at;caption.append(document.createTextNode(' · '),time);}section.append(caption);
 }
 function error(section){if(!section)return;section.hidden=false;section.setAttribute('aria-busy','false');section.replaceChildren(node('p','notice neutral','Indicadores no disponibles. Vuelve a cargar los datos para actualizarlos.'));}
 window.SGRKpis={mount,update,error};
})();
