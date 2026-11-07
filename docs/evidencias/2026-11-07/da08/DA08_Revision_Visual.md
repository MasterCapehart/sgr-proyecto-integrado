# DA08 · Revisión de alineación de selectores y mensajes

**Entorno:** sistema local (`127.0.0.1:8010`), base nueva `sgr_local` con datos ficticios, rama `sgr/da08`, 07-11-2026.
**Vistas:** escritorio (zoom 100 %) y móvil (Chrome DevTools, iPhone, 393 × 852).
**Alcance:** solo ajustes CSS acotados. No se modificaron datos, requisitos ni comportamiento de guardado.

## 1. Resultado del recorrido

| N° | Pantalla | Observación | Decisión | Estado |
|---|---|---|---|---|
| 1 | Paginación de mantenedores (Ítems y metas, Delegaciones, Períodos, Configuración de metas y demás) | Los selectores "10" y "Más recientes" tenían el texto pegado al borde izquierdo y un borde negro distinto al resto de controles. | Ajuste CSS | Corregido |
| 2 | Auditoría | La etiqueta "Buscar acción, recurso o usuario" quedaba pegada a un campo sin estilo. | Ajuste CSS | Corregido |
| 3 | Clasificación de actividades | El buscador medía unos 170 px, más angosto que en las demás pantallas. | Ajuste CSS | Corregido |
| 4 | Evidencias | Encabezado de columna partido a mitad de palabra (observado en AWS el 06-11-2026). | No se repite en la versión actual | Descartado |
| 5 | Auditoría y Clasificación | Con 0 registros la tabla queda vacía, sin mensaje "No hay registros". | Comportamiento (JS), fuera del alcance de DA08 | Informado |
| 6 | Instalación nueva | No se puede crear la primera delegación desde la pantalla: la reserva de código exige una delegación activa (`code_reservation.py`). Se creó con la consola de Django. | Fuera del alcance de DA08 | Informado (`HAL-DA08-INIT`) |
| 7 | Metas ajustadas | Selectores Funcionario y Período alineados en escritorio y móvil. | Sin cambios | Correcto |

## 2. Cambio aplicado

Archivo: `frontend/assets/css/operacion.css` (al final del archivo).

```css
/* DA08: ajustes visuales acotados. Solo presentación; no cambia datos ni comportamiento. */
.local-pagination select{padding:8px 36px 8px 12px;border:1px solid #bbc3cd;border-radius:6px;background-color:#fff;color:#202a35;font:inherit}
label[for="audit-search"]{display:block;margin:20px 0 6px;font-size:12px;font-weight:bold;text-transform:uppercase;letter-spacing:.3px}
#audit-search{display:block;width:100%;max-width:520px;min-height:40px;padding:8px 10px;border:1px solid #bbc3cd;border-radius:6px;background:#fff;font:inherit}
#audit-search:focus{border-color:#AD0000;outline:2px solid #fee2e2}
.toolbar .field:has(input[id^="classification-"][name="q"]){flex:1 1 280px;max-width:420px}
input[id^="classification-"][name="q"]{width:100%;min-height:40px}
```

Los colores y medidas reutilizan los de los controles existentes (`.toolbar input`, borde `#bbc3cd`, radio 6 px, foco rojo institucional).

## 3. Evidencia

Carpeta `capturas/`: capturas **antes** y **después**, en escritorio y móvil, de paginación, Auditoría y Clasificación.

## 4. Notas para el revisor

- Tras actualizar, recargar sin caché (Ctrl + Shift + R o DevTools → Network → Disable cache): las páginas cargan `operacion.css?v=menu-planificacion-1` y el navegador puede mostrar la versión anterior.
- La regla de Clasificación usa `:has()`, soportado por los navegadores actuales (Chrome, Edge, Firefox y Safari recientes).
