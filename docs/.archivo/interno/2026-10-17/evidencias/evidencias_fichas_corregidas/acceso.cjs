const { chromium } = require('/Users/danielflores/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');

const ROOT = path.resolve('.');
const OUT_DIR = path.resolve(ROOT, 'output/evidencias_fichas_corregidas/acceso');
if (!fs.existsSync(OUT_DIR)) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
}

const CHROME_PATH = path.resolve(ROOT, '.local-browsers/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing');
const ACCOUNTS_FILE = path.resolve(ROOT, '.aislamiento/perfiles-evaluacion.json');
const accounts = JSON.parse(fs.readFileSync(ACCOUNTS_FILE, 'utf8'));

const navMapping = [
  ['alertas', 'alertas.ver'],
  ['gobierno', 'gobierno.ver'],
  ['reclamos', 'reclamos.ver'],
  ['desempeno', 'actividades.ver'],
  ['evidencias', 'evidencias.ver'],
  ['tubo-trabajo', 'compromisos.ver'],
  ['validacion', 'evidencias.revisar'],
  ['casos-sociales', 'atenciones.ver'],
  ['ingreso-atencion', 'atenciones.crear'],
  ['reportes', 'reportes.ver'],
  ['auditoria', 'auditoria.ver'],
  ['delegaciones', 'delegaciones.ver'],
  ['roles', 'roles.ver'],
  ['cargos', 'cargos.ver'],
  ['usuarios', 'usuarios.ver'],
  ['items-metas', 'items-metas.ver'],
  ['configuraciones-metas', 'configuraciones-metas.ver'],
  ['tipos-atencion', 'tipos-atencion.ver'],
  ['subatenciones', 'subatenciones.ver']
];

