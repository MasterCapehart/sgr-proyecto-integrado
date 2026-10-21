document.addEventListener('DOMContentLoaded',async()=>{
 const target=document.getElementById('main-content'),node=(tag,text)=>{const e=document.createElement(tag);e.textContent=text;return e;};
 try{
  const context=await SGRSession;if(!context.permisos.includes('atenciones.ver'))throw new Error('No tienes permiso para consultar atenciones.');
  const id=new URLSearchParams(location.search).get('id');if(!/^\d+$/.test(id||''))throw new Error('Atención no válida.');
  const a=(await SGRApi.request('/api/atenciones/'+id+'/')).data;target.replaceChildren(node('div','SGR / Atención ciudadana'),node('h1','Detalle de atención'));const card=node('section','');card.className='card';const dl=node('dl','');dl.className='detail-list';
  for(const [label,value] of [['Folio',a.folio],['Solicitante',a.solicitante],['Junta de vecinos',a.junta_vecinos||'No informada'],['Tipo de atención',a.tipo_nombre],['Subatención',a.subatencion_nombre],['Descripción',a.descripcion],['Caso social',a.caso_social||'Sin expediente'],['Gestión',a.numero_gestion||'—'],['Registrado por',a.usuario_nombre]])dl.append(node('dt',label),node('dd',String(value||'—')));card.append(dl);target.append(card);
  function link(text,url){const e=node('a',text);e.href=url;e.className='button secondary';target.append(e);}
  if(a.compromiso&&context.permisos.includes('compromisos.ver'))link('Abrir compromiso vinculado','compromiso-detalle.html?id='+a.compromiso);
  if(a.caso_social)link('Abrir expediente social','casos-sociales.html?caso='+encodeURIComponent(a.caso_social));
  if(a.actividad&&context.permisos.includes('actividades.ver'))link('Abrir registro y evidencias','desempeno.html?registro='+a.actividad);
  link('Volver a atención ciudadana','ingreso-atencion.html');
 }catch(e){target.replaceChildren(node('p',e.message));}
});
