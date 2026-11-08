# DA04 · Plantillas de correo de activación y confirmación

Tres plantillas de texto plano para que el equipo las integre en el flujo de cuentas (tareas DF41 y DF42). Esta tarea **no implementa** la lógica de seguridad: solo entrega los textos.

| N° | Plantilla | Cuándo se envía | Requisito |
|---|---|---|---|
| 01 | Activación | El administrador crea la cuenta; queda pendiente de activación | RC §12, pasos 3 a 6 |
| 02 | Vencimiento | Se intenta usar un enlace de activación vencido o ya utilizado | RC §12, paso 5 (vigencia limitada) |
| 03 | Confirmación de cambio | La contraseña se cambió (activación o recuperación) | RC §12, recuperación: "se enviará una confirmación al correo registrado" |

Cada plantilla tiene dos archivos: `NN_nombre_asunto.txt` (una línea) y `NN_nombre_cuerpo.txt`.

## Campos de plantilla

Formato `{{ campo }}`, compatible con plantillas de Django (`render_to_string`).

| Campo | Contenido | Plantillas |
|---|---|---|
| `{{ nombre }}` | Nombre de pila del funcionario | 01, 02, 03 |
| `{{ usuario }}` | Nombre de usuario (no el correo completo) | 01, 02, 03 |
| `{{ enlace_activacion }}` | Enlace de un solo uso generado por el sistema | 01 |
| `{{ vigencia_texto }}` | Duración del enlace en texto, calculada desde la configuración (ej. "24 horas") | 01 |
| `{{ url_sistema }}` | Dirección de ingreso al SGR | 02 |
| `{{ url_recuperacion }}` | Dirección de la pantalla de recuperación | 03 |
| `{{ fecha_cambio }}` | Fecha y hora del cambio, formato dd-mm-aaaa hh:mm | 03 |
| `{{ nombre_institucion }}` | Ej. "Delegaciones Municipales · Municipalidad de La Serena" (configurable) | 01, 02, 03 |

## Reglas que cumplen los textos

- **No incluyen contraseñas** temporales ni definitivas. La activación usa un enlace de un solo uso (RC §12 permite "enlace o código temporal").
- **La vigencia es un parámetro** (`{{ vigencia_texto }}`): ningún texto fija una duración, porque aún no está confirmada.
- **No exponen datos personales** fuera del nombre y el usuario del destinatario: no incluyen RUT, delegación, rol ni correo.
- **No revelan si una cuenta existe** a terceros: solo se envían al correo registrado de la cuenta.
- Indican qué hacer si el correo no era esperado o si el cambio no fue reconocido.

## Pendiente de confirmar por el equipo

- Si la activación usará **enlace** o **código**. Si se usa código, reemplazar el párrafo del enlace por: `Tu código de activación es: {{ codigo }}` y mantener el aviso de un solo uso y vigencia.
- Si la plantilla 02 se enviará automáticamente o solo se mostrará como mensaje en pantalla. El texto sirve para ambos casos.
- La duración real de la vigencia (decisión del equipo o docente).
