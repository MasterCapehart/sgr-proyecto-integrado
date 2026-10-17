# Backend SGR

## Preparación

Requiere Python 3.12 o posterior compatible con Django 5.2, MySQL 8 y las bibliotecas de compilación de mysqlclient correspondientes al equipo.

Desde la raíz del repositorio:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Si ya existe `.env`, conservarlo: no ejecutar la copia de plantilla sobre sus datos. Completar SECRET_KEY, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST y DB_PORT con la configuración propia. No publicar `.env`.

## Base de datos

Crear una base MySQL vacía con codificación utf8mb4 y un usuario autorizado. Las migraciones Django son la fuente del esquema vigente. Los SQL históricos de docs son referencia; no mezclarlos indiscriminadamente con las migraciones.

Antes de actualizar una base existente, hacer un respaldo de sus datos. Revisar el plan y ejecutar:

```bash
python manage.py check
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8010
```

Abrir http://127.0.0.1:8010/pages/login.html. Usar la cuenta creada, sin credenciales compartidas en Git. El superusuario permite configurar roles, delegaciones y usuarios desde las pantallas. El panel técnico /admin/ es de consulta para evitar omitir auditoría y control de versión. Configurar permisos y delegaciones autorizadas antes de crear cuentas operativas.

Esta entrega conserva la migración remota `0007_usuario_recuperacion_seguridad` y encadena a continuación la migración ampliada de la copia. No borrar migraciones ni usar --fake para resolver diferencias sin revisar el esquema real.

## Recuperación de contraseña

El correo destino es el registrado en cada usuario. `SGR_EMAIL_MODE=local` guarda mensajes en el buzón privado configurado por el proyecto; no envía mensajes reales. Para Gmail establecer `SGR_EMAIL_MODE=smtp` y completar EMAIL_HOST_USER, EMAIL_HOST_PASSWORD (contraseña de aplicación), DEFAULT_FROM_EMAIL y las variables TLS de .env.example. Cada instalación configura su propio remitente; nunca se publica la contraseña.

## Verificación

```bash
python manage.py test core --noinput
python manage.py makemigrations --check --dry-run
```

Las pruebas crean una base con prefijo test_; el usuario MySQL debe tener autorización sobre esa base temporal. Nunca ejecutar pruebas manuales destructivas en datos reales.

Las clases tests_legacy_crud, tests_acceso_permisos y tests_roles_usuarios conservan las regresiones del contrato anterior y usan exclusivamente URLs de prueba. No acreditan el contrato de producción actual. Las demás suites verifican la API integrada, incluidos aislamiento, permisos y flujos operativos. Existe una prueba marcada como fallo esperado heredada; no equivale a cobertura satisfactoria de esa condición.

El servidor de desarrollo y el servicio estático incluidos son para uso local. El despliegue de producción se configura posteriormente.
