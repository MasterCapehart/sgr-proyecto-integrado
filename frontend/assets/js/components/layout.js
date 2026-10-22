(() => {
  const publicPages = ['login', 'recovery', 'validate-code', 'new-password'];
  function dirty() { return window.SGRDrafts?.hasChanges() || false; }

  const ICONS = {
    hitos: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18M8 15h3"/></svg>`,
    periodos: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"></rect><path d="M16 3v4M8 3v4M3 11h18"></path></svg>`,
    home: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>`,
    alertas: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>`,
    gobierno: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
    reclamos: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`,
    actividades: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>`,
    evidencias: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>`,
    compromisos: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
    validacion: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
    'casos-sociales': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>`,
    atencion: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><line x1="20" y1="8" x2="20" y2="14"></line><line x1="23" y1="11" x2="17" y2="11"></line></svg>`,
    reportes: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`,
    auditoria: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
    delegaciones: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>`,
    roles: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>`,
    cargos: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>`,
    usuarios: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
    'items-metas': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>`,
    'configuraciones-metas': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`,
    'tipos-atencion': `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"></path><line x1="7" y1="7" x2="7.01" y2="7"></line></svg>`,
    subatenciones: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>`
  };

  ICONS['clasificacion-actividades'] = ICONS['items-metas'];
  const links = [
    ['clasificacion-actividades','clasificacion-actividades','Clasificación de actividades','clasificacion-actividades.ver'],
    ['hitos','hitos','Hitos y festividades','hitos.ver'],
    ['vecinos','vecinos','Vecinos','vecinos.ver'],
    ['organizaciones','organizaciones','Juntas y organizaciones','organizaciones.ver'],
    ['alertas', 'alertas', 'Alertas operativas', 'alertas.ver'],
    ['gobierno', 'gobierno', 'Reglas y permisos', 'gobierno.ver'],
    ['reclamos', 'reclamos', 'Reclamos y felicitaciones', 'reclamos.ver'],
    ['actividades', 'desempeno', 'Mi planilla de trabajo', 'actividades.ver'],
    ['evidencias', 'evidencias', 'Evidencias', 'evidencias.ver'],
    ['compromisos', 'tubo-trabajo', 'Tubo de trabajo', 'compromisos.ver'],
    ['validacion', 'validacion', 'Bandeja de validación', 'evidencias.revisar'],
    ['casos-sociales', 'casos-sociales', 'Gestión social', 'atenciones.ver'],
    ['atencion', 'ingreso-atencion', 'Registrar atención', 'atenciones.crear'],
    ['reportes', 'reportes', 'Reportes operativos', 'reportes.ver'],
    ['auditoria', 'auditoria', 'Auditoría', 'auditoria.ver'],
    ['delegaciones', 'delegaciones', 'Delegaciones', 'delegaciones.ver'],
    ['roles', 'roles', 'Roles y permisos', 'roles.ver'],
    ['cargos', 'cargos', 'Cargos y áreas', 'cargos.ver'],
    ['usuarios', 'usuarios', 'Usuarios', 'usuarios.ver'],
    ['items-metas', 'items-metas', 'Ítems y metas', 'items-metas.ver'],
    ['periodos', 'periodos', 'Períodos de gestión', 'periodos.ver'],
    ['configuraciones-metas', 'configuraciones-metas', 'Configuración de metas', 'configuraciones-metas.ver'],
    ['tipos-atencion', 'tipos-atencion', 'Tipos de atención', 'tipos-atencion.ver'],
    ['subatenciones', 'subatenciones', 'Subatenciones', 'subatenciones.ver']
  ];

  window.SGRLayout = {
    hasUnsavedChanges: dirty,
    mount({ basePath = '', currentPage }) {
      const header = document.getElementById('site-header'), sidebar = document.getElementById('site-sidebar');
      if (header) {
        header.classList.add('top');
        header.innerHTML = `
          <a class="mark" href="${basePath}index.html">
            <span class="brand-symbol"><img src="${basePath}assets/images/escudo-blanco.svg" alt="Escudo Municipalidad de La Serena"></span>
            <span><strong>SGR · La Serena</strong><small>Sistema de Gestión de Resultados</small></span>
          </a>
        `;
      }

      if (!document.getElementById('academic-notice')) {
        const notice = document.createElement('footer');
        notice.id = 'academic-notice';
        notice.className = 'academic-notice';
        notice.setAttribute('aria-label', 'Aviso académico');
        const title = document.createElement('strong');
        title.textContent = 'Proyecto académico';
        const text = document.createElement('span');
        text.textContent = 'Datos ficticios de demostración. Diseño sin aprobación institucional.';
        notice.append(title, text);
        document.body.append(notice);
      }

      if (publicPages.includes(currentPage)) return;

      if (header) {
        header.insertAdjacentHTML('beforeend', `
          <div class="context">
            <small><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="vertical-align:text-top;margin-right:3px"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>DELEGACIÓN ACTIVA</small>
            <select id="session-delegation-select" aria-label="Delegación activa"></select>
          </div>
          <div class="identity">
            <div class="user-avatar" id="session-avatar">👤</div>
            <div class="user-details">
              <strong id="session-user">Cargando…</strong>
              <div class="user-badges">
                <small id="session-role" class="role-badge">Cargando…</small>
                <small id="session-cargo" class="cargo-badge" hidden></small>
              </div>
            </div>
            <button type="button" id="logout-local" class="btn-logout" title="Cerrar sesión">Cerrar sesión</button>
          </div>
        `);
      }

      const mobile = document.createElement('button');
      mobile.type = 'button';
      mobile.className = 'button mobilemenu';
      mobile.textContent = '☰ Menú';
      mobile.setAttribute('aria-label', 'Menú');
      mobile.setAttribute('aria-controls', 'site-sidebar');
      header?.after(mobile);
      if (sidebar) {
        sidebar.classList.add('sidebar');
        const layout = sidebar.closest('.layout');
        const narrow = window.matchMedia('(max-width:700px)');
        const showMenu = open => {
          if (!open && sidebar.contains(document.activeElement)) mobile.focus();
          sidebar.hidden = !open;
          sidebar.classList.toggle('open', open);
          layout?.classList.toggle('sidebar-collapsed', !open);
          mobile.setAttribute('aria-expanded', String(open));
          mobile.title = open ? 'Ocultar menú' : 'Mostrar menú';
        };
        showMenu(!narrow.matches);
        mobile.onclick = () => showMenu(sidebar.hidden);
        narrow.addEventListener('change', event => showMenu(!event.matches));
      } else mobile.hidden = true;

      const ready = (async () => {
        try {
          const { data: c } = await SGRApi.request('/api/contexto/');
          window.SGRContext = c;
          const user = document.getElementById('session-user');
          const role = document.getElementById('session-role');
          const avatar = document.getElementById('session-avatar');
          const select = document.getElementById('session-delegation-select');

          if (user) user.textContent = c.usuario.nombre;
          if (role) role.textContent = c.rol;
          if (avatar && c.usuario.nombre) {
            const parts = c.usuario.nombre.trim().split(/\s+/);
            const initials = parts.length >= 2 ? (parts[0][0] + parts[1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();
            avatar.textContent = initials;
          }

          const cargo = document.getElementById('session-cargo');
          if (cargo && c.usuario.cargo_nombre) {
            cargo.hidden = false;
            cargo.textContent = c.usuario.cargo_nombre;
          }

          if (select) {
            for (const d of c.delegaciones_autorizadas) {
              const o = new Option(`${d.codigo || ''} · ${d.nombre}`, d.id, false, d.id === c.delegacion_activa?.id);
              select.add(o);
            }
            select.disabled = c.delegaciones_autorizadas.length <= 1;
            select.addEventListener('change', async () => {
              const previous = window.SGRContext.delegacion_activa?.id;
              if (dirty() && !(await Swal.fire({
                target: document.querySelector('dialog[open]') || document.body,
                icon: 'warning',
                title: '¿Cambiar delegación?',
                text: 'Se descartarán los datos sin guardar.',
                showCancelButton: true,
                confirmButtonText: 'Cambiar',
                cancelButtonText: 'Mantener'
              })).isConfirmed) {
                select.value = previous;
                return;
              }
              try {
                await SGRApi.send('/api/contexto/cambiar-delegacion/', { delegacion_id: Number(select.value) });
                SGRDrafts.cleanAll();
                location.reload();
              } catch (e) {
                select.value = previous;
                SGRApi.message(e.message);
              }
            });
          }

          if (sidebar) {
            const nav = document.createElement('nav');
            nav.setAttribute('aria-label', 'Navegación principal');
            const home = document.createElement('a');
            home.href = basePath + 'index.html';
            home.innerHTML = `${ICONS.home} <span>Inicio</span>`;
            home.className = 'nav';
            if (currentPage === 'home') home.setAttribute('aria-current', 'page');
            nav.append(home);

            // Read-only catalogues belong to consultation, not administration.
            const catalogIds = ['clasificacion-actividades','items-metas', 'tipos-atencion', 'subatenciones'];
            const readOnlyCatalogs = catalogIds.filter(id =>
              c.permisos.includes(id + '.ver') &&
              !['crear', 'editar', 'desactivar','configurar'].some(action => c.permisos.includes(id + '.' + action))
            );
            const groups = [
              ['Gestión diaria', ['actividades', 'atencion', 'casos-sociales', 'compromisos', 'reclamos']],
              ['Planificación', ['hitos']],
              ['Comunidad', ['vecinos','organizaciones']],
              ['Seguimiento', ['evidencias', 'validacion', 'alertas', 'reportes', 'auditoria']],
              ['Catálogos de consulta', readOnlyCatalogs],
              ['Administración', ['clasificacion-actividades','delegaciones', 'usuarios', 'roles', 'cargos', 'items-metas', 'periodos', 'configuraciones-metas', 'tipos-atencion', 'subatenciones', 'gobierno'].filter(id => !readOnlyCatalogs.includes(id))]
            ];

            for (const [label, ids] of groups) {
              const available = links.filter(x => ids.includes(x[0]) && c.permisos.includes(x[3]) && !(x[0] === 'atencion' && (document.body.dataset.capturePreview || c.permisos.includes('actividades.crear')))).sort((a, b) => ids.indexOf(a[0]) - ids.indexOf(b[0]));
              if (!available.length) continue;
              const section = document.createElement('details');
              section.className = 'nav-section';
              section.open = label === 'Gestión diaria' || available.some(x => x[0] === currentPage) || (currentPage === 'compromiso-detalle' && ids.includes('compromisos'));
              const title = document.createElement('summary');
              title.textContent = label;
              section.append(title);
              for (const [id, file, text] of available) {
                const a = document.createElement('a');
                a.href = basePath + 'pages/' + (document.body.dataset.capturePreview && id === 'actividades' ? 'planilla-unificada-preview' : file) + '.html';
                const iconSvg = ICONS[id] || '';
                a.innerHTML = `${iconSvg} <span>${text}</span>`;
                a.className = 'nav';
                if (id === currentPage || (id === 'compromisos' && currentPage === 'compromiso-detalle')) {
                  a.setAttribute('aria-current', 'page');
                }
                section.append(a);
              }
              nav.append(section);
            }
            sidebar.replaceChildren(nav);
          }

          document.getElementById('logout-local')?.addEventListener('click', async () => {
            if (dirty() && !(await Swal.fire({
              target: document.querySelector('dialog[open]') || document.body,
              icon: 'warning',
              title: '¿Cerrar sesión?',
              text: 'Hay datos sin guardar.',
              showCancelButton: true
            })).isConfirmed) return;
            try {
              await SGRApi.send('/api/logout/', {});
              SGRDrafts.cleanAll();
              sessionStorage.clear();
              location.href = basePath + 'pages/login.html';
            } catch (e) {
              SGRApi.message(e.message);
            }
          });

          return c;
        } catch (e) {
          if (e.status === 401) {
            sessionStorage.clear();
            location.replace(basePath + 'pages/login.html');
          } else {
            await SGRApi.message(e.message);
          }
          throw e;
        }
      })();

      window.SGRSession = ready;
      ready.catch(() => {});
    }
  };
})();
