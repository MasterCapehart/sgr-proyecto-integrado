/**
 * Módulo del CRUD de Usuarios (T10, T11, T12)
 * Conectado a la API de Django: listado paginado, búsqueda, filtro de estado,
 * crear/editar con rol y delegación reales, activar/desactivar y exportar a Excel.
 */
document.addEventListener("DOMContentLoaded", () => {
    const API_BASE = "http://127.0.0.1:8000/api";
    const API_URL = `${API_BASE}/usuarios/`;
    const PAGE_SIZE = 10;

    const tbody = document.getElementById("table-body");
    const btnNuevo = document.getElementById("btn-nuevo");
    const btnExport = document.getElementById("btn-export");
    const searchInput = document.getElementById("search-input");
    const statusFilter = document.getElementById("status-filter");
    const modalEditor = document.getElementById("modal-editor");
    const formEditor = document.getElementById("form-editor");
    const modalClose = document.getElementById("modal-close");
    const modalCancel = document.getElementById("modal-cancel");
    const pageInfo = document.getElementById("page-info");
    const btnPrev = document.getElementById("btn-prev");
    const btnNext = document.getElementById("btn-next");
    const pageNumber = document.getElementById("page-number");
    const campoRol = document.getElementById("campo-rol");
    const campoDelegacion = document.getElementById("campo-delegacion");
    const campoPassword = document.getElementById("campo-password");
    const ayudaPassword = document.getElementById("ayuda-password");

    let currentUserId = null;
    let currentPage = 1;
    let totalPages = 1;

    function getCookie(name) {
        const parte = document.cookie.split(";").map(c => c.trim()).find(c => c.startsWith(name + "="));
        return parte ? decodeURIComponent(parte.substring(name.length + 1)) : null;
    }

    function esc(str) {
        return String(str ?? "").replace(/[&<>"']/g, s => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[s]);
    }

    function mensajeError(data, porDefecto) {
        const det = data?.error?.details;
        if (det && typeof det === "object") {
            const textos = Object.values(det).flat().filter(Boolean);
            if (textos.length) return textos.join(" ");
        }
        return data?.error?.message || data?.message || porDefecto;
    }

    async function llamar(url, opciones = {}) {
        const res = await fetch(url, { credentials: "include", ...opciones });
        let data = null;
        try { data = await res.json(); } catch (_) { /* respuesta sin JSON */ }
        return { res, data };
    }

    // ---------- Catálogos para los selectores ----------
    async function cargarCatalogo(endpoint, select, textoVacio) {
        select.innerHTML = `<option value="">${textoVacio}</option>`;
        try {
            const { res, data } = await llamar(`${API_BASE}/${endpoint}/?estado=activos&page_size=100`);
            if (res.ok && data?.results) {
                data.results.forEach(it => {
                    const op = document.createElement("option");
                    op.value = it.id;
                    op.textContent = it.nombre;
                    select.appendChild(op);
                });
            }
        } catch (_) { /* se informa al guardar */ }
    }

    // ---------- Listado ----------
    async function loadUsers() {
        const term = searchInput ? searchInput.value.trim() : "";
        const url = `${API_URL}?search=${encodeURIComponent(term)}&page_size=${PAGE_SIZE}&page=${currentPage}`;
        try {
            const { res, data } = await llamar(url);
            if (res.status === 401) {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;">Debe iniciar sesión para ver los usuarios.</td></tr>`;
                if (pageInfo) pageInfo.textContent = "Sin sesión activa";
                return;
            }
            if (!res.ok || !data?.success) throw new Error(`HTTP ${res.status}`);

            let items = data.results;
            // La API de Usuarios no filtra por estado: se filtra aquí sobre la página recibida
            const estadoSel = statusFilter ? statusFilter.value : "todos";
            if (estadoSel === "activo") items = items.filter(i => i.estado);
            if (estadoSel === "inactivo") items = items.filter(i => !i.estado);

            totalPages = data.total_pages || 1;
            renderTable(items);
            if (pageInfo) pageInfo.textContent = `Mostrando ${items.length} de ${data.count} registros (Página ${data.page} de ${totalPages})`;
            if (pageNumber) pageNumber.textContent = data.page;
            if (btnPrev) btnPrev.disabled = data.page <= 1;
            if (btnNext) btnNext.disabled = data.page >= totalPages;
        } catch (error) {
            console.error("Error cargando usuarios:", error);
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;">No se pudieron cargar los usuarios. Verifique que el servidor esté activo.</td></tr>`;
            if (pageInfo) pageInfo.textContent = "Error al cargar";
        }
    }

    function renderTable(data) {
        tbody.innerHTML = "";
        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:24px;">No se encontraron usuarios.</td></tr>`;
            return;
        }
        data.forEach(item => {
            const nombre = `${item.first_name || ""} ${item.last_name || ""}`.trim() || item.username;
            const rol = item.rol ? esc(item.rol.nombre) : '<span style="color:#666;font-style:italic;">Sin rol</span>';
            const del = item.delegacion ? esc(item.delegacion.nombre) : '<span style="color:#666;font-style:italic;">Sin delegación</span>';
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${esc(nombre)}</strong><br><small>${esc(item.username)}</small></td>
                <td>${esc(item.email)}</td>
                <td>${rol}</td>
                <td>${del}</td>
                <td><span class="badge ${item.estado ? "green" : "red"}">${item.estado ? "Activo" : "Inactivo"}</span></td>
                <td>
                    <button type="button" class="linkbtn btn-ver">Ver</button> ·
                    <button type="button" class="linkbtn btn-editar">Editar</button> ·
                    <button type="button" class="linkbtn btn-toggle">${item.estado ? "Desactivar" : "Activar"}</button>
                </td>`;
            tr.querySelector(".btn-ver").addEventListener("click", () => showVer(item, nombre));
            tr.querySelector(".btn-editar").addEventListener("click", () => showEditar(item));
            tr.querySelector(".btn-toggle").addEventListener("click", () => confirmarToggle(item, nombre));
            tbody.appendChild(tr);
        });
    }

    function showVer(item, nombre) {
        Swal.fire({
            title: "Detalle de cuenta",
            html: `<div style="text-align:left;line-height:1.8;">
                <p><strong>Nombre:</strong> ${esc(nombre)}</p>
                <p><strong>Usuario:</strong> ${esc(item.username)}</p>
                <p><strong>Correo:</strong> ${esc(item.email)}</p>
                <p><strong>RUT:</strong> ${esc(item.rut || "-")}</p>
                <p><strong>Rol:</strong> ${esc(item.rol ? item.rol.nombre : "Sin rol")}</p>
                <p><strong>Delegación:</strong> ${esc(item.delegacion ? item.delegacion.nombre : "Sin delegación")}</p>
                <p><strong>Estado:</strong> ${item.estado ? "Activo" : "Inactivo"}</p></div>`,
            icon: "info",
            confirmButtonColor: "#B01E22"
        });
    }

    // ---------- Modal ----------
    function configurarPassword(esNuevo) {
        campoPassword.value = "";
        campoPassword.required = esNuevo;
        if (ayudaPassword) ayudaPassword.textContent = esNuevo
            ? "Obligatoria. Mínimo 8 caracteres. El usuario podrá cambiarla con la recuperación de clave."
            : "Déjela vacía para mantener la contraseña actual.";
    }

    function showEditar(item) {
        currentUserId = item.id;
        formEditor.reset();
        document.getElementById("modal-title").textContent = "Editar usuario";
        document.getElementById("campo-nombre").value = `${item.first_name || ""} ${item.last_name || ""}`.trim();
        document.getElementById("campo-correo").value = item.email || "";
        document.getElementById("campo-rut").value = item.rut || "";
        campoRol.value = item.rol ? String(item.rol.id) : "";
        campoDelegacion.value = item.delegacion ? String(item.delegacion.id) : "";
        document.getElementById("campo-estado").value = item.estado ? "Activo" : "Inactivo";
        configurarPassword(false);
        modalEditor.showModal();
    }

    if (btnNuevo) {
        btnNuevo.addEventListener("click", () => {
            currentUserId = null;
            formEditor.reset();
            document.getElementById("modal-title").textContent = "Nuevo usuario";
            document.getElementById("campo-estado").value = "Activo";
            configurarPassword(true);
            modalEditor.showModal();
        });
    }

    [modalClose, modalCancel].forEach(btn => {
        if (btn) btn.addEventListener("click", () => { modalEditor.close(); formEditor.reset(); });
    });

    formEditor.addEventListener("submit", async (e) => {
        e.preventDefault();

        const nombreCompleto = document.getElementById("campo-nombre").value.trim();
        const email = document.getElementById("campo-correo").value.trim();
        const rut = document.getElementById("campo-rut").value.trim();
        const password = campoPassword.value;

        if (!nombreCompleto || !email || !campoRol.value || !campoDelegacion.value) {
            Swal.fire({ icon: "warning", title: "Campos obligatorios", text: "Complete nombre, correo, rol y delegación.", confirmButtonColor: "#B01E22" });
            return;
        }
        if (!currentUserId && password.length < 8) {
            Swal.fire({ icon: "warning", title: "Contraseña", text: "La contraseña inicial debe tener al menos 8 caracteres.", confirmButtonColor: "#B01E22" });
            return;
        }
        if (currentUserId && password && password.length < 8) {
            Swal.fire({ icon: "warning", title: "Contraseña", text: "La nueva contraseña debe tener al menos 8 caracteres.", confirmButtonColor: "#B01E22" });
            return;
        }

        const btnSubmit = formEditor.querySelector('button[type="submit"]');
        const textoOriginal = btnSubmit.innerHTML;
        btnSubmit.innerHTML = "Guardando...";
        btnSubmit.disabled = true;

        const partes = nombreCompleto.split(/\s+/);
        const payload = {
            username: email,
            email: email,
            first_name: partes[0] || "",
            last_name: partes.slice(1).join(" "),
            rut: rut || null,               // null evita choques del campo único cuando no hay RUT
            rol: campoRol.value,
            delegacion: campoDelegacion.value,
            estado: document.getElementById("campo-estado").value === "Activo"
        };
        if (password) payload.password = password;

        // El backend de Usuarios crea y edita con POST (edición: POST /usuarios/<id>/)
        const url = currentUserId ? `${API_URL}${currentUserId}/` : API_URL;

        try {
            const { res, data } = await llamar(url, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") || "" },
                body: JSON.stringify(payload)
            });
            if (res.ok && data?.success) {
                modalEditor.close();
                formEditor.reset();
                Swal.fire({ icon: "success", title: "Éxito", text: data.message || "Usuario guardado.", confirmButtonColor: "#B01E22" });
                await loadUsers();
            } else {
                Swal.fire({ icon: "error", title: "No se pudo guardar", text: mensajeError(data, "Verifique los datos."), confirmButtonColor: "#B01E22" });
            }
        } catch (err) {
            Swal.fire({ icon: "error", title: "Error", text: "Problema de conexión con el servidor.", confirmButtonColor: "#B01E22" });
        } finally {
            btnSubmit.innerHTML = textoOriginal;
            btnSubmit.disabled = false;
        }
    });

    // ---------- Activar / desactivar ----------
    async function confirmarToggle(item, nombre) {
        const accion = item.estado ? "desactivar" : "activar";
        const r = await Swal.fire({
            title: `¿Desea ${accion} esta cuenta?`,
            text: nombre,
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#ad0000",
            confirmButtonText: `Sí, ${accion}`,
            cancelButtonText: "Cancelar"
        });
        if (!r.isConfirmed) return;
        try {
            const { res, data } = await llamar(`${API_URL}${item.id}/toggle-estado/`, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") || "" }
            });
            if (res.ok && data?.success) {
                Swal.fire({ icon: "success", title: "Actualizado", text: data.message, confirmButtonColor: "#B01E22" });
                await loadUsers();
            } else {
                Swal.fire({ icon: "error", title: "Error", text: mensajeError(data, "No se pudo cambiar el estado."), confirmButtonColor: "#B01E22" });
            }
        } catch (err) {
            Swal.fire({ icon: "error", title: "Error", text: "Problema de conexión.", confirmButtonColor: "#B01E22" });
        }
    }

    // ---------- Búsqueda, filtros, paginación, exportación ----------
    let temporizador = null;
    if (searchInput) searchInput.addEventListener("input", () => {
        clearTimeout(temporizador);
        temporizador = setTimeout(() => { currentPage = 1; loadUsers(); }, 300);
    });
    if (statusFilter) statusFilter.addEventListener("change", () => { currentPage = 1; loadUsers(); });
    if (btnPrev) btnPrev.addEventListener("click", () => { if (currentPage > 1) { currentPage--; loadUsers(); } });
    if (btnNext) btnNext.addEventListener("click", () => { if (currentPage < totalPages) { currentPage++; loadUsers(); } });

    if (btnExport) btnExport.addEventListener("click", () => {
        const term = searchInput ? searchInput.value.trim() : "";
        window.location.href = `${API_URL}export/?search=${encodeURIComponent(term)}`;
    });

    window.addEventListener("sgr:delegacion-cambiada", () => loadUsers());

    // ---------- Inicio ----------
    cargarCatalogo("roles", campoRol, "Seleccione un rol");
    cargarCatalogo("delegaciones", campoDelegacion, "Seleccione una delegación");
    loadUsers();
});