# Despliegue SGR en AWS Academy

Esta carpeta prepara el despliegue; no certifica que los recursos ya estén creados.
La instalación local conserva su configuración. AWS usa config.settings_production.

## Arquitectura acordada para el laboratorio

- EC2 Ubuntu 24.04 x86_64, Nginx y Gunicorn.
- RDS MySQL privado, accesible solamente desde el grupo de EC2.
- Bucket S3 privado, cifrado y versionado, para archivos de evidencias.
- LabInstanceProfile existente, sin editar los roles administrados del laboratorio.
- IP pública reservada y certificado IP de Let's Encrypt con renovación automática.

La consulta de CloudFront fue denegada por el laboratorio. No se utiliza ese servicio ni se intenta eludir sus restricciones. Certbot 5.4 o posterior permite certonly con --ip-address y el perfil shortlived. El certificado dura seis días y se debe renovar y recargar Nginx automáticamente. Referencia: https://letsencrypt.org/2026/03/11/shorter-certs-certbot

## Preparación

1. Actualizar las credenciales temporales en el perfil privado sgr-aws, fuera del repositorio.
2. Instalar backend/requirements-production.txt en un entorno Python compatible.
3. Ejecutar las pruebas y revisar recursos, región y costos antes de aprovisionar.
4. Crear recursos con `python deploy/aws/provision.py --profile sgr-aws --region us-east-1 --apply` desde la raíz del repositorio.

El comando crea recursos con costo y conserva estado y contraseñas en .integracion/aws-deploy/state.json, excluido de Git. También guarda una clave EC2 privada con permiso 600. Nunca publicar el estado ni la clave. No volver a ejecutar con otro archivo de estado para crear duplicados. Si se interrumpe una operación, inspeccionar el estado remoto antes de continuar: algunos pasos de configuración de red pueden necesitar conciliación manual.

## Configuración de aplicación

Copiar el contenido de .env.example a /etc/sgr/sgr.env, fuera del directorio público. Sustituir todos los marcadores, configurar chmod 640 y propietario root:sgr. No copiar los datos de conexión de MAMP. El almacenamiento usa las credenciales temporales del rol EC2; no guardar claves AWS estáticas.

Crear la base con la identidad de despliegue, aplicar migraciones y crear el usuario sgr_app con SELECT, INSERT, UPDATE y DELETE sobre sgr_prueba.*. La ejecución normal no debe utilizar la cuenta maestra. Los archivos sgr.service y sgr-manage corresponden a /srv/sgr/app. Nginx sirve el frontend y los estáticos, y pasa /api/ y /admin/ a loopback 8000.

El certificado se obtiene con webroot en /var/lib/letsencrypt. El Nginx de arranque debe permitir /.well-known/acme-challenge/. Una vez emitido el certificado IP confiable, usar nginx-https.conf.template sustituyendo PUBLIC_IP; no publicar login sobre HTTP ni instalar un certificado de staging como válido.

## Verificación

- `manage.py check --deploy` con el entorno de producción, revisando cada advertencia.
- `manage.py migrate --check` sin migraciones pendientes.
- GET /api/version/ debe mostrar GIT_SHA (hash de 40 caracteres) y ningún secreto.
- GET /api/health/ debe responder ok cuando MySQL esté disponible; es distinto de /healthz de Nginx.
- Login, recuperación, CRUD, exportación, atención, permisos y descarga autorizada desde la URL HTTPS.
- RDS sin acceso público; bucket y objetos privados; puertos 8000 y 3306 no públicos.
- Renovación Certbot probada, servicios habilitados y persistencia después de reinicio.

Los fallos conocidos de metas duplicadas y períodos no son corregidos por el despliegue. La cuenta de evaluación, los datos ficticios, el correo y la aceptación AWS se documentan cuando estén configurados y comprobados.
