# Revisión de ponderaciones por cargo y período

Implementado y desplegado en AWS el23/10/2026, versión `56d64c7ae960076c11df57264ab35ace725f106a`. Consulta aritmética; no modifica metas, ponderaciones, usuarios, períodos ni cálculos.

## Uso

Administración → Configuración de metas → Revisión de ponderaciones. Seleccionar período y revisar cargo, cantidad de metas efectivas, suma, faltante, exceso y resultado. Las cifras se conservan en decimal exacto para la comparación con100.

Resultados: Sin metas, Incompleta, Suma100 %, Excede100 % o Valores inválidos. Sumar100 % no acredita que estén todos los componentes ni constituye aprobación de la pauta. No hay una excepción formal ni un flujo de aprobación definidos en este incremento.

En períodos abiertos se reutiliza la selección de metas: específica activa del cargo; si no existe, general disponible para ese cargo. Se excluyen metas inactivas/conciliadas e ítems inactivos o no disponibles. No se cuentan las metas de otros cargos ni se duplican respaldo general y específica. General muestra las metas aplicables a una persona sin cargo.

En períodos cerrados se suman los alcances guardados en los parámetros del cierre. No se reconstruyen asociaciones históricas ítem/cargo ni se aplica la pertenencia actual para distribuir metas generales. Si faltan parámetros, se informa sin reconstrucción. Los cierres antiguos sin etiqueta de cargo se muestran como alcance histórico sin etiqueta.

No se bloquea guardar una pauta parcial, porque se completa por etapas. La consulta se actualiza al guardar/desactivar una meta y permite revisar de nuevo. No se normalizan pesos ni se asigna automáticamente el porcentaje que falta. Se corrigió el texto antiguo que afirmaba que no existía motor de cálculo.

## Permisos y fuentes

API GET `/api/configuraciones-metas/revision-ponderaciones/?periodo=ID`, con autenticación y permiso `configuraciones-metas.ver`, igual que el catálogo. Sin datos de personas ni ausencias. Respuesta privada sin caché. Métodos de escritura no admitidos.

Base: guía académica RN-001 y §13.1 (suma100 % salvo excepción formal). Ver [contraste de fórmulas](../calculos-fuentes/README.md). Este panel no aprueba automáticamente las49 metas cuantitativas ni completa los componentes de tubo, emergencias, felicitaciones, penalizaciones o metas territoriales.

## Verificación

8 pruebas específicas: suma exacta y diferencias de0,01, respaldo general, exclusión, alcance por cargo, cierre, autenticación, permisos, período inválido y método no permitido. Pruebas relacionadas de metas/cargo, fórmulas, períodos, ausencias y colectivos: **68 correctas**. [Salida](pruebas-relacionadas.txt).

Interfaz Edge local: tabla y advertencia, selector, limpieza al quitar selección, escritorio y móvil sin desbordamiento de página, sin errores de JavaScript. Se usó exclusivamente una base SQLite local con datos ficticios. No se escribieron datos en AWS. Sin migraciones.

Revisión independiente: corregidos el identificador Unicode inválido y los parámetros de cierre con formato no interpretable. Ambos defectos se reprodujeron antes de corregirlos y quedaron cubiertos por las pruebas.

## Comprobación en AWS

[Resultados de la verificación](aws-verificacion.json). Las49 metas del período histórico julio–septiembre2026 coinciden por cantidad y suma con el paquete del Excel: Apoyo95 %, Coordinación80 %, Gestores85 %, Territoriales70 % y Planificación45 %. Son los subtotales de los componentes cuantitativos cargados, no una pauta integral aprobada. No se rellenaron los porcentajes faltantes.

Salud/versión y servicios correctos, acceso anónimo bloqueado, período inválido responde400, interfaz móvil sin desbordamientos ni errores JavaScript. Las metas y las cuentas consultadas se conservaron exactamente sin cambios. Se usó el flujo de autenticación normal, sin altas ni ediciones de negocio.
