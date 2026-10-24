document.addEventListener('DOMContentLoaded', async () => {
 const panel=document.getElementById('weight-review');if(!panel)return;
 const select=document.getElementById('weight-period'),button=document.getElementById('weight-refresh'),status=document.getElementById('weight-status'),body=document.getElementById('weight-results');let sequence=0;
 const el=(tag,text)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;return node;};
 const percent=value=>new Intl.NumberFormat('es-CL',{maximumFractionDigits:2}).format(Number(value))+' %';
 async function review(){
  const current=++sequence,period=select.value;body.replaceChildren();button.disabled=false;panel.removeAttribute('aria-busy');if(!period){status.textContent='Selecciona un período para revisar sus ponderaciones.';return;}
  status.textContent='Revisando ponderaciones…';button.disabled=true;panel.setAttribute('aria-busy','true');
  try{
   const response=await SGRApi.request('/api/configuraciones-metas/revision-ponderaciones/?'+new URLSearchParams({periodo:period}));if(current!==sequence)return;const data=response.data;
   status.textContent=data.periodo_nombre+' · '+data.fuente;
   const note=el('p',data.advertencia);note.className='notice neutral';body.append(note,el('p',data.criterio));
   if(!data.pautas.length){body.append(el('p','Este período no conserva pautas que puedan revisarse.'));return;}
   const wrap=el('div');wrap.className='tablewrap';wrap.tabIndex=0;wrap.setAttribute('role','region');wrap.setAttribute('aria-label','Revisión de ponderaciones por cargo. Desplazamiento horizontal disponible.');
   const table=el('table'),caption=el('caption','Resultado aritmético por cargo'),head=el('thead'),headRow=el('tr');
   for(const title of ['Cargo','Metas','Suma','Falta','Exceso','Resultado']){const cell=el('th',title);cell.scope='col';headRow.append(cell);}head.append(headRow);const tbody=el('tbody');
   for(const row of data.pautas){const tr=el('tr');for(const value of [row.cargo_nombre,row.metas,percent(row.suma),percent(row.faltante),percent(row.exceso),row.estado])tr.append(el('td',value));tbody.append(tr);}
   table.append(caption,head,tbody);wrap.append(table);body.append(wrap);
  }catch(error){if(current===sequence)status.textContent='No se pudo revisar la pauta: '+error.message;}
  finally{if(current===sequence){button.disabled=false;panel.removeAttribute('aria-busy');}}
 }
 select.addEventListener('change',review);button.addEventListener('click',review);
 document.addEventListener('sgr:metas-actualizadas',()=>{if(select.value)review();});
 try{const response=await SGRApi.request('/api/opciones/');for(const period of response.data.periodos){const option=new Option(period.codigo+' · '+period.nombre+(period.cerrado?' · Cerrado':''),period.id);select.add(option);}status.textContent='Selecciona un período para revisar sus ponderaciones.';}
 catch(error){status.textContent='No se pudieron cargar los períodos: '+error.message;button.disabled=true;}
});
