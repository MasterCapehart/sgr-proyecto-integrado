# Revisión de ponderaciones por cargo y período

Alcance: consulta aritmética en Configuración de metas; no inventar pesos, aprobar pautas, modificar cálculos o cargar datos. Reutilizar Django/JS y permisos existentes. Sin migraciones.

1. Pruebas RED de endpoint GET configuraciones-metas/revision-ponderaciones/: autenticación, permisos, período inválido, suma inferior/exacta/superior100, exclusión inactiva/conciliada, alcance específico con respaldo general sin duplicar, aislamiento de cargos, lectura de cierre sin usar catálogo vigente.
2. Servicio de lectura con decimales: por alcance/cargo contar metas activas y sumar pesos de configuraciones efectivas; devolver suma/faltante/exceso y estado aritmético. 100 no significa aprobación. Período sin metas se informa explícitamente. Cierre usa snapshots disponibles; si faltan no reconstruir.
3. Panel accesible con selector de período, botón revisar y tabla con cargo/configuraciones/suma/falta/exceso/resultado. Refrescar al guardar/desactivar meta usando evento del mantenedor. Mensajes de carga/error y móvil sin desbordamiento.
4. Verificar pruebas relacionadas y UI local. Documentar resultados y pendientes. No desplegar hasta petición.

Decisión: no bloquear el guardado de filas parciales: una pauta se construye por etapas. Esta consulta no introduce un flujo de aprobación formal que aún no está definido.
