/* Recorrido real de edición y carga; ejecutar solo contra un entorno LOCAL de QA.
   Requiere Playwright y tres cuentas de prueba preparadas, nunca datos productivos. */
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const base = process.env.SGR_TEST_BASE_URL || 'http://127.0.0.1:8012';
assert(['localhost', '127.0.0.1'].includes(new URL(base).hostname), 'Solo se permiten pruebas locales');
const password = process.env.SGR_TEST_PASSWORD;
assert(password, 'Configura SGR_TEST_PASSWORD con una clave ficticia local');
(async () => {
 const browser = await chromium.launch({headless:true, ...(process.env.SGR_BROWSER_PATH ? {executablePath:process.env.SGR_BROWSER_PATH} : {})});
 try {
  const login = async username => {
   const c = await browser.newContext({viewport:{width:1280,height:900}});
   let token = (await (await c.request.get(base+'/api/csrf/')).json()).data.csrfToken;
   const r=await c.request.post(base+'/api/login/',{data:{username,password},headers:{'X-CSRFToken':token,Origin:base,Referer:base+'/pages/login.html'}});
   assert.equal(r.status(),200,'Ingreso de cuenta QA');
   token=(await(await c.request.get(base+'/api/csrf/')).json()).data.csrfToken;
   return {c, headers:{'X-CSRFToken':token,Origin:base,Referer:base+'/index.html'}};
  };
  const owner=await login(process.env.SGR_TEST_USER||'progreso');
  const opts=await(await owner.c.request.get(base+'/api/operacion/opciones/')).json();
  const created=await owner.c.request.post(base+'/api/operacion/actividades/',{headers:owner.headers,data:{fecha:new Date().toLocaleDateString('en-CA'),solicitud:'QA recorrido detalle '+Date.now(),accion:'Trabajo de prueba local',contacto:'Persona ficticia',telefono:'912345678',sector:'QA',item:opts.items[0].id,unidad:1}});
  assert.equal(created.status(),201,'Creación de actividad aislada');const item=(await created.json()).data;
  const page=await owner.c.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const open=async()=>{await page.goto(base+'/pages/desempeno.html?registro='+item.id);await page.getByRole('dialog',{name:'Detalle del registro',exact:true}).waitFor();};
  await open();let detail=page.getByRole('dialog',{name:'Detalle del registro',exact:true});
  if(process.env.SGR_TEST_OUTPUT_DIR){
   const fs=require('node:fs'),path=require('node:path');fs.mkdirSync(process.env.SGR_TEST_OUTPUT_DIR,{recursive:true});
   await page.screenshot({path:path.join(process.env.SGR_TEST_OUTPUT_DIR,'detalle-escritorio.png')});
   await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(process.env.SGR_TEST_OUTPUT_DIR,'detalle-movil.png')});
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,'Sin desbordamiento móvil');
   await page.setViewportSize({width:1280,height:900});
  }
  // RED: el código anterior no ofrece estas acciones en el detalle.
  assert.equal(await detail.getByRole('button',{name:'Editar actividad',exact:true}).count(),1,'Falta Editar actividad dentro del detalle');
  assert.equal(await detail.getByRole('button',{name:'Adjuntar evidencia',exact:true}).count(),1,'Falta Adjuntar evidencia dentro del detalle');
  const reader=await login(process.env.SGR_TEST_READER||'lectura_progreso');const readpage=await reader.c.newPage();await readpage.goto(base+'/pages/desempeno.html?registro='+item.id);const rd=readpage.getByRole('dialog',{name:'Detalle del registro',exact:true});await rd.waitFor();assert.equal(await rd.getByRole('button',{name:'Editar actividad',exact:true}).count(),0);assert.equal(await rd.getByRole('button',{name:'Adjuntar evidencia',exact:true}).count(),0);
  await detail.getByRole('button',{name:'Editar actividad',exact:true}).click();
  let form=page.getByRole('dialog',{name:'Editar actividad',exact:true});await form.getByLabel('Acción realizada').fill('Acción corregida desde el detalle');
  await form.getByRole('button',{name:'Guardar registro',exact:true}).click();await page.locator('.swal2-confirm').click();
  detail=page.getByRole('dialog',{name:'Detalle del registro',exact:true});await detail.waitFor();assert((await detail.innerText()).includes('Acción corregida desde el detalle'));
  await detail.getByRole('button',{name:'Adjuntar evidencia',exact:true}).click();
  form=page.getByRole('dialog',{name:'Adjuntar evidencia',exact:true});const selector=form.locator('select[name=actividad]');assert.equal(await selector.inputValue(),String(item.id));assert(await selector.isDisabled(),'Actividad debe quedar fijada');
  await form.locator('input[type=file]').setInputFiles({name:'respaldo-qa.png',mimeType:'image/png',buffer:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==','base64')});
  await form.getByLabel('Descripción del respaldo').fill('Evidencia ficticia del recorrido local');
  await form.getByRole('button',{name:'Guardar registro',exact:true}).click();await page.locator('.swal2-confirm').click();
  detail=page.getByRole('dialog',{name:'Detalle del registro',exact:true});await detail.waitFor();await detail.getByRole('link',{name:/respaldo-qa\.png/}).waitFor();
  let data=(await(await owner.c.request.get(base+'/api/operacion/actividades/'+item.id+'/')).json()).data;assert.equal(data.estado,'Pendiente');
  let ev=(await(await owner.c.request.get(base+'/api/operacion/evidencias/')).json()).results.find(e=>e.actividad===item.id);assert(ev,'Evidencia asociada a la actividad exacta');
  const reviewer=await login(process.env.SGR_TEST_REVIEWER||'otro_progreso');
  const returned=await reviewer.c.request.post(base+'/api/operacion/evidencias/'+ev.id+'/revisar/',{headers:reviewer.headers,data:{_version:ev.version,decision:'Corrección',observacion:'Adjuntar versión corregida para QA local'}});assert.equal(returned.status(),200);
  await page.goto(base+'/pages/evidencias.html?registro='+ev.id);let evdetail=page.getByRole('dialog',{name:'Detalle e historial de evidencia',exact:true});await evdetail.waitFor();await evdetail.getByRole('button',{name:'Corregir evidencia',exact:true}).click();
  form=page.getByRole('dialog',{name:'Adjuntar evidencia',exact:true});assert.equal(await form.locator('select[name=actividad]').inputValue(),String(item.id));assert.equal(await form.locator('select[name=reemplaza]').inputValue(),String(ev.id));assert(await form.locator('select[name=reemplaza]').isDisabled());
  await form.locator('input[type=file]').setInputFiles({name:'correccion-qa.png',mimeType:'image/png',buffer:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==','base64')});await form.getByLabel('Descripción del respaldo').fill('Nueva versión ficticia para QA');await form.getByRole('button',{name:'Guardar registro',exact:true}).click();await page.locator('.swal2-confirm').click();
  await page.getByRole('dialog',{name:'Detalle e historial de evidencia',exact:true}).waitFor();const previous=ev.id;ev=(await(await owner.c.request.get(base+'/api/operacion/evidencias/')).json()).results.find(e=>e.reemplaza===previous);assert(ev,'Nueva versión debe conservar vínculo al respaldo devuelto');
  const reviewed=await reviewer.c.request.post(base+'/api/operacion/evidencias/'+ev.id+'/revisar/',{headers:reviewer.headers,data:{_version:ev.version,decision:'Aprobada',observacion:'Aprobación ficticia de QA local'}});assert.equal(reviewed.status(),200,'Revisión por otra persona');
  await open();detail=page.getByRole('dialog',{name:'Detalle del registro',exact:true});assert.equal(await detail.getByRole('button',{name:'Editar actividad',exact:true}).count(),0);assert.equal(await detail.getByRole('button',{name:'Adjuntar evidencia',exact:true}).count(),0);
  assert.deepEqual(errors,[]);console.log('OK: detalle → editar → guardar → adjuntar al registro fijado → pendiente → devolución → nueva versión vinculada → revisión ajena → validada; consulta sin acciones.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
