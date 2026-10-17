(() => {
  const page = document.body.dataset.page;
  const basePath = document.body.dataset.basePath;
  window.SGRLayout.mount({ basePath, currentPage: page });
  const messages = {
    confirm: { title: 'Confirmación de ejemplo', text: 'Esta demostración no guarda información.', icon: 'question', showCancelButton: true, confirmButtonText: 'Confirmar', cancelButtonText: 'Cancelar' },
    warning: { title: 'Advertencia de ejemplo', text: 'Comprueba los datos antes de continuar.', icon: 'warning' },
    error: { title: 'Error de ejemplo', text: 'Este mensaje muestra el componente de error.', icon: 'error' }
  };
  document.querySelectorAll('[data-alert]').forEach(button => {
    button.addEventListener('click', () => {
      window.Swal.fire({ ...messages[button.dataset.alert], confirmButtonColor: '#AD0000', confirmButtonText: 'Aceptar', ...messages[button.dataset.alert] });
    });
  });
})();
