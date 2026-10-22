/* Vista previa calculada por el servidor; la captura final vuelve a aplicar la regla. */
window.SGREligibility={mount({getBeneficiary,onChange}={}){
 const $=id=>document.getElementById(id),box=$('eligibility-preview');let version=0,timer;
 const show=data=>{box.replaceChildren();const title=document.createElement('strong');title.textContent=data.estado+' · '+data.clasificacion;box.append(title);const list=document.createElement('ul');for(const reason of data.motivos){const li=document.createElement('li');li.textContent=reason;list.append(li);}box.append(list);const note=document.createElement('p');note.className='help';note.textContent='Vista previa con la regla vigente'+(data.regla?' v'+data.regla.version:'')+'. La regla se confirma al guardar. Ser candidato no otorga puntos ni reemplaza la revisión de evidencias.';box.append(note);};
 async function update(){const stamp=++version;if(!$('item').value){box.textContent='Selecciona un tipo de actividad para consultar su clasificación.';return;}box.textContent='Consultando clasificación…';try{const r=await SGRApi.send('/api/clasificacion-actividades/evaluar/',{item:Number($('item').value),contacto:$('contact').value.trim(),telefono:$('phone').value.trim(),rut_contacto:$('run').value.trim(),beneficiario_usuario:getBeneficiary?.()||null});if(stamp===version)show(r.data);}catch(e){if(stamp===version)box.textContent=e.message;}}
 function schedule(){version++;clearTimeout(timer);timer=setTimeout(update,300);}
 for(const id of ['contact','phone','run'])$(id).addEventListener('input',schedule);$('item').addEventListener('change',schedule);
 return {update,schedule};
}};
