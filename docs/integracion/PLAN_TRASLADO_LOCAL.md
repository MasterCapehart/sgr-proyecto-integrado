# Integración del avance de la copia local

## Objetivo
Trasladar el avance funcional de sgr-eva2-local al repositorio original actualizado, conservando los commits humanos existentes, las configuraciones privadas y los datos originales. Publicar una rama con commits por módulo, sin abrir una solicitud de revisión ni integrar en main, según la instrucción actual del usuario.

## Base
- Original actualizado a origin/main: 358a1ed.
- Respaldo privado externo: ../respaldos_integracion/20261017_122126.
- Rama de integración: feat/integracion-avance-local.
- Los cambios remotos de roles, usuarios, permisos y recuperación se conservan en el historial. Sus pruebas se revisan contra los nuevos contratos; no se borran para conseguir un resultado favorable.

## Lotes de commits
1. INT-00: plan, exclusiones de secretos y registro de integración.
2. INT-01: modelos y migraciones compatibles con la migración remota de recuperación.
3. INT-02: configuración portable, correo, API de acceso, catálogos y atención.
4. INT-03: operación territorial, evidencias, compromisos, matriz, indicadores e históricos.
5. INT-04: pantallas, diseño institucional y componentes del frontend.
6. INT-05: regresiones, pruebas funcionales y documentación de instalación y contratos.
7. INT-06: evidencias y estado real de pendientes.

## Verificación
- Comparar inventario de archivos y revisar diferencias con main actualizado.
- Construir migraciones sin modificar las existentes de los compañeros.
- Ejecutar las pruebas de la aplicación y comprobar deriva de modelos.
- Verificar contra base temporal; no ejecutar cambios destructivos en la base original.
- Auditar secretos, identidad y mensajes antes de cada commit.
- Publicar únicamente la rama, sin abrir pull request. No certificar AWS, cálculos ni escenarios no ejecutados.

## Pendientes conocidos
DEF-META-001: configuraciones de metas duplicadas. PAR-01/PAR-05: períodos con fechas/cierre no implementados. Trasladar el proyecto no subsana estas incidencias.
