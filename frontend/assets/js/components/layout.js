(() => {
 const publicPages=['login','recovery','validate-code','new-password'];
 function dirty(){return window.SGRDrafts?.hasChanges()||false;}
 const links=[['alertas','alertas','Alertas operativas','alertas.ver'],['gobierno','gobierno','Reglas y permisos','gobierno.ver'],['reclamos','reclamos','Reclamos y felicitaciones','reclamos.ver'],['actividades','desempeno','Mi planilla de trabajo','actividades.ver'],['evidencias','evidencias','Evidencias','evidencias.ver'],['compromisos','tubo-trabajo','Tubo de trabajo','compromisos.ver'],['validacion','validacion','Bandeja de validación','evidencias.revisar'],['casos-sociales','casos-sociales','Gestión social','atenciones.ver'],['atencion','ingreso-atencion','Registrar atención','atenciones.crear'],['reportes','reportes','Reportes operativos','reportes.ver'],['auditoria','auditoria','Auditoría','auditoria.ver'],['delegaciones','delegaciones','Delegaciones','delegaciones.ver'],['roles','roles','Roles y permisos','roles.ver'],['cargos','cargos','Cargos y áreas','cargos.ver'],['usuarios','usuarios','Usuarios','usuarios.ver'],['items-metas','items-metas','Ítems y metas','items-metas.ver'],['configuraciones-metas','configuraciones-metas','Configuración de metas','configuraciones-metas.ver'],['tipos-atencion','tipos-atencion','Tipos de atención','tipos-atencion.ver'],['subatenciones','subatenciones','Subatenciones','subatenciones.ver']];
 window.SGRLayout={hasUnsavedChanges:dirty,mount({basePath='',currentPage}){
  const header=document.getElementById('site-header'),sidebar=document.getElementById('site-sidebar');
  if(header){header.classList.add('top');header.innerHTML=`<a class="mark" href="${basePath}index.html"><img src="${basePath}assets/images/escudo-blanco.svg" alt="Escudo Municipalidad de La Serena"><span><strong>SGR · La Serena</strong><small>Sistema de Gestión de Resultados</small></span></a>`;}
  if(publicPages.includes(currentPage))return;
  if(header)header.insertAdjacentHTML('beforeend','<div class="context"><small>Delegación activa</small><select id="session-delegation-select" aria-label="Delegación activa"></select></div><div class="identity"><strong id="session-user">Cargando…</strong><small id="session-role">Cargando…</small><small id="session-cargo" hidden></small><button type="button" id="logout-local">Cerrar sesión</button></div>');
  const mobile=document.createElement('button');mobile.type='button';mobile.className='button mobilemenu';mobile.textContent='☰ Menú';mobile.setAttribute('aria-expanded','false');mobile.setAttribute('aria-controls','site-sidebar');header?.after(mobile);mobile.onclick=()=>{const open=sidebar.classList.toggle('open');mobile.setAttribute('aria-expanded',String(open));};
  const ready=(async()=>{
   try{
    const {data:c}=await SGRApi.request('/api/contexto/');window.SGRContext=c;
    const user=document.getElementById('session-user'),role=document.getElementById('session-role'),select=document.getElementById('session-delegation-select');
    if(user)user.textContent=c.usuario.nombre;if(role)role.textContent=c.rol;const cargo=document.getElementById('session-cargo');if(cargo&&c.usuario.cargo_nombre){cargo.hidden=false;cargo.textContent=c.usuario.cargo_nombre;}
    if(select){
     for(const d of c.delegaciones_autorizadas){const o=new Option(`${d.codigo || ''} · ${d.nombre}`,d.id,false,d.id===c.delegacion_activa?.id);select.add(o);}
     select.disabled=c.delegaciones_autorizadas.length<=1;
     select.addEventListener('change',async()=>{
      const previous=window.SGRContext.delegacion_activa?.id;
      if(dirty() && !(await Swal.fire({target:document.querySelector('dialog[open]')||document.body,icon:'warning',title:'¿Cambiar delegación?',text:'Se descartarán los datos sin guardar.',showCancelButton:true,confirmButtonText:'Cambiar',cancelButtonText:'Mantener'})).isConfirmed){select.value=previous;return;}
      try{await SGRApi.send('/api/contexto/cambiar-delegacion/',{delegacion_id:Number(select.value)});SGRDrafts.cleanAll();location.reload();}catch(e){select.value=previous;SGRApi.message(e.message);}
     });
    }
    if(sidebar){const nav=document.createElement('nav');nav.setAttribute('aria-label','Navegación principal');const home=document.createElement('a');home.href=basePath+'index.html';home.textContent='Inicio';home.className='nav';if(currentPage==='home')home.setAttribute('aria-current','page');nav.append(home);
     const groups=[['Gestión diaria',['actividades','atencion','casos-sociales','compromisos','reclamos']],['Seguimiento',['evidencias','validacion','alertas','reportes','auditoria']],['Administración',['delegaciones','usuarios','roles','cargos','items-metas','configuraciones-metas','tipos-atencion','subatenciones','gobierno']]];
     for(const [label,ids] of groups){const available=links.filter(x=>ids.includes(x[0])&&c.permisos.includes(x[3])).sort((a,b)=>ids.indexOf(a[0])-ids.indexOf(b[0]));if(!available.length)continue;const section=document.createElement('details');section.className='nav-section';section.open=label==='Gestión diaria'||available.some(x=>x[0]===currentPage)||(currentPage==='compromiso-detalle'&&ids.includes('compromisos'));const title=document.createElement('summary');title.textContent=label;section.append(title);for(const [id,file,text] of available){const a=document.createElement('a');a.href=basePath+'pages/'+file+'.html';a.textContent=text;a.className='nav';if(id===currentPage||(id==='compromisos'&&currentPage==='compromiso-detalle'))a.setAttribute('aria-current','page');section.append(a);}nav.append(section);}sidebar.replaceChildren(nav);}
    document.getElementById('logout-local')?.addEventListener('click',async()=>{if(dirty() && !(await Swal.fire({target:document.querySelector('dialog[open]')||document.body,icon:'warning',title:'¿Cerrar sesión?',text:'Hay datos sin guardar.',showCancelButton:true})).isConfirmed)return;try{await SGRApi.send('/api/logout/',{});SGRDrafts.cleanAll();sessionStorage.clear();location.href=basePath+'pages/login.html';}catch(e){SGRApi.message(e.message);}});
    return c;
   }catch(e){if(e.status===401){sessionStorage.clear();location.replace(basePath+'pages/login.html');}else await SGRApi.message(e.message);throw e;}
  })();window.SGRSession=ready;ready.catch(()=>{});
 }};
})();
