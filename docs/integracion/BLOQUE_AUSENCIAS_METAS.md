# Ausencias y metas proporcionales — R12

Estado: implementado y verificado en local el 22/10/2026. Pendiente de despliegue.

## Reglas y alcance

Administrador y delegado con permisos pueden confirmar calendarios y registrar, corregir y anular ausencias justificadas. Un funcionario con permiso de consulta ve solo su propia información en la delegación activa. No se habilita gestión de equipo a otros perfiles aunque tengan un permiso asignado accidentalmente.

Cada calendario identifica funcionario, delegación y período. La jornada semanal distingue completa, mañana, tarde y no laboral. Los feriados/días no laborables se ingresan expresamente por fecha y deben pertenecer al período. La propuesta lunes a viernes es solo un borrador: se exige confirmación de revisión antes de guardar; no existe descuento automático sin calendario.

Ausencias: día libre, vacaciones, día administrativo, licencia u otra justificada; inicio, término, jornada completa/mañana/tarde y motivo administrativo. La creación por el gestor las autoriza. Anular conserva historial y deja de descontar. No se solicitan documentos clínicos ni diagnósticos.

El cálculo recorta ausencias al período y a las jornadas previstas; usa conjuntos de medias jornadas para no descontar solapamientos dos veces. Una ausencia por la tarde no reduce una jornada prevista solo por la mañana.

**Meta ajustada = meta original × (días previstos − ausencia computable) ÷ días previstos.**

Ejemplo verificado: 20 días previstos, 5 días de ausencia y meta original 100 → meta ajustada 75. Las metas a prorratear se seleccionan expresamente en el calendario; las demás conservan su base. Nunca se sobrescribe ConfiguracionMeta.meta_esperada. Se conserva precisión decimal para el cálculo y se muestran dos decimales, con ROUND_HALF_UP; no se convierten cantidades fraccionarias a enteros arbitrariamente.

Sin calendario: sin cálculo. Cero jornadas previstas: no evaluable, sin dividir por cero. Ausencia total: meta proporcional cero y sin exigibilidad, sin asignar incumplimiento.

## Cierre e historia

Las escrituras bloquean primero el período, después calendario y ausencia. El cierre existente usa el mismo bloqueo y conserva un snapshot de las metas ajustadas. Altas, correcciones y anulaciones quedan bloqueadas en un período cerrado o inactivo. La reapertura autorizada existente permite corregir con auditoría.

Los snapshots de disponibilidad permanecen internos: se excluyen de los parámetros del catálogo general de períodos y de sus versiones de catálogo. El resumen los devuelve únicamente después de verificar usuario/equipo y delegación autorizados. Si el período se cerró sin calendario de un funcionario, no se reconstruyen metas históricas a partir de su cargo o catálogo actual.

Los eventos de alta/corrección conservan antes/después, versión, actor y fecha. La interfaz ofrece el historial de cada ausencia.

## Interfaz e integración

Menú Seguimiento → Ausencias y calendario / Metas ajustadas. La pantalla permite seleccionar funcionario y período, confirmar calendario y ver días previstos, ausencia computable, días disponibles, factor y base original/ajustada por ítem. Se reemplazaron las muestras estáticas de las páginas de semáforo y resumen de metas por datos reales autorizados.

El semáforo muestra el estado de la meta ajustada y deja explícitamente pendiente la evaluación del desempeño. Este bloque no construye el motor de puntaje, no aplica el tope del 120 % y no inventa resultados ni umbrales oficiales.

Migración 0027: CalendarioFuncionario, AusenciaFuncionario y restricciones de unicidad/rango. Permisos nuevos: ausencias.ver, ausencias.ver_equipo, ausencias.gestionar. Se incorporan a roles existentes denominados Administrador y Delegado; Funcionario recibe solo consulta. No se importan trabajadores, calendarios, ausencias ni feriados reales.

## Revisión de fuente y verificación

Se inspeccionó, sin modificar, el libro Copia INACAP 3ER COMPAÑIAS MATRIZ SGR TRIMESTRE 2026 REV.xlsx del proyecto. No se encontró una fórmula de ajuste por ausencias/calendario en la búsqueda de ausencias, vacaciones, licencias, días hábiles y feriados. La proporcionalidad utilizada proviene de la decisión de diseño aprobada por el usuario, no se atribuye al Excel. Los porcentajes históricos del libro no se convierten en reglas nuevas de este bloque.

- 35 pruebas de ausencias y períodos correctas:20/5, medias jornadas, solapamientos, feriados, recorte, cero/total, permisos/ámbito, versiones, anulación, privacidad, cierre concurrente y snapshot histórico.
- Suite completa:525 pruebas correctas, con un fallo esperado preexistente.
- Navegador local: calendario confirmado, meta100→75, historial, anulación→100; consulta propia sin gestión, pantalla móvil sin desbordamiento horizontal.
- Revisión independiente detectó la exposición de snapshots en catálogo general; corregida y cubierta con prueba roja/verde. Sin otros defectos bloqueantes confirmados.
- Modelos/migraciones consistentes, sintaxis JS y espacios del diff comprobados.

Solo se utilizaron datos ficticios en SQLite local y la base temporal MySQL de pruebas. No hubo despliegue ni cambios a diagramas.
