/* Transporte de sesión y CSRF. Los errores nunca se convierten en datos de demostración. */
window.SGRApi = {
  async request(url, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    if (!['GET','HEAD'].includes(method)) {
      const csrfResponse = await fetch('/api/csrf/', {credentials:'same-origin'});
      if (!csrfResponse.ok) throw new Error('No fue posible preparar la operación segura.');
      const csrfData = await csrfResponse.json();
      options.headers = {...options.headers, 'X-CSRFToken': csrfData.data.csrfToken};
    }
    const response = await fetch(url, {...options, credentials:'same-origin'});
    const data = await response.json().catch(() => ({}));
    if (!response.ok || data.success === false) {
      const details = data.error?.details || {};
      const message = [data.error?.message || 'No fue posible completar la operación.', ...Object.entries(details).map(([k,v]) => `${k}: ${Array.isArray(v)?v.join(', '):v}`)].join('\n');
      const error = new Error(message); error.status=response.status; throw error;
    }
    return data;
  },
  send(url, data, method='POST') { return this.request(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); },
  async all(resource, query='') {
    let results=[], page=1, response;
    do { response=await this.request(`/api/${resource}/?page_size=100&page=${page}&${query}`);results.push(...response.results);page++; } while(page<=response.total_pages);
    return results;
  },
  message(text, icon='error') { return Swal.fire({target:document.querySelector('dialog[open]') || document.body,icon,title:icon==='success'?'Operación completada':'Revisa la información',text,confirmButtonColor:'#AD0000'}); },
  toast(text, icon='success') {
    const Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      didOpen: (toast) => {
        toast.onmouseenter = Swal.stopTimer;
        toast.onmouseleave = Swal.resumeTimer;
      }
    });
    return Toast.fire({ icon, title: text });
  }
};
