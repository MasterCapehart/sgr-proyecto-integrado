# Indicadores operativos locales

Implementación en la copia `sgr-eva2-local`. No se modificó ni publicó el proyecto original.

Las tarjetas usan los colores, tipografía y espaciado del diseño municipal existente. Cuatro por pantalla, dos columnas en móvil; ocultan módulos sin permiso. Un error de conexión muestra indisponibilidad en lugar de resultados ficticios.

## Pantallas

| Pantalla | Indicadores |
|---|---|
| Inicio | Atenciones, actividades, compromisos abiertos y vencidos según permisos |
| Atenciones | Total, este mes, tipos utilizados y casos sociales distintos |
| Actividades | Total, pendientes, validadas y devueltas |
| Agenda | Total, pendientes/en proceso, realizados y vencidos |
| Evidencias / validación | Total, pendientes, aprobadas y devueltas; cantidad anulada en el detalle del total |
| Reportes | Los indicadores del recurso seleccionado y sus filtros |

Los indicadores de los listados consideran todos los resultados filtrados antes de paginar y se actualizan al consultar o guardar. Inicio muestra el historial autorizado de la delegación activa, sin un período ficticio. Las evidencias cuentan versiones (se indica en pantalla); los códigos de caso distintos no se presentan como personas únicas. Vencido significa plazo anterior a hoy y estado diferente de Realizado.

Los conteos respetan los mismos permisos de consulta, alcance propio/equipo y delegación del listado. No se incorporan ponderaciones, tasas ni cálculo de cumplimiento. El conteo mensual usa límites de fecha conscientes de la zona America/Santiago, sin depender de las tablas horarias de MySQL.

## Verificación

- 192 pruebas de backend aprobadas, incluidas ocho pruebas específicas de indicadores: scope, permisos, paginación, filtros, atenciones, evidencias, asignación de responsable y vencimientos.
- 20 comprobaciones en Chrome y Edge: tarjetas coinciden con el servidor en siete pantallas, filtro de estado, diseño móvil y manejo de error 503 sin ceros simulados.
- Revisión independiente de código sin hallazgos importantes.
- Los archivos originales conservan sus hashes. No hay remotos en la copia local.

Evidencias: [backend](pruebas-backend.log), [navegadores](pruebas-navegadores.json), [inicio](inicio.png), [móvil](movil.png).

Reproducir desde la raíz de esta copia:

```sh
backend/.venv/bin/python backend/manage.py test core --noinput
node scripts/verificar_kpis_local.cjs
```
