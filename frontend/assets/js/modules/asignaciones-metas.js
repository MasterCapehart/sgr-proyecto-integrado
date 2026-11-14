/* Objetivos y ponderaciones por funcionario y trimestre. */
(() => {
 const api=window.SGRApi,el=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
 let state,page=1,filter='';
 const button=(text,fn)=>{const b=el('button',text);b.className='button secondary';b.type='button';b.onclick=fn;return b;};
 function field(form,label,name,type,value=''){const wrap=el('label',label),n=el(type==='select'?'select':type==='textarea'?'textarea':'input');wrap.className='field';n.name=name;if(n.tagName==='INPUT')n.type=type;n.value=value;wrap.append(n);form.append(wrap);return n;}
 function editor(a){
  const d=el('dialog'),f=el('form'),h=el('h2',a?'Editar asignación':'Asignar meta individual');d.className='community-dialog';f.className='body grid';h.className='modalhead';d.append(h,f);const controls={};
  for(const [k,label,options] of [['funcionario','Funcionario',state.opciones.funcionarios],['item','Meta',state.opciones.items],['periodo','Trimestre',state.opciones.periodos]]){
   const n=field(f,label,k,'select');n.required=true;n.add(new Option('Selecciona…',''));
   const all=[...options];if(a&&!all.some(x=>x.id===a[k]))all.push({id:a[k],nombre:a[k+'_nombre']+' (histórico)'});
   for(const v of all)n.add(new Option(v.nombre+(v.cerrado?' · cerrado':''),v.id));n.value=a?.[k]??'';n.disabled=!!a;controls[k]=n;
  }
  for(const [k,label] of [['cantidad_objetivo','Cantidad objetivo'],['ponderacion','Ponderación (%)']]){const n=field(f,label,k,'number',a?.[k]??'');n.required=true;n.min=k==='cantidad_objetivo'?'0.01':'0';n.max=k==='ponderacion'?'100':'9999999999.99';n.step='0.01';controls[k]=n;}
  controls.observacion=field(f,'Observación','observacion','textarea',a?.observacion??'');controls.observacion.maxLength=2000;
  const active=field(f,'Estado','estado','select');active.add(new Option('Activa','true'));active.add(new Option('Inactiva','false'));active.value=String(a?.estado??true);controls.estado=active;
  f.append(el('p','Las ponderaciones activas por funcionario y trimestre pueden sumar hasta 100 %. La cantidad objetivo corresponde a esta asignación individual.'));
  const msg=el('p');msg.setAttribute('role','status');f.append(msg);const save=el('button','Guardar');save.className='button';save.type='submit';f.append(save,button('Cancelar',()=>d.close()));
  f.onsubmit=async e=>{e.preventDefault();if(save.disabled||!f.reportValidity())return;save.disabled=true;try{const data=Object.fromEntries(Object.entries(controls).map(([k,n])=>[k,['funcionario','item','periodo'].includes(k)?Number(n.value):k==='estado'?n.value==='true':n.value]));if(a)data._version=a.version;await api.send('/api/asignaciones-metas/'+(a?a.id+'/':''),data,a?'PATCH':'POST');d.close();await load();}catch(e){msg.textContent=e.message;}finally{save.disabled=false;}};
  d.onclose=()=>d.remove();document.body.append(d);d.showModal();
 }
 async function load(){const main=document.querySelector('#main-content');try{
  state=await api.request('/api/asignaciones-metas/?'+new URLSearchParams({page,periodo:filter}));main.replaceChildren(el('p','SGR / Planificación'),el('h1','Asignaciones individuales de metas'),el('p','Define cantidades y ponderaciones para cada funcionario y trimestre. Los trimestres cerrados conservan su historial.'));
  const toolbar=el('div');toolbar.className='toolbar';main.append(toolbar);if(state.puede_crear)toolbar.append(button('+ Asignar meta',()=>editor()));const select=field(toolbar,'Filtrar trimestre','filtro','select');select.add(new Option('Todos',''));for(const p of state.opciones.periodos)select.add(new Option(p.nombre,p.id));select.value=filter;select.onchange=()=>{filter=select.value;page=1;load();};
  const table=el('table'),head=el('tr');for(const s of ['Funcionario','Meta','Trimestre','Objetivo','Ponderación','Estado','Acciones'])head.append(el('th',s));const thead=el('thead');thead.append(head);table.append(thead);const body=el('tbody');
  for(const a of state.results){const row=el('tr');for(const v of [a.funcionario_nombre,a.item_nombre,a.periodo_nombre,a.cantidad_objetivo,a.ponderacion+' %',a.cerrado?'Trimestre cerrado':a.estado?'Activa':'Inactiva'])row.append(el('td',v));const cell=el('td');if(state.puede_editar&&!a.cerrado)cell.append(button('Editar / desactivar',()=>editor(a)));row.append(cell);body.append(row);}table.append(body);const wrap=el('div');wrap.className='tablewrap';wrap.append(table);main.append(wrap);if(!state.results.length)main.append(el('p','No hay asignaciones para este filtro.'));
  const status=el('p',`${state.count} asignaciones · Página ${state.page} de ${state.total_pages}`);status.setAttribute('role','status');main.append(status);const prev=button('Anterior',()=>{page--;load();}),next=button('Siguiente',()=>{page++;load();});prev.disabled=page<=1;next.disabled=page>=state.total_pages;main.append(prev,next);
 }catch(e){main.replaceChildren(el('p',e.message));}}
 document.addEventListener('DOMContentLoaded',async()=>{try{await window.SGRSession;await load();}catch(e){document.querySelector('#main-content').textContent=e.message;}});
})();
