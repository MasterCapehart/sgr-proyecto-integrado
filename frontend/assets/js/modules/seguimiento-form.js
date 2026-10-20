/* Captura de seguimiento compartida. Los datos del origen se reutilizan al guardar. */
window.SGRFollowup={async attach({context,existingSelect,description,sector,sourceDate,attention=false}){
 const make=(tag,text)=>{const e=document.createElement(tag);if(text)e.textContent=text;return e;};
 const uid='follow-'+crypto.randomUUID(),form=existingSelect.form,existingWrap=existingSelect.closest('.field');
 const root=make('section');root.className='field full sgr-followup';root.setAttribute('aria-label','Seguimiento en el tubo');
 const label=make('label','¿Requiere seguimiento en el tubo?');const mode=make('select');mode.id=uid;label.htmlFor=mode.id;
 mode.add(new Option('No requiere seguimiento','no'));
 if(context.permisos.includes('compromisos.crear'))mode.add(new Option('Sí, crear compromiso','nuevo'));
 if(context.permisos.includes('compromisos.ver'))mode.add(new Option('Vincular compromiso existente','existente'));
 existingWrap.before(root);root.append(label,mode,existingWrap);const details=make('div');details.className='grid';root.append(details);
 const controls={};
 function field(key,title,type='text'){
  const box=make('div');box.className='field';const l=make('label',title+' *'),input=make(type==='textarea'?'textarea':type==='select'?'select':'input');
  if(input.tagName==='INPUT')input.type=type;input.id=uid+'-'+key;l.htmlFor=input.id;input.required=true;box.append(l,input);details.append(box);controls[key]=input;return input;
 }
 const owner=field('responsable','Responsable del compromiso','select');owner.add(new Option('Selecciona responsable…',''));
 if(context.permisos.includes('compromisos.crear')){
  const options=await SGRApi.request('/api/seguimiento/opciones/');for(const u of options.responsables)owner.add(new Option(u.nombre,u.id));owner.value=String(context.usuario.id);
 }
 const due=field('fecha_comprometida','Plazo del compromiso','date');
 const text=field('descripcion','Descripción del compromiso','textarea');text.maxLength=5000;text.value=description.value;
 let changed=false;text.addEventListener('input',()=>{changed=true;});description.addEventListener('input',()=>{if(!changed)text.value=description.value;});
 if(!sector){const s=field('sector','Sector del compromiso');s.maxLength=150;}
 const area=field('area_apoyo','Área de apoyo');area.maxLength=150;area.value=context.usuario.area||'';
 const origin=field('origen','Origen del compromiso','select');origin.add(new Option('Interno','Interno'));origin.add(new Option('Externo','Externo'));origin.value=attention?'Externo':'Interno';
 const note=make('p','El solicitante y la fecha se toman del registro de origen. El compromiso se guardará junto con la atención o actividad.');note.className='help';root.append(note);
 function update(){const creating=mode.value==='nuevo';details.style.display=creating?'grid':'none';for(const input of Object.values(controls))input.disabled=!creating;existingWrap.style.display=mode.value==='existente'?'':'none';existingSelect.disabled=mode.value!=='existente';existingSelect.required=mode.value==='existente';due.min=sourceDate?.value||new Date().toLocaleDateString('en-CA');note.hidden=!creating;}
 mode.onchange=update;sourceDate?.addEventListener('change',update);
 form.addEventListener('reset',()=>queueMicrotask(()=>{changed=false;mode.value='no';owner.value=String(context.usuario.id);area.value=context.usuario.area||'';origin.value=attention?'Externo':'Interno';text.value=description.value;update();}));update();
 return {root,apply(data){if(mode.value==='nuevo'){data.compromiso=null;data.nuevo_compromiso=Object.fromEntries(Object.entries(controls).map(([k,v])=>[k,v.value.trim()]));if(sector)data.nuevo_compromiso.sector=sector.value.trim();}else data.compromiso=mode.value==='existente'?existingSelect.value:null;return data;}};
}};
