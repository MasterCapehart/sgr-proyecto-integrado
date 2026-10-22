DOMAIN_PERMISSIONS = [f'{r}.{a}' for r in ['actividades','evidencias','compromisos'] for a in ['ver','crear','editar','exportar','ver_equipo','editar_equipo']] + ['evidencias.revisar','conversaciones.crear','reportes.ver','evidencias.anular','compromisos.reabrir','alertas.ver','alertas.revisar','gobierno.ver','gobierno.configurar']

DOMAIN_PERMISSIONS += ['reclamos.'+a for a in ['ver','crear','editar','exportar','ver_equipo','editar_equipo']]

DOMAIN_PERMISSIONS += ['periodos.cerrar','periodos.reabrir']

DOMAIN_PERMISSIONS += [f'{r}.{a}' for r in ['vecinos','organizaciones','pertenencias'] for a in ['ver','crear','editar','desactivar']]
DOMAIN_PERMISSIONS += ['hitos.'+a for a in ['ver','ver_equipo','crear','editar','asignar','avanzar']]
