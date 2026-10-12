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
      sidebar.innerHTML = `<nav aria-label="Navegación principal"><a href="${basePath}index.html" ${currentPage === 'home' ? 'aria-current="page"' : ''}>Inicio</a><a href="${basePath}pages/guia.html" ${currentPage === 'guide' ? 'aria-current="page"' : ''}>Guía de componentes</a><a href="${basePath}pages/login.html" ${currentPage === 'login' ? 'aria-current="page"' : ''}>Iniciar sesión</a><p class="nav-heading">Próximos módulos</p><span class="planned">Acceso y recuperación<small>Pendiente de implementación</small></span><span class="planned">Administración y catálogos<small>Pendiente de implementación</small></span><span class="planned">Atención ciudadana<small>Pendiente de implementación</small></span></nav>`;
    }
  }
};