async function run() {
  console.log('Iniciando batería de pruebas automáticas para Acceso (ACC-01, ACC-02, ACC-03)...');
  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROME_PATH
  });

  const resultados = {
    fecha: new Date().toISOString(),
    navegador: 'Google Chrome for Testing ' + browser.version(),
    entorno: 'LOCAL/QA',
    servidor: 'http://127.0.0.1:8010',
    casos: {}
  };

  try {
    // ==========================================
    // ACC-01: Login con los 6 roles activos
    // ==========================================
    console.log('\n--- Ejecutando ACC-01: Inicio de sesión con los 6 roles activos ---');
    const rolesActivos = ['Administrador', 'Coordinador', 'Delegado', 'Funcionario', 'Verificador', 'Consulta'];
    resultados.casos['ACC-01'] = { nombre: 'Inicio de sesión por cada rol activo', variantes: [] };

    for (const rolName of rolesActivos) {
      const acc = accounts.find(a => a.perfil === rolName && a.is_active);
      assert.ok(acc, `Cuenta para perfil ${rolName} encontrada`);
      console.log(`Probando rol: ${rolName} (usuario: ${acc.usuario})...`);

      const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
      const page = await context.newPage();
      const erroresJS = [];
      page.on('pageerror', err => erroresJS.push(err.message));

      // 1. Visitar login y verificar sin sesión (401)
      await page.goto('http://127.0.0.1:8010/pages/login.html');
      await page.locator('#username').waitFor();
      const unauthStatus = await page.evaluate(async () => {
        const r = await fetch('/api/contexto/');
        return r.status;
      });
      assert.equal(unauthStatus, 401, 'No debe haber sesión activa antes de loguear');

      // 2. Ingresar credenciales válidas
      await page.fill('#username', acc.usuario);
      await page.fill('#password', acc.clave);
      const [loginRes] = await Promise.all([
        page.waitForResponse(r => r.url().endsWith('/api/login/') && r.request().method() === 'POST'),
        page.click('#btn-submit')
      ]);
      assert.equal(loginRes.status(), 200, `Login para ${acc.usuario} debe ser HTTP 200`);

      await page.waitForURL('**/index.html');
      await page.waitForFunction(() => window.SGRContext?.usuario?.id);

      // 3. Verificar datos de cabecera
      const visibleUser = await page.locator('#session-user').innerText();
      const visibleRole = await page.locator('#session-role').innerText();
      const visibleDelegation = await page.locator('#session-delegation-select option:checked').innerText();
      const contextUser = await page.evaluate(() => window.SGRContext.usuario);
      assert.equal(contextUser.username, acc.usuario, 'La sesión debe corresponder a la cuenta ingresada');
      assert.equal(visibleUser, contextUser.nombre, 'Nombre visible coincide con usuario autenticado');
      assert.equal(visibleRole, rolName, `Rol visible debe ser ${rolName}`);
      assert.ok(visibleDelegation.includes(acc.delegacion_codigo), `Delegación activa debe incluir ${acc.delegacion_codigo}`);

      // 4. Verificar menú lateral adaptado según permisos
      const visibleMenuLinks = await page.locator('#site-sidebar a').evaluateAll(links =>
        links.map(a => new URL(a.href).pathname).sort()
      );
      const permisos = await page.evaluate(() => window.SGRContext.permisos);
      const expectedLinks = ['/index.html', ...navMapping.filter(([_, perm]) => permisos.includes(perm)).map(([file]) => '/pages/' + file + '.html')].sort();
      assert.deepEqual(visibleMenuLinks, expectedLinks, `El menú visible debe coincidir exactamente con los permisos del rol ${rolName}`);

      // Expandir detalles para la captura
      for (const section of await page.locator('.nav-section').all()) {
        await section.evaluate(el => el.open = true);
      }

      // Captura 1: Inicio y menú del rol
      const pic1 = `EV-ACC01-${rolName}-01.png`;
      await page.screenshot({ path: path.join(OUT_DIR, pic1), fullPage: true });

      // 5. Navegar a un módulo accesible y recargar
      const targetPage = visibleMenuLinks.find(url => url !== '/index.html') || '/index.html';
      await page.goto('http://127.0.0.1:8010' + targetPage);
      await page.waitForFunction(() => window.SGRContext?.usuario?.id);
      await page.reload();
      await page.waitForFunction(() => window.SGRContext?.usuario?.id);

      // Captura 2: Módulo activo y recarga con persistencia de sesión
      const pic2 = `EV-ACC01-${rolName}-02.png`;
      await page.screenshot({ path: path.join(OUT_DIR, pic2), fullPage: true });

      // 6. Cerrar sesión
      await page.click('#logout-local');
      await page.waitForURL('**/pages/login.html');
      const logoutStatus = await page.evaluate(async () => {
        const r = await fetch('/api/contexto/');
        return r.status;
      });
      assert.equal(logoutStatus, 401, 'Sesión debe cerrarse');

      resultados.casos['ACC-01'].variantes.push({
        perfil: rolName,
        usuario: acc.usuario,
        identidad_visible_verificada: true,
        delegacion: acc.delegacion_codigo + ' · ' + acc.delegacion_nombre,
        total_links: visibleMenuLinks.length,
        estado: 'Aprobado',
        evidencias: [pic1, pic2],
        erroresJS
      });

      await context.close();
      console.log(`  -> Aprobado (${visibleMenuLinks.length} opciones en menú)`);
    }

    // ==========================================
    // ACC-03: Cierre de sesión y botón Atrás
    // ==========================================
    console.log('\n--- Ejecutando ACC-03: Cierre de sesión y protección de ruta con botón Atrás ---');
    const accFunc = accounts.find(a => a.usuario === 'funcionario1.qa');
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();

    // Iniciar sesión
    await page.goto('http://127.0.0.1:8010/pages/login.html');
    await page.fill('#username', accFunc.usuario);
    await page.fill('#password', accFunc.clave);
    await Promise.all([
      page.waitForResponse(r => r.url().endsWith('/api/login/')),
      page.click('#btn-submit')
    ]);
    await page.waitForURL('**/index.html');

    // Navegar a ruta interna protegida
    await page.goto('http://127.0.0.1:8010/pages/ingreso-atencion.html');
    await page.waitForFunction(() => window.SGRContext?.usuario?.id);
    const picAcc03_01 = 'EV-ACC03-01-SesionActiva.png';
    await page.screenshot({ path: path.join(OUT_DIR, picAcc03_01), fullPage: true });

    // Cerrar sesión
    await page.click('#logout-local');
    await page.waitForURL('**/pages/login.html');

    // Pulsar botón Atrás en el navegador
    await page.goBack();
    await page.waitForTimeout(1000);

    // Comprobar que una petición de datos protegidos devuelve HTTP 401
    const contextStatus = await page.evaluate(async () => {
      const r = await fetch('/api/contexto/');
      return r.status;
    });
    assert.equal(contextStatus, 401, 'Petición a datos protegidos debe devolver HTTP 401');

    // Si recarga la página, el frontend debe redirigir a login
    await page.reload();
    await page.waitForURL('**/pages/login.html');
    assert.equal(new URL(page.url()).pathname, '/pages/login.html', 'Debe redirigir al login tras expirar sesión');

    const picAcc03_02 = 'EV-ACC03-02-PostLogoutRechazo.png';
    await page.screenshot({ path: path.join(OUT_DIR, picAcc03_02), fullPage: true });

    resultados.casos['ACC-03'] = {
      nombre: 'Cierre de sesión, botón Atrás y rechazo de rutas protegidas',
      estado: 'Aprobado',
      evidencias: [picAcc03_01, picAcc03_02],
      observado: 'Sesión finalizada mediante logout. Al pulsar botón Atrás y recargar o solicitar contexto, el servidor respondió HTTP 401 y la interfaz redirigió automáticamente a login.html.'
    };
    await context.close();
    console.log('  -> Aprobado (HTTP 401 y redirección comprobada)');

    // ==========================================
    // ACC-02: Rechazo de accesos inválidos
    // ==========================================
    console.log('\n--- Ejecutando ACC-02: Rechazo de credenciales, vacíos y cuentas inactivas ---');
    resultados.casos['ACC-02'] = { nombre: 'Rechazo de accesos inválidos', variantes: [] };

    const variantesAcc02 = [
      { id: 'V01', desc: 'Contraseña incorrecta', user: 'funcionario1.qa', pass: 'ClaveTotalmenteErronea.999' },
      { id: 'V02', desc: 'Usuario inexistente', user: 'usuario_fantasma_no_existe', pass: 'CualquierClave.123' },
      { id: 'V03', desc: 'Cuenta inactiva (is_active=False)', user: 'inactivo.qa', pass: accounts.find(a => a.usuario === 'inactivo.qa')?.clave },
      { id: 'V04', desc: 'Rol inactivo (estado=False)', user: 'rol_inactivo.qa', pass: accounts.find(a => a.usuario === 'rol_inactivo.qa')?.clave },
      { id: 'V05', desc: 'Campos vacíos', user: '', pass: '' }
    ];

    for (const v of variantesAcc02) {
      console.log(`Probando ACC-02-${v.id}: ${v.desc}...`);
      const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
      const page = await context.newPage();

      await page.goto('http://127.0.0.1:8010/pages/login.html');
      await page.locator('#username').waitFor();

      if (v.user) await page.fill('#username', v.user);
      if (v.pass) await page.fill('#password', v.pass);

      let statusRecibido = null;
      let errorCapturado = null;

      if (v.id === 'V05') {
        // En campos vacíos, verificar validación del formulario
        await page.click('#btn-submit');
        const validationMessage = await page.$eval('#username', el => el.validationMessage);
        assert.ok(validationMessage.length > 0, 'Debe solicitar rellenar el campo');
        errorCapturado = 'Validación HTML5: ' + validationMessage;
        statusRecibido = 'Cliente';
      } else {
        const [res] = await Promise.all([
          page.waitForResponse(r => r.url().endsWith('/api/login/')),
          page.click('#btn-submit')
        ]);
        statusRecibido = res.status();
        assert.ok(statusRecibido === 400 || statusRecibido === 401 || statusRecibido === 403, `Debe rechazar con código 4xx, obtenido: ${statusRecibido}`);
        await page.waitForSelector('.swal2-popup', { state: 'visible', timeout: 3000 });
        errorCapturado = await page.locator('.swal2-title, .swal2-html-container').allInnerTexts();
      }

      // Asegurar que no se creó sesión
      const checkSession = await page.evaluate(async () => {
        const r = await fetch('/api/contexto/');
        return r.status;
      });
      assert.equal(checkSession, 401, 'No debe existir sesión activa tras intento inválido');

      const pic = `EV-ACC02-${v.id}.png`;
      await page.screenshot({ path: path.join(OUT_DIR, pic), fullPage: true });

      resultados.casos['ACC-02'].variantes.push({
        variante: v.id,
        descripcion: v.desc,
        usuario_probado: v.user,
        http_status: statusRecibido,
        mensaje_observado: errorCapturado,
        sin_sesion_verificado: true,
        estado: 'Aprobado',
        evidencia: pic
      });

      await context.close();
      console.log(`  -> Aprobado (Rechazo correcto: ${statusRecibido})`);
    }

  } catch (err) {
    console.error('Error durante la ejecución:', err);
    process.exitCode = 1;
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(OUT_DIR, 'resultados_acceso.json'), JSON.stringify(resultados, null, 2));
    console.log(`\nBatería de Acceso finalizada. Resultados guardados en ${path.join(OUT_DIR, 'resultados_acceso.json')}`);
  }
}

run();
