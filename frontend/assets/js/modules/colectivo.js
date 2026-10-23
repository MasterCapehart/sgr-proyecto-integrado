/* Tablero de lectura: no altera actividades, metas ni calendarios. */
(() => {
 const el=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;};
 const fmt=new Intl.NumberFormat('es-CL',{maximumFractionDigits:2});
 const num=v=>v==null?'Sin evaluación':fmt.format(Number(v));
 const pct=v=>v==null?'Sin evaluación':num(v)+' %';
 let sequence=0;
 function table(parent,title,headers,rows){const section=el('section','card');section.append(el('h2','collective-title',title));const wrap=el('div','tablewrap'),t=el('table','collective-table'),head=el('thead'),tr=el('tr');headers.forEach(h=>{const th=el('th',null,h);th.scope='col';tr.append(th);});head.append(tr);const body=el('tbody');rows.forEach(values=>{const row=el('tr');values.forEach(v=>{const td=el('td');td.append(typeof v==='string'?document.createTextNode(v):v);row.append(td);});body.append(row);});if(!rows.length){const row=el('tr'),td=el('td','empty','No hay resultados para este contexto.');td.colSpan=headers.length;row.append(td);body.append(row);}t.append(head,body);wrap.append(t);section.append(wrap);parent.append(section);}
 function badge(color){return el('span','badge '+({Verde:'green',Naranjo:'amber',Rojo:'red'}[color]||''),color);}
 function render(r,target,periodId){
  target.replaceChildren();target.append(el('p','notice neutral',r.delegacion+' · '+r.periodo+' · '+r.fuente));
  const stats=el('div','absence-metrics');for(const [label,value] of [['Índice colectivo de actividades',pct(r.cumplimiento)],['Personas evaluadas',r.evaluados+' de '+r.personas.length],['Sin evaluación',String(r.sin_evaluacion)],['Requieren atención',String(r.distribucion.Rojo+r.distribucion.Naranjo)]]){const card=el('section','absence-metric');card.append(el('h2',null,label),el('strong',null,value));stats.append(card);}target.append(stats);
  if(r.parcial)target.append(el('p','notice neutral','Cobertura parcial: hay personas o ítems sin evaluación. No se cuentan como cero ni se incluyen en el índice. Revisa calendarios y metas antes de interpretar el resultado.'));
  if(!r.pesos_compatibles)target.append(el('p','notice neutral','Los pesos de algunos ítems no son compatibles entre personas; el índice global no se calcula. Consulta los resultados por ítem.'));
  const chart=el('section','card collective-chart');chart.append(el('h2',null,'Distribución del equipo'),el('p','help','Semáforo según el objetivo al día de cada persona. La falta de evaluación se muestra por separado.'));
  for(const [label,count] of Object.entries(r.distribucion)){const line=el('div','collective-bar');line.append(el('span',null,label));const progress=el('div','collective-track');progress.setAttribute('role','progressbar');progress.setAttribute('aria-valuemin','0');progress.setAttribute('aria-valuemax',String(Math.max(r.personas.length,1)));progress.setAttribute('aria-valuenow',String(count));progress.setAttribute('aria-label',label+': '+count+' personas');const fill=el('span',{'Verde':'green','Naranjo':'amber','Rojo':'red'}[label]||'neutral');fill.style.width=(count/Math.max(r.personas.length,1)*100)+'%';progress.append(fill);line.append(progress,el('strong',null,String(count)));chart.append(line);}target.append(chart);
  table(target,'Cumplimiento por ítem',['Ítem','Meta conjunta','Aporte reconocido','Exceso conservado','Cumplimiento','Semáforo','Cobertura'],r.items.map(i=>[i.codigo+' · '+i.nombre,num(i.meta),num(i.reconocido),num(i.exceso),pct(i.cumplimiento),badge(i.semaforo),i.evaluados+' evaluados · '+i.sin_evaluacion+' sin evaluación']));
  table(target,'Resultado individual del equipo',['Funcionario','Área actual','Índice individual','Semáforo','Ítems evaluados / sin evaluación','Consulta'],r.personas.map(p=>{const link=r.cerrado?el('span',null,'Resultado conservado al cierre'):el('a',null,'Ver detalle');if(!r.cerrado)link.href='semaforo.html?'+new URLSearchParams({funcionario:p.id,periodo:periodId});return [p.nombre,r.cerrado?'No conservada al cierre':p.area||'Sin área asignada',pct(p.cumplimiento),badge(p.semaforo),p.items_evaluados+' / '+p.items_sin_evaluacion,link];}));
  table(target,'Distribución de actividades por territorio',['Territorio registrado','Actividades registradas'],r.territorios.map(t=>[t.nombre,String(t.registradas)]));target.append(el('p','help',r.territorios_nota));
  const details=el('details','card collective-rule');details.append(el('summary',null,'Cómo se calcula y qué incluye'),el('p',null,r.regla),el('p',null,'Cada actividad conserva su trazabilidad. El aporte se limita primero al 120 % individual; no se usa el excedente para compensar a otra persona. El índice normaliza los pesos de los ítems evaluables; no incluye felicitaciones ni otros componentes. Verde: alcanza el objetivo al día; naranjo: al menos el 60 % de ese objetivo; rojo: por debajo. No se presenta un promedio simple de porcentajes de funcionarios.'));target.append(details);
 }
 document.addEventListener('DOMContentLoaded',async()=>{
  const main=document.getElementById('main-content');
  try{
   await SGRSession;const options=await SGRApi.request('/api/ausencias/opciones/');
   main.replaceChildren(el('div','crumb','SGR / Seguimiento / Indicadores colectivos'),el('h1',null,'Indicadores colectivos'),el('p','sub','Cumplimiento del equipo en la delegación activa. Metas ajustadas, aportes validados y cobertura visible.'));
   const filters=el('div','card absence-filters');function select(label,id){const field=el('div','field'),l=el('label',null,label),n=el('select');l.htmlFor=id;n.id=id;field.append(l,n);filters.append(field);return n;}
   const period=select('Período de gestión','collective-period'),area=select('Equipo / área de trabajo','collective-area');
   for(const p of options.periodos)period.add(new Option(p.nombre+(p.cerrado?' · cerrado':''),p.id));const query=new URLSearchParams(location.search),chosen=options.periodos.find(p=>String(p.id)===query.get('periodo'))||options.periodos.find(p=>p.estado&&!p.cerrado)||options.periodos[0];period.value=chosen?.id||'';area.add(new Option('Todas las áreas',''));
   const target=el('div');target.id='collective-result';target.setAttribute('aria-live','polite');main.append(filters,target);
   async function load(){const stamp=++sequence;target.textContent='Calculando resultados del equipo…';if(!period.value){target.textContent='No hay períodos disponibles.';return;}
    try{const response=await SGRApi.request('/api/cumplimiento/colectivo/?'+new URLSearchParams({periodo:period.value,area:area.value}));if(stamp!==sequence)return;const r=response.data,old=area.value;area.replaceChildren(new Option('Todas las áreas',''));r.areas.forEach(a=>area.add(new Option(a,a)));area.value=old;area.disabled=r.cerrado;render(r,target,period.value);}catch(e){if(stamp===sequence)target.textContent=e.message;}}
   period.onchange=()=>{area.value='';load();};area.onchange=load;await load();
  }catch(e){main.textContent=e.message;}
 });
})();
