# Acercamiento a las planillas actuales

Diseño aprobado en conversación: ampliar gestiones y agenda, separar cargo de rol, registrar derivaciones, presentar expediente social de hasta tres gestiones y evidencia visible. Fuente visual: las diez imágenes de ../Galería-20260831. Solo sgr-eva2-local; sin datos masivos, GitHub, AWS ni motor de cálculo.

- [x] Pruebas RED: cargos e ítems por cargo; fecha de solicitud; derivación histórica; evidencia en actividad; campos sociales y expediente limitado por delegación.
- [x] Modelos y migración aditiva: Cargo, usuario.cargo, ítems.cargos, actividad.cargo y derivación, compromiso.fecha_solicitud; campos de visita/informe/beneficio en atención. Sin inventar fechas históricas.
- [x] API: validación, permisos existentes, versión y auditoría; catálogo por cargo; expediente social solo con atenciones autorizadas; XLSX con encabezados legibles.
- [x] Interfaz: catálogo de cargos, asignación en usuario/ítem, columnas de Excel, vínculos de agenda, evidencia y derivación; expediente social; filtros y columnas fijas.
- [x] Verificación: suite completa, recorrido real de navegador, revisión visual móvil/escritorio y aislamiento.

Decisiones: rol controla permisos; cargo describe función/área. No se asignan cargos a usuarios por inferencia. Los ítems sin cargos configurados son generales. Los registros históricos sin nuevo antecedente muestran «No registrado». No se interpreta la columna «Unidad» de las fotografías como cantidad ni como unidad organizacional sin definición; no se implementan sus cálculos. No se importan personas ni información sensible desde las fotos.


## Resultado verificado

- Migraciones 0012 y 0013 aplicadas solo a sgr_eva2_local; sin cambios de modelo pendientes.
- 171 pruebas de backend aprobadas en MySQL de prueba. Registro: .revision-local/excel-suite-final.log.
- Recorrido nuevo en Chrome y Edge aprobado: cargo/ítem, agenda, actividad, filtro de columna,
  derivación, evidencia, XLSX y tres etapas sociales desde la interfaz. Capturas revisadas.
- Regresión de los seis mantenedores y pruebas de perfiles/móvil aprobadas.
- XLSX abierto con openpyxl: títulos legibles, paneles C5, filtros y registros persistidos.
- Revisión independiente: dos hallazgos corregidos con RED→GREEN (ítems exclusivos para cuenta
  sin cargo y reintentos inválidos de atención). También se corrigieron JSON inválido, contacto
  informado en etapa posterior, estado desconocido histórico, filtro de nombre completo y día local.
- Original sin diferencias según hashes y copia sin remotos. Sin commits, publicación ni datos masivos.
- Configuración real de cargos y asignaciones queda disponible al administrador; no se infiere
  el cargo desde el rol ni se cargan personas de las fotografías.
