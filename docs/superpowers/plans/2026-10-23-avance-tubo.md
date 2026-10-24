# Porcentaje completado del tubo

Alcance aprobado: indicador operativo realizados/total×100, sin puntaje ni cambios a metas. Reutilizar conteos autorizados de kpis.resource_kpis, antes de paginar y después de filtros. Mostrar explícitamente que se refiere a filtros actuales. Ingresado, Pendiente y En proceso permanecen en el denominador, sin sumar nuevamente el total como estado.

1. RED: CAL-C8/10, ausencia de compromisos neutral, paginación/filtros, privacidad propia/delegación y redondeo1/3.
2. Backend: ampliar respuesta KPI de compromisos con bloque completion (total, realizados, por_completar, porcentaje y porcentaje_exacto). Decimal, sin dividir por cero, sin umbral80 ni aporte ponderado.
3. Interfaz: panel con porcentaje, n de total, barra accesible; vacío explica Sin compromisos. Reutilizar componente KPI, cambiar caché en páginas publicadas consumidoras sin tocar previews.
4. Actualizar contraste CAL-C y probar API/interfaz en local; no desplegar hasta petición. Verificar que otras tarjetas no cambian.
