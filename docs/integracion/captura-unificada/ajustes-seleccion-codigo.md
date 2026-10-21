# Selección de actividad, código visible y contexto — 21/10/2026

## Cambios

- «Ítem de la meta» se presenta como **¿Qué trabajo realizaste?**. Un botón abre un cuadro de búsqueda por nombre o referencia, con actividades autorizadas para el cargo. Se conserva el identificador real del catálogo; el servidor vuelve a comprobarlo al guardar.
- El código se reserva al abrir el formulario y se muestra completo. El servidor conserva exactamente ese código al guardar y en la referencia del compromiso. Cambiar la fecha obtiene otra reserva; los códigos históricos no se modifican.
- Las reservas son eventos de auditoría, no actividades ficticias. Se vinculan a usuario, delegación, cargo y fecha; vencen a las 24 horas. El consumo ocurre en la misma transacción de alta. Cerrar o abandonar el formulario puede dejar saltos en la secuencia, sin crear trabajo inexistente.
- Reenvíos simultáneos con la misma clave y huella recuperan el registro confirmado. Usar la misma reserva para otra captura o cambiar su contexto se rechaza.
- Se corrigió el selector del encabezado: fondo integrado en el rojo institucional, texto blanco, desplegable legible, foco visible y ancho adaptable. No se renombraron delegaciones: el nombre mostrado procede de la delegación activa autorizada en la sesión. D01 · Delegación de demostración D01 es un nombre existente de demostración, no un nombre real deducido del Excel.

## API y compatibilidad

`POST /api/captura/reservar-codigo/` recibe la fecha y devuelve código y reserva firmada. Requiere crear actividades. `POST /api/captura/` acepta `_reserva_codigo` y mantiene compatibilidad con clientes anteriores sin reserva. Una reserva ajena, vencida, consumida para otra captura o de otro contexto no puede utilizarse.

Formato adaptado a la aplicación: prefijo de cargo + fecha + R + identificador de reserva. R distingue esta secuencia de los consecutivos históricos basados en actividad. No se requiere migración de tablas.

## Validación

Pruebas específicas de reserva sin crear actividad, códigos distintos por formulario, código visible igual al guardado, contexto ajeno/fecha cambiada, error que no consume reserva, idempotencia y tres solicitudes simultáneas con una sola actividad. Navegador QA: buscador sin coincidencias y selección real, código visible, creación general y social con evidencia, detalle y vista móvil sin desbordamiento. Revisión independiente del caso concurrente, corregido antes de publicación.
