/* Búsqueda y registro vecinal; el directorio se consulta en la delegación activa. */
window.SGRNeighbors = {
  mount({beforeSelect = () => true} = {}) {
    const $ = id => document.getElementById(id);
    const affiliations=document.createElement('div');affiliations.className='notice neutral';affiliations.hidden=true;$('neighbor-selected').after(affiliations);
    let selected = null, version = 0, creating = false, createKey;
    const fields = {nombre:'contact', rut:'run', telefono:'phone', sector:'sector', junta_vecinos:'junta-vecinos'};
    const message = text => { $('neighbor-message').textContent = text; };
    function choose(person) {
      const allowed = beforeSelect(person);
      if (allowed !== true) { message(allowed); return false; }
      selected = person; version++;
      for (const [field, id] of Object.entries(fields)) $(id).value = person[field] || '';
      affiliations.replaceChildren();const memberships=person.organizaciones||[];
      affiliations.hidden=!memberships.length;
      if(memberships.length){const title=document.createElement('strong');title.textContent='Organizaciones registradas de este vecino';affiliations.append(title);for(const membership of memberships){const line=document.createElement('p');line.textContent=membership.nombre+' · '+membership.rol;affiliations.append(line);}const label=document.createElement('label');label.textContent='Organización relacionada con esta gestión · opcional';const select=document.createElement('select');select.id='neighbor-organization';label.htmlFor=select.id;select.add(new Option('Conservar texto actual / sin selección',''));for(const membership of memberships)select.add(new Option(membership.nombre+' · '+membership.rol,membership.id));select.onchange=()=>{const found=memberships.find(m=>String(m.id)===select.value);if(found)$('junta-vecinos').value=found.nombre;};affiliations.append(label,select);}
      $('contact').readOnly = true; $('run').readOnly = true;
      $('neighbor-selected').textContent = 'Vecino seleccionado: ' + person.nombre + (person.rut ? ' · RUN ' + person.rut : ' · RUN no informado');
      $('neighbor-selected').hidden = false; $('neighbor-clear').hidden = false;
      $('neighbor-results').replaceChildren();
      message('Datos completados. Puedes ajustar teléfono, sector y junta para este registro; el directorio vecinal conserva sus datos originales.');
      return true;
    }
    async function search() {
      const query = $('neighbor-search').value.trim(), requestVersion = ++version;
      $('neighbor-results').replaceChildren();
      if (query.length < 3) { message('Escribe al menos tres letras del nombre o el RUN completo.'); return; }
      message('Buscando vecino…');
      try {
        const response = await SGRApi.send('/api/vecinos/buscar/', {q:query});
        if (requestVersion !== version) return;
        const rows = response.results;
        message(response.message || (!rows.length ? 'No encontramos coincidencias en esta delegación. Si es un vecino nuevo, pulsa «Registrar vecino».' : rows.length + ' coincidencias.' + (response.has_more ? ' Hay más resultados; precisa el nombre.' : '')));
        for (const person of rows) {
          const button = document.createElement('button'); button.type = 'button'; button.className = 'neighbor-result';
          const name = document.createElement('strong'); name.textContent = person.nombre;
          const description = document.createElement('span'); description.textContent = ['RUN: ' + (person.rut || 'No informado'), person.sector, person.junta_vecinos].filter(Boolean).join(' · ');
          const action = document.createElement('small'); action.textContent = 'Usar estos datos';
          button.append(name, description, action); button.onclick = () => choose(person); $('neighbor-results').append(button);
        }
      } catch(error) { if (requestVersion === version) message(error.message); }
    }
    $('neighbor-find').onclick = search;
    $('neighbor-search').onkeydown = event => { if (event.key === 'Enter') { event.preventDefault(); search(); } };
    $('neighbor-clear').onclick = () => {
      selected = null; version++; affiliations.hidden=true;affiliations.replaceChildren(); $('contact').readOnly = false; $('run').readOnly = false;
      $('neighbor-selected').hidden = true; $('neighbor-clear').hidden = true;
      message('Selección quitada. Los datos del formulario se conservan para que puedas editarlos o buscar a otra persona.');
    };
    $('neighbor-new').onclick = () => {
      if($('new-neighbor-direccion'))$('new-neighbor-direccion').value='';
      createKey = crypto.randomUUID(); $('neighbor-create-message').textContent = '';
      for (const [field, id] of Object.entries(fields)) $('new-neighbor-' + field).value = $(id).value;
      if (!$('new-neighbor-nombre').value && !/^[\d.\sKk-]+$/.test($('neighbor-search').value)) $('new-neighbor-nombre').value = $('neighbor-search').value.trim();
      $('neighbor-dialog').showModal(); $('new-neighbor-nombre').focus();
    };
    $('neighbor-cancel').onclick = () => $('neighbor-dialog').close();
    $('neighbor-create').onsubmit = async event => {
      event.preventDefault(); if (creating || !$('neighbor-create').reportValidity()) return;
      const data = {clave_idempotencia:createKey}; for (const field of Object.keys(fields)) data[field] = $('new-neighbor-' + field).value.trim();
      if($('new-neighbor-direccion'))data.direccion=$('new-neighbor-direccion').value.trim();
      const allowed = beforeSelect(data); if (allowed !== true) { $('neighbor-create-message').textContent = allowed; return; }
      creating = true; $('neighbor-confirm').disabled = true;
      try {
        const response = await SGRApi.send('/api/vecinos/', data);
        if (choose(response.data)) $('neighbor-dialog').close();
      } catch(error) {
        $('neighbor-create-message').textContent = error.message;
        if (error.status === 409) {
          $('neighbor-search').value = data.rut || data.nombre; $('neighbor-dialog').close(); await search();
          message('Revisa las coincidencias: el RUN o esta solicitud ya estaban registrados. Selecciona el vecino correcto.');
        }
      } finally { creating = false; $('neighbor-confirm').disabled = false; }
    };
    return {get:() => selected, matches(person) {
      if (!selected) return true;
      const name = value => value.trim().replace(/\s+/g, ' ').toLocaleLowerCase('es');
      const rut = value => (value || '').replace(/[.\s-]/g, '').toUpperCase().replace(/^0+/, '');
      return name(selected.nombre) === name(person.nombre) && (!selected.rut || !person.rut || rut(selected.rut) === rut(person.rut));
    }};
  }
};
