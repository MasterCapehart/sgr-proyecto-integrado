# Avance funcional local — segunda evaluación SGR

Trabajo realizado exclusivamente en `sgr-eva2-local`. El original y GitHub no se actualizan.

## Abrir y probar

1. Ejecutar `INICIAR_LOCAL.command` en la raíz de esta copia.
2. Abrir http://127.0.0.1:8010/pages/login.html.
3. Consultar las cuentas ficticias en `.aislamiento/cuentas-locales.json` (archivo privado).
   Administrador: seis mantenedores. Operador: registrar y consultar atenciones propias del contexto.
   Consulta: solo lectura de catálogos autorizados. Son perfiles de prueba, no una aprobación
   de la matriz institucional de permisos.
4. Solicitar una recuperación con el correo ficticio de la cuenta.
5. Ejecutar `backend/.venv/bin/python scripts/leer_correo_local.py` para leer el mensaje.
   No existe envío SMTP a Internet en esta versión.
6. Al terminar, ejecutar `DETENER_LOCAL.command`.

## Operativo con persistencia real

- Login por usuario o correo, contraseña Django, logout, sesión y CSRF.
- Recuperación: respuesta genérica; código cifrado; 10 minutos; cinco intentos;
  reenvío mínimo de 60 segundos; cambio confirmado e invalidación del código.
- Permisos por operación. Delegaciones autorizadas explícitas y contexto en sesión.
  Cambiar contexto conserva la delegación principal de la cuenta.
- Delegaciones, roles, usuarios, ítems, tipos y subatenciones: crear, consultar, listar,
  editar y activar/desactivar. Validaciones y protección de relaciones en servidor.
- Búsqueda parcial, estado, ordenamiento permitido, paginación y total.
- XLSX real de todas las páginas del filtro autorizado; sin contraseñas ni tokens.
  Las cadenas se escriben como texto para evitar fórmulas inyectadas.
- Atención con tipo/subatención compatibles y activos, autor y origen del servidor,
  folio único, historial local, prevención de doble envío por clave de operación.
- Caso social: misma identificación textual normalizada, máximo tres gestiones;
  no se presenta como padrón completo de personas o identidad legal verificada.
- SweetAlert2 de éxito después de guardar y de errores sin perder el formulario.
  Consulta en solo lectura; cancelaciones sin cambios; navegación por permisos.
- Logotipo oficial descargado íntegro y rojo heráldico `#C41230`.
  Fuente y huella del activo: `identidad-institucional.json`.

## Evidencias reales

- `pruebas-backend.log`: resultado de la suite Django, incluidas pruebas anteriores adaptadas.
- `resultados-funcionales.json` y `matriz-pruebas.csv`: registro individual automatizado.
- `pruebas-interfaz.json`: apertura, registro y tamaño móvil.
- `pruebas-flujos-ui.json`: seis CRUD desde Edge, XLSX, cancelación y duplicado.
- `pruebas-recuperacion-ui.json`: recuperación completa y acceso con nueva clave.
- `capturas/`: imágenes de la interfaz local.
- `aislamiento-final.json`: contraste de huellas del original y ausencia de remotos.

Las pruebas heredadas se conservaron y actualizaron: ahora autentican sus fixtures,
leen XLSX con un lector real y esperan rechazo de campos de autor manipulados.
La prueba de doble clic utiliza una clave estable; se eliminó la suposición de que dos
solicitudes parecidas en pocos segundos necesariamente son la misma visita.
El caso de tres gestiones utiliza una misma persona, en vez de tres personas diferentes.
No se cambió una aserción para aceptar una violación de permisos o pérdida de integridad.

## Documentos y diagramas

- `../uml/referencia-previa/`: copia de los UML existentes. No acredita implementación de
  los módulos futuros que esos diagramas describen.
- `../uml/incremento-local/`: vistas técnicas editables `.drawio`, vistas `.svg` y diccionario
  generado a partir de los modelos Django de este incremento. Son vistas parciales por módulo,
  no sustituyen silenciosamente el modelo conceptual completo de 43 tablas.
- `Requisitos_Segunda_Evaluacion.pdf`: fuente entregada por el usuario.
- `Plan_Tareas_Origen.xlsx` y `tareas-fuente.json`: plan original sin alterar sus estados.
- `seguimiento-plan-original.csv`: conserva sin aprobar los casos completos del plan original.
  Una prueba automatizada concreta aprobada no equivale a aprobar todas sus variantes ni
  a certificar los casos de AWS o módulos que todavía no forman parte del incremento.

## Excluido o pendiente de aceptación externa

- T25, T26, T27: AWS, despliegue, correo externo y estrés en AWS.
- Push, PR, merge, tags remotos y actualización de GitHub.
- Aprobación humana de roles, diseño, diagramas y aceptación funcional del equipo.
- Certificación municipal de uso gráfico; se aplicaron activos y paleta publicados,
  sin afirmar que Arial sea una tipografía oficial certificada.
- Estrés del entorno desplegado y sus métricas no se sustituyen por dos peticiones locales.
- Agenda, evidencias, indicadores, tableros y demás módulos de futuras entregas no se
  implementaron ni se marcaron como operativos por conservar sus mockups.

## Repetir la verificación

Desde la raíz de la copia:

```bash
backend/.venv/bin/python backend/manage.py check
backend/.venv/bin/python backend/manage.py test core --testrunner=core.evidence.EvidenceRunner --noinput
node scripts/verificar_ui.cjs
node scripts/verificar_flujos_ui.cjs
node scripts/verificar_recuperacion_ui.cjs
backend/.venv/bin/python scripts/comprobar_aislamiento.py
```

Las pruebas Django crean y eliminan `test_sgr_eva2_local`; no usan la base original.
Las pruebas de navegador requieren el servicio local y Microsoft Edge; crean datos ficticios
solo en la copia. El recorrido de recuperación actualiza la clave ficticia de Operador y
su archivo privado de cuentas. Para repetirlo inmediatamente debe respetarse la espera de
60 segundos del servidor. No borrar restricciones para forzar una prueba aprobada.
