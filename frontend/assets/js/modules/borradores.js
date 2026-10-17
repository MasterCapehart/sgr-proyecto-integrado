/* Protección de borradores en memoria. Nunca guarda contraseñas ni datos ciudadanos en Storage. */
(() => {
 const baselines=new WeakMap();const publicPages=['login','recovery','validate-code','new-password'];
 const enabled=()=>!publicPages.includes(document.body.dataset.page);
 function controls(form){return Array.from(form.elements).filter(e=>e.matches('input,select,textarea')&&!e.readOnly&&!['submit','button','reset','hidden'].includes(e.type));}
 function signature(form){return JSON.stringify(controls(form).map(e=>[e.id||e.name,e.type==='file'?Array.from(e.files||[],f=>[f.name,f.size,f.lastModified]):e.type==='checkbox'||e.type==='radio'?e.checked:e.multiple?Array.from(e.selectedOptions,o=>o.value):e.value]));}
 function remember(form){if(form&&!baselines.has(form))baselines.set(form,signature(form));}
 function dirty(form){return baselines.has(form)&&baselines.get(form)!==signature(form);}
 function clean(form){if(form)baselines.set(form,signature(form));}
 function hasChanges(){return enabled()&&Array.from(document.forms).some(dirty);}
 function cleanAll(){Array.from(document.forms).forEach(clean);}
 async function discard(){const result=await Swal.fire({target:document.querySelector('dialog[open]')||document.body,icon:'warning',title:'¿Descartar cambios sin guardar?',text:'Los datos del formulario aún no se han guardado.',showCancelButton:true,confirmButtonText:'Descartar cambios',cancelButtonText:'Seguir editando'});return result.isConfirmed;}
 document.addEventListener('focusin',e=>remember(e.target.closest('form')),true);
 document.addEventListener('pointerdown',e=>remember(e.target.closest('form')),true);
 document.addEventListener('reset',e=>{queueMicrotask(()=>clean(e.target));},true);
 document.addEventListener('cancel',async e=>{if(!enabled()||!Array.from(e.target.querySelectorAll('form')).some(dirty))return;e.preventDefault();if(await discard()){e.target.querySelectorAll('form').forEach(clean);e.target.close();}},true);
 document.addEventListener('click',async e=>{
  if(!enabled()||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;
  const button=e.target.closest('button'),dialog=button?.closest('dialog');
  if(dialog&&['Cancelar','Cerrar','✕'].includes(button.textContent.trim())&&Array.from(dialog.querySelectorAll('form')).some(dirty)){
   e.preventDefault();e.stopImmediatePropagation();if(await discard()){dialog.querySelectorAll('form').forEach(clean);dialog.close();}return;
  }
  const a=e.target.closest('a[href]');if(!a||a.target==='_blank'||a.hasAttribute('download')||!hasChanges())return;
  const url=new URL(a.href,location.href);if(url.origin!==location.origin||url.pathname.startsWith('/api/')||url.href===location.href||url.protocol!=='http:'&&url.protocol!=='https:')return;
  e.preventDefault();e.stopImmediatePropagation();if(await discard()){cleanAll();location.assign(url.href);}
 },true);
 window.addEventListener('beforeunload',e=>{if(hasChanges()){e.preventDefault();e.returnValue='';}});
 window.SGRDrafts={hasChanges,clean,cleanAll,remember};
})();
