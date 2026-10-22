/* Reclamos conservados; felicitaciones con respaldo y revisión explícita del delegado. */
(() => {
 const n=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e;};
 const button=(text,fn,cls='button secondary')=>{const b=n('button',cls,text);b.type='button';b.onclick=fn;return b;};
 let ctx,options,page=1,total=1,search='',clase='';
 const can=a=>ctx.permisos.includes('reclamos.'+a),manager=()=>options.puede_gestionar_felicitaciones;
 const editable=item=>can('editar')&&(item.clase!=='Felicitación'||manager())&&(item.autor===ctx.usuario.id||can('editar_equipo'));
 const query=()=>new URLSearchParams({page,search,clase});
 function fileLink(file){const a=n('a','linkbtn',file.nombre);a.href=file.archivo_url;return a;}
 async function load(){
  const rows=document.getElementById('feedback-rows');
  try{const r=await SGRApi.request('/api/reclamos/?'+query());total=r.total_pages;rows.replaceChildren();
   for(const item of r.results){const tr=n('tr');for(const key of ['fecha','clase','vecino','contacto','ubicacion','situacion','profesional_nombre','informado_a'])tr.append(n('td',null,item[key]||'—'));
    const state=n('td');state.append(n('span','badge '+(item.revision.estado==='Validada'?'green':item.revision.estado==='Rechazada'?'red':'amber'),item.revision.estado));tr.append(state);
    const td=n('td','local-actions');td.append(button(item.clase==='Felicitación'?'Ver / revisar':'Consultar',()=>editor(item,false),'linkbtn'));
    if(editable(item))td.append(button('Editar',()=>editor(item,true),'linkbtn'));tr.append(td);rows.append(tr);
   }
   if(!r.results.length){const tr=n('tr'),td=n('td','empty','No hay registros para este filtro.');td.colSpan=10;tr.append(td);rows.append(tr);}
   document.getElementById('feedback-count').textContent=r.count+' resultados · Página '+page+' de '+total;
   document.getElementById('feedback-prev').disabled=page<=1;document.getElementById('feedback-next').disabled=page>=total;
  }catch(e){rows.textContent=e.message;}
 }
 function formalDetails(d,item){
  const section=n('section','felicitacion-review');section.append(n('h3',null,'Revisión formal de la felicitación'),n('p','badge '+(item.revision.estado==='Validada'?'green':item.revision.estado==='Rechazada'?'red':'amber'),item.revision.estado),n('p','help',item.revision.alcance));
  if(item.revision.potencialmente_puntuable)section.append(n('p',null,'Cumple las condiciones formales. Esta validación no concede puntos.'));
  const reasons=n('ul');for(const text of item.revision.motivos)reasons.append(n('li',null,text));section.append(reasons,n('h4',null,'Respaldos formales'));
  for(const [index,file] of item.respaldos.entries()){const row=n('p');row.append(fileLink(file),document.createTextNode(' · '+(index===0?'Vigente':'Anterior')+' · '+Math.ceil(file.tamano/1024)+' KB'));section.append(row);}
  if(!item.respaldos.length)section.append(n('p','help','Sin respaldo formal adjunto. Un indicador de “medio escrito” o una evidencia anterior no sustituye esta carga.'));
  const refresh=async data=>{d.close();await load();await editor(data,false);};
  if(editable(item)){
   const upload=n('form','felicitacion-upload'),label=n('label',null,'Adjuntar respaldo formal (PDF, PNG o JPEG, hasta 10 MB)'),file=n('input');file.type='file';file.id='fel-file';file.accept='.pdf,.png,.jpg,.jpeg';file.required=true;label.htmlFor=file.id;
   upload.append(label,file,n('p','help','Adjuntar un nuevo archivo conserva los anteriores y exige una nueva revisión.'));
   const save=n('button','button secondary','Adjuntar respaldo');save.type='submit';upload.append(save);
   upload.onsubmit=async e=>{e.preventDefault();if(save.disabled||!upload.reportValidity())return;save.disabled=true;try{const f=file.files[0];if(f.size>10*1024*1024||f.size===0)throw new Error('Adjunta un archivo de hasta 10 MB.');const data=new FormData();data.append('_version',item.version);data.append('archivo',f);const r=await SGRApi.request('/api/reclamos/'+item.id+'/respaldos/',{method:'POST',body:data});await refresh(r.data);}catch(e){await SGRApi.message(e.message);}finally{save.disabled=false;}};section.append(upload);
   const review=n('form','felicitacion-decision'),lab=n('label',null,'Observación de la revisión *'),note=n('textarea');note.id='fel-note';lab.htmlFor=note.id;note.required=true;note.maxLength=2000;review.append(lab,note,n('p','help','Al validar confirmas la procedencia directa, el destinatario y que comprobaste el respaldo formal. Guardar el registro no realiza esta validación.'));
   const actions=n('div','primary-actions'),validate=n('button','button primary','Validar felicitación'),reject=n('button','button secondary','Rechazar con motivo');validate.type=reject.type='submit';validate.value='Validada';reject.value='Rechazada';actions.append(validate,reject);review.append(actions);
   review.onsubmit=async e=>{e.preventDefault();if(validate.disabled||!review.reportValidity())return;const decision=e.submitter?.value;if(!decision)return;validate.disabled=reject.disabled=true;try{const r=await SGRApi.send('/api/reclamos/'+item.id+'/revision/',{_version:item.version,decision,observacion:note.value.trim()});await refresh(r.data);}catch(e){await SGRApi.message(e.message);}finally{validate.disabled=reject.disabled=false;}};section.append(review);
  }
  const history=n('details'),summary=n('summary',null,'Historial de revisiones ('+item.revisiones.length+')');history.append(summary);
  for(const r of item.revisiones){const row=n('div','review-history');row.append(n('strong',null,r.decision+' · '+r.autor_nombre),n('p',null,new Date(r.creado).toLocaleString('es-CL')+' · Versión '+r.version_registro),n('p','readonly-details',r.observacion));history.append(row);}
  section.append(history);d.append(section);
 }
 async function editor(item=null,edit=true,kind='Reclamo'){
  try{if(item)item=(await SGRApi.request('/api/reclamos/'+item.id+'/')).data;
   const isFel=(item?.clase||kind)==='Felicitación',d=n('dialog'),head=n('div','modalhead'),title=n('h2',null,item?(edit?'Editar registro':'Consultar registro'):isFel?'Nueva felicitación':'Nuevo reclamo');
   d.setAttribute('aria-label',title.textContent);head.append(title,button('Cerrar',()=>d.close()));d.append(head);
   const form=n('form','feedback-form'),grid=n('div','grid');let evidence=[];
   if(!isFel&&ctx.permisos.includes('evidencias.ver'))evidence=await SGRApi.all('operacion/evidencias');
   const defs=[['clase','Clase','class'],['fecha',isFel?'Fecha de recepción':'Fecha','date'],['vecino',isFel?'Vecino / usuario emisor':'Usuario / vecino'],['contacto','Contacto'],['ubicacion','Ubicación'],['situacion',isFel?'Descripción de la felicitación':'Situación que reclama','textarea'],['profesional',isFel?'Funcionario reconocido (opcional)':'Profesional involucrado','staff']];
   if(isFel)defs.push(['procedencia','Procedencia','source'],['destinatario','Dirigida a','target']);else defs.push(['medio_escrito','Medio escrito','boolean'],['informado_a','Reclamo informado a'],['evidencia','Archivo verificador asociado','evidence']);
   const required=['clase','fecha','vecino','situacion'];
   for(const [key,label,type] of defs){const wrap=n('div','field'+(type==='textarea'?' full':'')),lab=n('label',null,label+(required.includes(key)?' *':''));lab.htmlFor='fb-'+key;let input;
    if(['class','staff','evidence','boolean','source','target'].includes(type)){input=n('select');let choices=[];
     if(type==='class')choices=[[item?.clase||kind,item?.clase||kind]];
     if(type==='boolean')choices=[['no','No'],['si','Sí']];
     if(type==='source')choices=[['Sin determinar','Sin determinar'],['Directa','Directamente del vecino / usuario'],['Personal','Mensaje personal al funcionario, sin formalizar'],['Otra','Otra procedencia']];
     if(type==='target')choices=['Sin determinar','Delegación','Delegado','Funcionario','Otro'].map(v=>[v,v]);
     if(type==='staff'||type==='evidence'){const values=type==='staff'?options.responsables:evidence;choices=[['','Sin asignar'],...values.map(v=>[v.id,type==='staff'?v.nombre:v.nombre_archivo])];if(item&&item[key]&&!values.some(v=>v.id===item[key]))choices.push([item[key],type==='staff'?item.profesional_nombre:'Evidencia '+item.evidencia]);}
     for(const [value,text] of choices)input.add(new Option(text,value));
    }else if(type==='textarea')input=n('textarea');else{input=n('input');input.type=type||'text';}
    input.id='fb-'+key;input.name=key;input.required=required.includes(key);input.disabled=!edit||key==='clase';
    if(input.tagName==='INPUT'||input.tagName==='TEXTAREA')input.maxLength=key==='situacion'?5000:key==='contacto'?100:key==='ubicacion'?250:200;
    input.value=item?(key==='medio_escrito'?(item[key]?'si':'no'):item[key]??''):(key==='fecha'?options.fecha_municipal:key==='clase'?kind:key==='medio_escrito'?'no':['procedencia','destinatario'].includes(key)?'Sin determinar':'');wrap.append(lab,input);grid.append(wrap);
   }
   if(isFel)grid.append(n('p','help field full','Solo el delegado registra y valida. Primero guarda; luego adjunta el respaldo y revisa. Cada corrección exige nueva revisión. No se asignan puntos automáticamente.'));
   form.append(grid);const foot=n('div','modalfoot');foot.append(button(edit?'Cancelar':'Cerrar',()=>d.close()));
   if(edit){const save=n('button','button primary',isFel?'Guardar sin validar':'Guardar registro');save.type='submit';foot.append(save);
    form.onsubmit=async e=>{e.preventDefault();if(save.disabled||!form.reportValidity())return;save.disabled=true;try{const data=Object.fromEntries(new FormData(form));data.clase=item?.clase||kind;data.profesional=data.profesional?Number(data.profesional):null;if(!isFel){data.medio_escrito=data.medio_escrito==='si';data.evidencia=data.evidencia?Number(data.evidencia):null;}if(item)data._version=item.version;const r=await SGRApi.send('/api/reclamos/'+(item?item.id+'/':''),data,item?'PATCH':'POST');SGRDrafts.clean(form);d.close();await load();if(isFel)await editor(r.data,false);else await SGRApi.message('Registro guardado con su historial.','success');}catch(e){await SGRApi.message(e.message);}finally{save.disabled=false;}};
   }
   if(item&&isFel&&!edit){const intro=n('div','felicitacion-intro');intro.append(n('strong',null,item.vecino),n('p','readonly-details',item.situacion));d.append(intro);const basic=n('details','felicitacion-datos');basic.append(n('summary',null,'Ver datos de la felicitación'),grid);d.append(basic);formalDetails(d,item);d.append(foot);}else{form.append(foot);d.append(form);}document.body.append(d);d.addEventListener('close',()=>d.remove());d.showModal();d.querySelector('button').focus();
  }catch(e){await SGRApi.message(e.message);}
 }
 document.addEventListener('DOMContentLoaded',async()=>{
  const main=document.getElementById('main-content');try{ctx=await SGRSession;if(!can('ver')){main.textContent='No tienes permiso para consultar estos registros.';return;}options=await SGRApi.request('/api/reclamos/opciones/');
   main.replaceChildren(n('div','crumb','SGR / Gestión diaria / Reclamos y felicitaciones'));const head=n('div','head'),copy=n('div');copy.append(n('h1',null,'Reclamos y felicitaciones'),n('p','sub','Registros de la delegación activa. Las felicitaciones requieren respaldo formal y revisión explícita del delegado.'));head.append(copy);
   if(can('crear')){const actions=n('div','primary-actions');actions.append(button('+ Nuevo reclamo',()=>editor(null,true,'Reclamo')));if(manager())actions.append(button('+ Nueva felicitación',()=>editor(null,true,'Felicitación'),'button primary'));head.append(actions);}main.append(head);
   const card=n('section','card'),toolbar=n('div','toolbar'),searchLabel=n('label');searchLabel.append(n('span',null,'Buscar'));const input=n('input');input.type='search';input.placeholder='Vecino, situación, ubicación o folio';searchLabel.append(input);let timer;input.oninput=()=>{clearTimeout(timer);timer=setTimeout(()=>{search=input.value;page=1;load();},250);};toolbar.append(searchLabel);
   const classLabel=n('label');classLabel.append(n('span',null,'Clase'));const select=n('select');for(const [v,t] of [['','Reclamos y felicitaciones'],['Reclamo','Reclamo'],['Felicitación','Felicitación']])select.add(new Option(t,v));select.onchange=()=>{clase=select.value;page=1;load();};classLabel.append(select);toolbar.append(classLabel);
   if(can('exportar'))toolbar.append(button('Exportar a Excel',()=>location.assign('/api/reclamos/export/?'+query())));card.append(toolbar);
   const wrap=n('div','tablewrap'),table=n('table','feedback-table');wrap.tabIndex=0;wrap.setAttribute('aria-label','Listado desplazable de reclamos y felicitaciones');table.setAttribute('aria-label','Planilla de reclamos y felicitaciones');const thead=n('thead'),tr=n('tr');
   for(const h of ['Fecha','Clase','Usuario / vecino','Contacto','Ubicación','Situación','Profesional involucrado','Informado a','Revisión','Acciones'])tr.append(n('th',null,h));thead.append(tr);const tbody=n('tbody');tbody.id='feedback-rows';table.append(thead,tbody);wrap.append(table);card.append(wrap);
   const pager=n('div','pager'),count=n('span');count.id='feedback-count';count.setAttribute('aria-live','polite');pager.append(count);
   for(const [id,text,step] of [['feedback-prev','Anterior',-1],['feedback-next','Siguiente',1]]){const b=button(text,()=>{page+=step;load();});b.id=id;pager.append(b);}card.append(pager);main.append(card);await load();
  }catch(e){main.textContent=e.message;}
 });
})();
