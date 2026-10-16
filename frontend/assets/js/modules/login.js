/**
 * Módulo para gestionar el inicio de sesión real conectado al Backend (T05 / T09)
 */

// Función mágica para obtener el CSRF Token de las cookies de Django
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

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const togglePasswordBtn = document.getElementById("toggle-password");
    const submitBtn = document.getElementById("btn-submit");

    // Lógica para mostrar/ocultar contraseña
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener("click", () => {
            const isPassword = passwordInput.type === "password";
            passwordInput.type = isPassword ? "text" : "password";
            togglePasswordBtn.textContent = isPassword ? "Ocultar" : "Mostrar";
            togglePasswordBtn.setAttribute("aria-label", isPassword ? "Ocultar contraseña" : "Mostrar contraseña");
        });
    }

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            if (!loginForm.checkValidity()) {
                loginForm.reportValidity();
                return;
            }

            const email = usernameInput.value.trim();
            const password = passwordInput.value;
            const csrfToken = getCookie('csrftoken'); // Obtenemos el token

            // Bloquear el botón mientras carga
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = "Iniciando sesión...";
            submitBtn.disabled = true;

            try {
                const response = await fetch("http://127.0.0.1:8000/api/login/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        // Enviamos el token para que Django confíe en nosotros
                        "X-CSRFToken": csrfToken || "" 
                    },
                    credentials: "include", 
                    body: JSON.stringify({ username: email, password: password }) // Volvemos a username
                });

                const data = await response.json();

                if (response.ok && !data.error) { // Tu backend devuelve 'error' cuando falla
                    localStorage.setItem("user", JSON.stringify({username: data.usuario}));
                    
                    Swal.fire({
                        title: "¡Bienvenido!",
                        text: data.mensaje || "Has iniciado sesión correctamente.", // Tu backend envía 'mensaje'
                        icon: "success",
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = "roles.html";
                    });
                } else {
                    Swal.fire({
                        title: "Error de acceso",
                        text: data.error || "Credenciales incorrectas.", // Atrapamos el 'error'
                        icon: "error",
                        confirmButtonText: "Intentar de nuevo",
                        confirmButtonColor: "#B01E22" 
                    });
                }
            } catch (error) {
                console.error("Error al conectar con la API:", error);
                Swal.fire({
                    title: "Error de conexión",
                    text: "No se pudo contactar al servidor. Asegúrate de que el backend esté corriendo.",
                    icon: "error",
                    confirmButtonText: "Entendido",
                    confirmButtonColor: "#B01E22"
                });
            } finally {
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }
        });
    }
});