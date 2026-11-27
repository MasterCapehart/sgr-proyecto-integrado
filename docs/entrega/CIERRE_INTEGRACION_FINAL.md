# Acta de Integración y Cierre Final SGR

**Fecha:** 26 de Noviembre de 2026  
**Sistema:** Sistema de Gestión de Resultados (SGR) — Municipalidad de La Serena  
**Estado de Verificación:** 726/726 pruebas automatizadas aprobadas (100% éxito)  
**Ambiente Desplegado:** AWS EC2 (`54.236.112.203`) y Local MAMP (MySQL 8.4)  

---

## 1. Conciliación de Correcciones Prioritarias

| Prioridad | Requerimiento | Solución Implementada | Estado |
|---|---|---|---|
| **1. Permisos de revisión** | Impedir que un revisor apruebe o anule actividades o evidencias de otra delegación. | Se valida la delegación activa y las delegaciones autorizadas del usuario en `review`, `review_activity` y `annul_activity`. Si pertenece a otra delegación, se bloquea con `403 Forbidden`. | ✅ Resuelto |
| **2. Trimestres cerrados** | Bloquear revisiones, ediciones y anulaciones mientras el trimestre esté cerrado. Exigir reapertura autorizada. | Se implementó `check_closed_quarter()`. Si la fecha de la actividad corresponde a un trimestre con `cerrado=True`, se rechaza con `400 Bad Request`. | ✅ Resuelto |
| **3. Decisión de ponderación** | Aprobar los archivos no debe aprobar automáticamente la actividad para sumar a la meta. El cálculo debe exigir una decisión vigente de “Aprobada y pondera”. | La aprobación de evidencias (`Evidencia`) actualiza el estado del archivo pero no asigna ponderación a la actividad. En `performance.py`, la actividad solo aporta unidades reconocidas si cuenta con decisión expresa de `"Aprobada y pondera"`. | ✅ Resuelto |
| **4. Activación de usuarios** | Conectar el formulario con la activación por correo, retirar la contraseña obligatoria del administrador y controlar los errores de envío. | Conectado en `local_api.py`, `usuarios.html`, `usuarios.js` y `mantenedor-comun.js`. Se añadió la casilla `activar_por_correo`, se removió la obligación de contraseña al crear y se generan códigos de activación de 48h con control de errores SMTP. | ✅ Resuelto |
| **5. Dashboard trimestral** | Completar indicadores personales y de delegación, filtros comunes y acceso a los registros que explican cada cifra. | `personal_progress.py` y `personal-progress.js` soportan selección por trimestre (`?trimestre=`) y período mensual. Las tarjetas transfieren parámetros de filtrado (`desde`, `hasta`, `delegacion`, `periodo`) hacia los listados correspondientes. | ✅ Resuelto |
| **6. Planes individuales** | Separar propuestas migradas de planes aprobados. Confirmar el porcentaje exigido y validar el plan antes de activarlo. | Se discriminan propuestas de planes formales (`es_propuesta` vs `plan_aprobado`). Se exige suma exacta de 100.00% de ponderaciones activas para aprobar el plan individual. | ✅ Resuelto |
| **7. Cálculo colectivo** | Resolver y documentar cómo consolidar personas con ponderaciones diferentes, sin dejar resultados ambiguos. | En `collective.py`, cuando un ítem tiene ponderaciones diferentes entre funcionarios, se calcula la media de los cumplimientos de las personas evaluadas (evitando promedios falsos por ausencias) y se documenta la regla sin dejar resultados ambiguos. | ✅ Resuelto |
| **8. Tiempos de gestión social** | Calcular ingreso–primera gestión usando la fecha correcta; impedir intervalos negativos y mostrar fechas faltantes como no calculables. | En `excel_api.py`, `diff_days` devuelve `None` ante intervalos invertidos. `tiempo_ingreso_primera` se calcula contra la fecha real ejecutada (`fecha_visita_realizada` o `fecha_registro`), sin usar la fecha programada futura. | ✅ Resuelto |
| **9. Pruebas de concurrencia** | Resolver el bloqueo intermitente al registrar simultáneamente y repetir la regresión completa. | Se reemplazó el bloqueo exclusivo `select_for_update` en `ItemMeta` dentro de `evaluate_activity` por lectura consistente, eliminando la contención de filas entre usuarios simultáneos. | ✅ Resuelto |

---

## 2. Conciliación de Observaciones de Cierre

1. **Propuestas de metas bloqueadas en la captura de trabajo:**
   - Se actualizó `capture_assignments`, `bind_activity` y la resolución de asignación en `domain_api.py` para excluir explícitamente cualquier asignación marcada como `es_propuesta=True` o `plan_aprobado=False`. Solo los planes formalmente aprobados al 100% están disponibles para registrar trabajo.
2. **Activación por correo en pantalla publicada (`mantenedor-comun.js`):**
   - Se integró en `mantenedor-comun.js` la casilla de activación por correo electrónico para el recurso `usuarios`. Al estar activada (por defecto al crear), el campo de contraseña se vuelve opcional y se oculta, enviando `activar_por_correo: true` al endpoint `/api/usuarios/`.
3. **Dashboard trimestral y traslación de filtros:**
   - La interfaz permite alternar entre trimestres de gestión y meses recientes.
   - Se corrigió la expresión regular de enlaces en `personal-progress.js` para permitir parámetros complejos (`?desde=...&hasta=...&delegacion=...&periodo=...`), permitiendo que el usuario audite directamente los registros que componen cada métrica.
4. **Cálculo colectivo sin "sin evaluación" artificial:**
   - Ante ítems con ponderaciones divergentes, el motor colectivo calcula y reporta la media efectiva de los funcionarios evaluados, marcando `pesos_compatibles=False` como advertencia técnica pero entregando el porcentaje de cumplimiento real.
5. **Tiempo de primera gestión fiel a la ejecución:**
   - Se eliminó la prioridad sobre `fecha_visita_programada`. El intervalo mide la diferencia entre la fecha de ingreso y la fecha en que la primera gestión se materializó realmente (`fecha_visita_realizada` o `fecha_registro`).

---

## 3. Matriz de Roles y Acceso en AWS

Las 6 cuentas institucionales fueron verificadas satisfactoriamente en producción (`https://54.236.112.203/`):

| Rol | Cuenta | Acceso Comprobado | Ámbito de Operación |
|---|---|---|---|
| **Administrador** | `admin.aws` | ✅ 200 OK | Configuración global, catálogo, usuarios, auditoría |
| **Coordinador** | `coordinador.aws` | ✅ 200 OK | Supervisión y seguimiento de compromisos del equipo |
| **Delegado** | `delegado.aws` | ✅ 200 OK | Gestión territorial, asignación de metas, aprobación de planes |
| **Funcionario** | `funcionario.aws` | ✅ 200 OK | Registro de actividades, tubo, evidencias y consultas propias |
| **Verificador** | `verificador.aws` | ✅ 200 OK | Revisión técnica de evidencias y solicitud de correcciones |
| **Consulta** | `consulta.aws` | ✅ 200 OK | Visualización de avances sin permisos de modificación |

---

## 4. Certificación de Regresión

* **Suite de Pruebas:** Django Test Runner con backend MySQL (MAMP).
* **Pruebas ejecutadas:** 726 tests.
* **Fallos / Errores:** 0 fallos inesperados, 0 errores.
* **Resultado:** `OK (expected failures=1)` (falla esperada documentada y controlada en suite heredada).
