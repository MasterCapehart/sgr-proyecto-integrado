# Despliegue inicial AWS Academy

Objetivo: publicar el SGR desde su carpeta original sin afectar la instalación local.
Arquitectura inicial: EC2 con Nginx y Gunicorn, RDS MySQL privado, S3 privado y HTTPS con un endpoint permitido en Learner Lab. Sin dominio propio: comprobar CloudFront antes de elegir la terminación TLS.
Fuente: guía de despliegue solicitada por el usuario y requisitos A4 y B17 del PDF de evaluación.

## Restricciones
- Trabajar dentro de sgr-proyecto-integrado, en rama feat/despliegue-aws.
- No abrir solicitudes de revisión ni integrar en main sin instrucción.
- No publicar secretos; usar configuración AWS local y rol de instancia existente.
- Preservar la base local y sus registros. Datos AWS ficticios y aislados.
- No afirmar cumplimiento de cálculos ni períodos pendientes.
- Respetar límites de servicios y permisos de Learner Lab.

## Etapas
- [ ] Inventariar recursos y permisos de consulta; elegir región y HTTPS sin dominio.
- [ ] Probar configuración de producción, almacenamiento privado y errores de descarga.
- [ ] Añadir settings_production, dependencias y archivos operativos reproducibles.
- [ ] Crear recursos propios etiquetados; reutilizar solo infraestructura autorizada.
- [ ] Preparar servidor, base y perfiles de demostración; SMTP privado.
- [ ] Publicar endpoint HTTPS y verificar flujos, persistencia y permisos.
- [ ] Documentar recursos, versión, respaldo y pendientes reales.

## Verificación
Ejecutar pruebas del backend aisladas; validar configuración sin AWS cuando sea posible; comprobar rutas y respuestas en el entorno remoto. Un servicio denegado se documenta sin eludir permisos. Registrar decisiones y resultados en deploy/aws y estado privado en .integracion/aws-deploy.

## Decisiones comprobadas
- CloudFront devuelve AccessDenied en Learner Lab. No se intenta eludir la restricción.
- Sin dominio propio: probar certificado IP de Let’s Encrypt con Certbot 5.4 o superior, perfil shortlived y renovación automática. Fuente oficial https://letsencrypt.org/2026/03/11/shorter-certs-certbot
- Esperar renovación de credenciales AWS antes de crear recursos; avanzar mientras tanto con el código.
