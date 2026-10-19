# Mockups SGR — actualización 2026-10-05

Abrir `index.html` para recorrer las 20 pantallas. Los HTML cargan recursos locales: no necesitan conexión para navegar. Las imágenes principales están en `png`; los formularios de creación y edición de los seis mantenedores, en `png/estados`.

Se conservaron los nombres M-01 a M-10 y se añadieron M-11 a M-20. Respaldo de las versiones anteriores: `respaldos/Antes_2026-10-05`.

## Referencias
- Requisitos_y_Plan_Pruebas_Segunda_Evaluacion_SGR.pdf: A1–A4, referencias C1–C6 y criterios gráficos D. La parte B es un plan de pruebas del sistema completo, no una lista de pruebas ya aprobadas.
- https://laserena.cl/conocenos/normas-graficas
- https://laserena.cl/documentos/docs/REGLAMENTO_normas_graficas_2019.pdf
- https://framework.laserena.cl/
- Escudo monocromo obtenido sin modificar de https://framework.laserena.cl/img/escudo-blanco.svg. No se redibuja, recolorea ni deforma. Su uso aquí corresponde a un prototipo académico, sin aprobación institucional.

## Cinco revisiones diferenciadas

1. **Identidad visual.** Arial, blanco/grises, acento #AD0000 del documento central, escudo oficial en proporción conservada, estados textuales además del color y jerarquía uniforme. Se revisaron las imágenes de las 20 pantallas. No equivale a una certificación municipal del área de autonomía o de la marca.
2. **Cobertura de pantallas.** Login M-01; recuperación M-11/12/13; seis mantenedores M-14…19; ingreso de atención M-20. Las diez vistas originales de operación/resultados siguen disponibles. Catálogo navegable y enlaces comprobados mediante apertura de cada pantalla.
3. **Campos y contexto.** Delegaciones: código/nombre/dirección/comuna/estado. Roles: nombre/descripción/permisos/alcance. Usuarios: nombre/correo/rol/delegaciones autorizadas/estado. Ítems: código/nombre/descripción/estado. Tipo: código/nombre/descripción/estado. Sub Atención: código/nombre/tipo/estado. Atención: solicitante/tipo/subatención/descripción/delegación/responsable/fecha. Contexto visible y campos automáticos de solo lectura. Se corrigió la elección arbitraria de rol y delegación en el login anterior.
4. **Flujos de interfaz.** Búsqueda parcial sin distinción de mayúsculas y acentos; filtros conservados al paginar; exportación XLSX de todo el conjunto filtrado; formularios crear/editar/consultar; consulta sin guardar; cancelación sin registro; relación tipo/subatención que limpia selecciones incompatibles; recuperación con código de ejemplo, reenvío, vigencia, límite de intentos, coincidencia y política de contraseña; SweetAlert2 para mensajes. Se comprobaron los flujos seleccionados en navegador. No son pruebas del servidor.
5. **Legibilidad y estados.** Sin errores JavaScript ni desbordes exteriores en las 20 vistas de escritorio. Tres vistas móviles verificadas: login, Delegaciones e ingreso de atención. Revisados formularios de seis mantenedores y sus imágenes. Estados de carga, vacío, sin coincidencias y error disponibles desde los botones de exploración. Se corrigió una regla de estilos que mostraba Guardar en consulta y la presentación de casillas de permisos.

## Correspondencia con el documento central

| Referencia | Representación | Estado |
|---|---|---|
| A1 acceso y recuperación / C1–C2 | M-01, M-11, M-12, M-13 | Pantallas y flujo local de ejemplo |
| A1 seis CRUD / C3–C5 | M-14…19 + formularios modales | Formularios navegables; operaciones simuladas |
| A1 atención / C6 | M-20 | Dependencia de catálogos y contexto representados |
| A2 template y distintivo | Cabecera y recursos compartidos | Aplicados a las vistas |
| A2 listados, búsqueda, paginador, exportación | Seis mantenedores | Interacción local; XLSX generado con datos ficticios |
| A2 estados y guardar/cancelar | Formularios, botones de exploración | Representados en el prototipo |
| A3 recuperación y SweetAlert2 | Acceso, recuperación, confirmaciones y errores | Simulación de interfaz; sin correo ni contraseña reales |
| A3 validaciones servidor/permisos/doble envío | Textos de contexto y botón bloqueado durante simulación | Requiere implementación y pruebas Backend |
| A3 estrés / A4 AWS y Git | No corresponden a una pantalla de mockup | No acreditados por esta entrega |
| B escenarios del SGR completo | M-02…10 y flujo de atención social | Vistas de apoyo, no ejecución de los 84 casos |

## Configuraciones de ejemplo

Código de recuperación de demostración: `123456`. Vigencia 10 minutos, espera de reenvío 45 segundos, límite 5 intentos y política de clave de 8 caracteres con mayúscula/minúscula/número son parámetros ilustrativos de la demostración, no nuevos requisitos oficiales. Ajustarlos a las decisiones del proyecto antes de implementar.

La cifra ponderada del ejemplo se corrigió a 57,04% para coincidir con los valores de la tabla. Todos los nombres, direcciones y correos de prueba son ficticios.

## Límites pendientes para la aplicación final

Autenticación, autorización por ruta/delegación, persistencia, integridad entre catálogos, recuperación real por correo, invalidación real de claves, control de concurrencia, cómputo de metas, cifrado/hash, carga de archivos, despliegue AWS y ejecución del plan de pruebas requieren Backend. El catálogo permite explorar perfiles/pantallas y no aplica seguridad real; el menú final deberá limitarse según permisos validados. La creación muestra validación del formulario, sin crear registros reales. La edición/desactivación cambian solo la vista local. No declarar cumplimiento funcional del 100% basándose en estas imágenes.

## Recursos y reproducción

`generate_mockups.py` genera los HTML; `render_and_verify.cjs` exporta imágenes y realiza verificaciones de interfaz con el navegador de escritorio. `Verificacion_5_Aspectos.json` registra resultados técnicos de la última ejecución.

Bibliotecas locales: SweetAlert2 11.26.3 y SheetJS/xlsx 0.18.5, obtenidas desde jsDelivr. El archivo XLSX de la prueba se guarda únicamente en `/tmp`, no se presenta como información municipal real.
