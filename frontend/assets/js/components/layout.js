/* Componentes compartidos; la identidad real se incorporará desde el backend. */
window.SGRLayout = {
  mount({ basePath, currentPage }) {
    const header = document.getElementById('site-header');
    const sidebar = document.getElementById('site-sidebar');
    if (header) {
      if (currentPage === 'login' || currentPage === 'recovery' || currentPage === 'validate-code' || currentPage === 'new-password') {
        header.innerHTML = `<a class="brand" href="${basePath}index.html"><img src="${basePath}assets/images/escudo-blanco.svg" alt="Escudo de la Municipalidad de La Serena"><span><strong>SGR</strong><small>Municipalidad de La Serena</small></span></a><div class="public-title">Sistema de Gestión de Resultados</div>`;
      } else {
        header.innerHTML = `<a class="brand" href="${basePath}index.html"><img src="${basePath}assets/images/escudo-blanco.svg" alt="Escudo de la Municipalidad de La Serena"><span><strong>SGR</strong><small>Municipalidad de La Serena</small></span></a><dl class="identity" aria-label="Contexto de acceso"><div><dt>Usuario</dt><dd id="session-user">Sin sesión</dd></div><div><dt>Rol</dt><dd id="session-role">Sin asignar</dd></div><div><dt>Delegación activa</dt><dd id="session-delegation">Sin seleccionar</dd></div></dl>`;
      }
    }
    if (sidebar) {
      sidebar.innerHTML = `<nav aria-label="Navegación principal">
        <a href="${basePath}index.html" ${currentPage === 'home' ? 'aria-current="page"' : ''}>Inicio</a>
        <a href="${basePath}pages/guia.html" ${currentPage === 'guide' ? 'aria-current="page"' : ''}>Guía de componentes</a>
        <p class="nav-heading">Operación</p>
        <a href="${basePath}pages/ingreso-atencion.html" ${currentPage === 'atencion' ? 'aria-current="page"' : ''}>Registrar atención</a>
        <p class="nav-heading">Administración</p>
        <a href="${basePath}pages/delegaciones.html" ${currentPage === 'delegaciones' ? 'aria-current="page"' : ''}>Delegaciones</a>
        <a href="${basePath}pages/roles.html" ${currentPage === 'roles' ? 'aria-current="page"' : ''}>Roles y permisos</a>
        <a href="${basePath}pages/usuarios.html" ${currentPage === 'usuarios' ? 'aria-current="page"' : ''}>Usuarios</a>
        <a href="${basePath}pages/items-metas.html" ${currentPage === 'items-metas' ? 'aria-current="page"' : ''}>Ítems y metas</a>
        <p class="nav-heading">Catálogos</p>
        <a href="${basePath}pages/tipos-atencion.html" ${currentPage === 'tipos-atencion' ? 'aria-current="page"' : ''}>Tipos de atención</a>
        <a href="${basePath}pages/subatenciones.html" ${currentPage === 'subatenciones' ? 'aria-current="page"' : ''}>Subatenciones</a>
        <p class="nav-heading">Acceso</p>
        <a href="${basePath}pages/login.html" ${currentPage === 'login' ? 'aria-current="page"' : ''}>Cerrar sesión / Login</a>
      </nav>`;
    }
  }
};
