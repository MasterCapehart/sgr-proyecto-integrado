# Despliegue AWS personal y evidencias de instalación

## Versión y entorno comprobados

Última verificación registrada: 21 de octubre de 2026.

- URL: https://54.236.112.203/pages/login.html
- Salud: https://54.236.112.203/api/health/
- Versión: https://54.236.112.203/api/version/
- Código evaluado: `1387aa8a976d802588fcb1e173b3bf50db1664f6`.
- Región: `us-east-1`.
- Perfil administrativo local: `sgr-personal`; laboratorio separado: `sgr-aws`.

La cuenta personal contiene una copia independiente de la aplicación del laboratorio. No se sincronizan automáticamente el código ni los datos entre ambos entornos.

Último incremento: [vecinos, organizaciones y pertenencias](../../integracion/BLOQUE_VECINOS_ORGANIZACIONES.md), migración0022 aplicada y permisos comprobados en AWS. Las evidencias de instalación que siguen corresponden al traslado inicial del18/10/2026.

## Componentes

| Componente | Configuración comprobada |
|---|---|
| Aplicación | EC2 Ubuntu 24.04, t3.small, Nginx y Gunicorn; usuario de servicio sgr |
| Acceso web | IP reservada propia, HTTPS y certificado renovable automáticamente |
| Base | RDS MySQL 8.4.11, db.t3.micro, 20 GB; base sgr_prueba, sin acceso público |
| Archivos | Bucket S3 privado, cifrado y versionado; rol exclusivo del servidor |
| Red | VPC propia; MySQL accesible desde el grupo de seguridad de la aplicación |
| Persistencia | Discos cifrados, respaldos RDS con siete días de retención y protección contra borrado |
| Arranque | Servicios sgr y nginx habilitados; reinicio comprobado |

El servidor usa credenciales temporales de su rol EC2 para S3 y un usuario MySQL de aplicación. No utiliza claves administrativas AWS estáticas en el código. El remitente SMTP está configurado privadamente; se comprobó autenticación sin enviar un correo durante la copia.

## Instalación realizada y evidencia

Se creó infraestructura nueva y se extrajo la aplicación desplegada del laboratorio; no se utilizó un clon limpio de Git como fuente en ese procedimiento.

1. Se instalaron Python, bibliotecas MySQL, Nginx, cliente MySQL, SSM y Certbot.
2. Se creó el entorno virtual y se instalaron las dependencias de producción. [Salida de instalación](evidencias/instalar-destino.txt).
3. Se generó un respaldo SQL del origen y se importó en una base vacía del destino; no se sobrescribió la base del laboratorio.
4. Se compararon conteos y CHECKSUM TABLE de las 39 tablas antes de las pruebas web: todos coincidieron. [Verificación de restauración](evidencias/database-verification.json).
5. Se configuraron variables privadas nuevas para IP, RDS, S3 y SECRET_KEY. Se mantuvieron los usuarios y sus contraseñas; las sesiones previas requieren un nuevo inicio de sesión.
6. Se instaló el certificado y se habilitaron los servicios. [Registro inicial](evidencias/configurar-destino.txt): la petición inmediata obtuvo 502 durante el arranque. [Comprobación final](evidencias/final-destino.txt): servicios activos, migraciones sin pendientes, salud y versión correctas.
7. Se verificaron [49 comprobaciones web](evidencias/web-verification.json), los [objetos S3](evidencias/s3-copy-manifest.json), el [reinicio](evidencias/reboot-verification.json) y la [simulación de renovación HTTPS](evidencias/renovacion-certificado.txt).

Estos archivos no incluyen contraseñas, cookies, tokens, SQL con datos ni la configuración privada del servidor.

## Instrucciones para instalar o actualizar desde el repositorio

Este procedimiento documentado queda pendiente de un ensayo completo desde clon limpio y de reversión de versión. Debe ejecutarlo un operador autorizado sobre un entorno identificado, con respaldo previo y durante una ventana de mantenimiento.

1. Confirmar cuenta, región, servidor y base de destino. Revisar el costo antes de crear recursos. No ejecutar `deploy/aws/provision.py` sin adaptarlo y revisarlo: el procedimiento original utiliza `LabInstanceProfile`, que no pertenece a la cuenta personal.
2. Preparar una copia de la versión elegida del repositorio. Para reproducir la versión evaluada, usar el SHA indicado arriba y no asumir que `main` coincide con el servidor.
3. Seguir [backend/README.md](../../../backend/README.md) para requisitos y dependencias. Para AWS, instalar `backend/requirements-production.txt` y usar `config.settings_production`.
4. Configurar privadamente `/etc/sgr/sgr.env`, tomando como referencia [deploy/aws/.env.example](../../../deploy/aws/.env.example). Ajustar DB_NAME, DB_HOST, DB_USER, DB_PASSWORD, RDS_CA_PATH, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, SECRET_KEY, AWS_REGION, AWS_STORAGE_BUCKET_NAME, SMTP y GIT_SHA. No subir ese archivo. Protegerlo como root:sgr, modo 640. No sustituirlo con la configuración local de MAMP.
5. Respaldar MySQL y los archivos afectados. Revisar `migrate --plan` con la identidad de despliegue; aplicar las migraciones autorizadas. El usuario normal sgr_app no tiene permisos para modificar el esquema. No usar `--fake` para omitir diferencias sin investigarlas.
6. Ejecutar `check --deploy`, `migrate --check` y `collectstatic --noinput` con el entorno correcto. Las opciones HSTS de subdominios y preload no se activan indiscriminadamente para una IP.
7. Instalar [sgr.service](../../../deploy/aws/sgr.service) y [sgr-manage](../../../deploy/aws/sgr-manage), ajustar el [Nginx](../../../deploy/aws/nginx-https.conf.template) a la dirección y al certificado propios. Nginx expone 80/443; Gunicorn escucha solo en loopback.
8. Validar Nginx antes de recargarlo, habilitar servicios y renovación. Consultar HTTPS, salud y versión, e ingresar con una cuenta autorizada. Comprobar registros y archivos persistidos.
9. Para futuras actualizaciones, mantener la versión anterior y su respaldo. Si existe una migración incompatible, volver únicamente al código anterior puede ser insuficiente: definir cómo restaurar o conciliar datos antes de ejecutar una reversión. No ensayar una restauración destructiva en la base operativa sin autorización específica.

## Recuperación acreditada y límites

- Laboratorio: [restauración SQL aislada](../../../.archivo/interno/2026-10-17/evidencias/rendimiento-aws/restore-resultado.json), 39 tablas con conteos y checksums coincidentes; la base operativa no fue reemplazada.
- Cuenta personal: restauración inicial de un respaldo posterior, 39 tablas y 11.201 filas, más recuperación automática tras reiniciar el servidor. Las sesiones y auditorías posteriores generan cambios normales respecto del respaldo.
- No se ensayó una recuperación desde snapshot RDS ante desastre ni un rollback completo de código y esquema en la cuenta personal.
- Los SQL, las contraseñas y el estado privado de infraestructura se mantienen fuera de Git. No publicar esos archivos para aportar evidencia: utilizar resultados sanitizados y sus identificadores de versión.

La carga y el estrés disponibles corresponden al laboratorio; no son resultados de rendimiento medidos en esta cuenta personal. Ver [verificación de la entrega](../README.md).
