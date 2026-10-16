/**
 * Módulo exclusivo para el CRUD de Usuarios (Tarea T10)
 * Este script es completamente independiente del mantenedor común.
 */
document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:8000/api/usuarios/";
    const tbody = document.getElementById("table-body");
    const btnNuevo = document.getElementById("btn-nuevo");
    const modalEditor = document.getElementById("modal-editor");
    const formEditor = document.getElementById("form-editor");
    const modalClose = document.getElementById("modal-close");
    const modalCancel = document.getElementById("modal-cancel");
    const pageInfo = document.getElementById("page-info");
    
    let currentUserId = null;

    // Función para obtener el token de seguridad de Django
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 1. Cargar Usuarios
    async function loadUsers() {
        try {
            const res = await fetch(API_URL + "?page_size=50", { credentials: "include" });
            const data = await res.json();
            if (data.success && data.results) {
                renderTable(data.results);
                if(pageInfo) pageInfo.textContent = `Mostrando ${data.results.length} registros`;
            }
        } catch (error) {
            console.error("Error cargando usuarios:", error);
        }
    }

    // 2. Renderizar Tabla
    function renderTable(data) {
        tbody.innerHTML = "";
        if (data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center;">No hay usuarios registrados.</td></tr>`;
            return;
        }
        data.forEach(item => {
            const tr = document.createElement("tr");
            const nombreCompleto = (item.first_name || item.last_name) ? `${item.first_name} ${item.last_name}`.trim() : item.username;
            const rolNombre = item.rol ? item.rol.nombre : '<span style="color: #666; font-style: italic;">Sin Rol</span>';
            const delegacionNombre = item.delegacion ? item.delegacion.nombre : '<span style="color: #666; font-style: italic;">Sin Delegación</span>';
            const badgeClass = item.estado ? "green" : "red";
            const badgeText = item.estado ? "Activo" : "Inactivo";
            const actionText = item.estado ? "Desactivar" : "Activar";
            
            tr.innerHTML = `
                <td><strong>${nombreCompleto}</strong><br><small>${item.username}</small></td>
                <td>${item.email}</td>
                <td>${rolNombre}</td>
                <td>${delegacionNombre}</td>
                <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                <td>
                    <button type="button" class="linkbtn btn-ver">Ver</button> · 
                    <button type="button" class="linkbtn btn-editar">Editar</button> · 
                    <button type="button" class="linkbtn btn-toggle">${actionText}</button>
                </td>
            `;
            
            // Asignar eventos de clic directamente a cada botón
            tr.querySelector(".btn-ver").addEventListener("click", () => showVer(item, nombreCompleto, rolNombre, delegacionNombre));
            tr.querySelector(".btn-editar").addEventListener("click", () => showEditar(item));
            tr.querySelector(".btn-toggle").addEventListener("click", () => toggleEstado(item.id));
            
            tbody.appendChild(tr);
        });
    }

    // 3. Acción: Ver Detalles (Reemplaza al modal undefined)
    function showVer(item, nombre, rol, del) {
        Swal.fire({
            title: "Detalle de Cuenta",
            html: `
                <div style="text-align: left; line-height: 1.8; margin-top: 10px;">
                    <p><strong>Nombre:</strong> ${nombre}</p>
                    <p><strong>Correo:</strong> ${item.email}</p>
                    <p><strong>Rol Asignado:</strong> ${rol}</p>
                    <p><strong>Delegación:</strong> ${del}</p>
                    <p><strong>Estado:</strong> <span class="badge ${item.estado ? 'green' : 'red'}">${item.estado ? 'Activo' : 'Inactivo'}</span></p>
                </div>
            `,
            icon: "info",
            confirmButtonColor: "#B01E22"
        });
    }

    // 4. Acción: Editar
    function showEditar(item) {
        currentUserId = item.id;
        document.getElementById("modal-title").textContent = "Editar Usuario";
        document.getElementById("campo-nombre").value = `${item.first_name} ${item.last_name}`.trim();
        document.getElementById("campo-correo").value = item.email;
        document.getElementById("campo-estado").value = item.estado ? "Activo" : "Inactivo";
        modalEditor.showModal();
    }

    // 5. Acción: Nuevo
    if (btnNuevo) {
        btnNuevo.addEventListener("click", () => {
            currentUserId = null;
            formEditor.reset();
            document.getElementById("modal-title").textContent = "Nuevo Usuario";
            document.getElementById("campo-estado").value = "Activo";
            modalEditor.showModal();
        });
    }

    // 6. Cerrar Modal
    [modalClose, modalCancel].forEach(btn => {
        if (btn) btn.addEventListener("click", () => {
            modalEditor.close();
            formEditor.reset();
        });
    });

    // 7. Guardar (Submit)
    formEditor.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const btnSubmit = formEditor.querySelector('button[type="submit"]');
        const originalText = btnSubmit.innerHTML;
        btnSubmit.innerHTML = "Guardando...";
        btnSubmit.disabled = true;

        const nombreCompleto = document.getElementById("campo-nombre").value.trim();
        const email = document.getElementById("campo-correo").value.trim();
        const estadoRaw = document.getElementById("campo-estado").value;
        
        const partes = nombreCompleto.split(" ");
        const payload = {
            username: email,
            email: email,
            first_name: partes[0] || "",
            last_name: partes.slice(1).join(" "),
            estado: (estadoRaw === "Activo"),
            password: currentUserId ? "" : "Password123*" // Requisito del backend para usuarios nuevos
        };

        const url = currentUserId ? `${API_URL}${currentUserId}/` : API_URL;
        const method = currentUserId ? "PUT" : "POST";

        try {
            const res = await fetch(url, {
                method: method,
                headers: { 
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken") || ""
                },
                credentials: "include",
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (res.ok && data.success) {
                modalEditor.close();
                Swal.fire("Éxito", data.message || "Usuario guardado correctamente", "success");
                loadUsers();
            } else {
                Swal.fire("Error", data.error?.message || data.message || "Verifica los datos", "error");
            }
        } catch (err) {
            Swal.fire("Error", "Problema de conexión con el servidor", "error");
        } finally {
            btnSubmit.innerHTML = originalText;
            btnSubmit.disabled = false;
        }
    });

    // 8. Activar / Desactivar
    async function toggleEstado(id) {
        try {
            const res = await fetch(`${API_URL}${id}/toggle-estado/`, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") || "" },
                credentials: "include"
            });
            const data = await res.json();
            if (res.ok && data.success) {
                Swal.fire("Actualizado", data.message, "success");
                loadUsers();
            } else {
                Swal.fire("Error", "No se pudo cambiar el estado", "error");
            }
        } catch (err) {
            Swal.fire("Error", "Problema de conexión", "error");
        }
    }

    // Iniciar carga al abrir la página
    loadUsers();
});