# MT08 - Revisión de Formularios en Dispositivos Móviles y Estados Vacíos
**Responsable:** Matías | **Fecha:** 28/11/2026 | **Etapa:** 10. Ajustes de interfaz | **Estado:** Terminada

## 1. Propósito
Verificar la correcta visualización, usabilidad táctil y respuesta ante estados vacíos (empty states) en pantallas móviles de smartphones y tablets.

## 2. Aspectos Verificados
- **Diseño Responsive:** Los modales de diálogo (`community-dialog`, `sgr-dialog`) ocupan el 95 % del ancho en pantallas < 768px con scroll interno.
- **Campos de Formulario:** Botones con altura mínima de 44px para facilitar la interacción táctil.
- **Listados sin datos:** Mensajes claros y no técnicos (p.ej. *"No hay asignaciones para este filtro"*, *"No se encontraron vecinos registrados"*).
- **Tablas con scroll horizontal:** Envoltorio `.tablewrap` garantiza que tablas anchas no rompan la estructura ni oculten botones de acción.
