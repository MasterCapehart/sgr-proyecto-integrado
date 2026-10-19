# Incidencias y límites observados

## REN-EXP-01 — Exportación de 10.000 atenciones no completada

Prioridad alta para la entrega. En AWS, una cuenta con permiso de exportar solicitó `/api/atenciones/export/?search=REN50d1c897` mientras diez usuarios realizaban operaciones mixtas sobre su propia delegación.

El cliente no obtuvo el archivo antes de su timeout de 15 segundos. Independientemente de ese límite de cliente, el registro de Gunicorn confirmó `WORKER TIMEOUT` y error HTTP 500 al atender esa misma exportación, aproximadamente al alcanzar los 90 segundos de configuración del worker. No hay archivo Excel completo que permita aprobar REN-03. Se conserva el extracto del registro en `servidor-incidencias.txt`.

Durante ese escalón, 11 de 97 solicitudes fallaron desde el cliente: exportación, consulta, registro, tablero y reenvío. El código 0 de la traza significa que no se recibió un estado HTTP, no un código enviado por Django. Los tipos TimeoutError/URLError y las latencias están en la traza. La coincidencia temporal identifica impacto durante la exportación; no prueba por sí sola la causa interna de cada fallo.

Corrección pendiente: investigar el costo real de las consultas y serialización de exportación, optimizar la obtención de relaciones y la generación del archivo, y repetir el conjunto exportación + usuarios concurrentes. Aumentar únicamente los timeouts no acredita que se haya resuelto el problema. No se modificó código productivo para ocultar el fallo.

## REN-HARNESS-01 — Etiqueta imprecisa del ejecutor

El script ejecutado registró «Idempotencia incorrecta VU 2» cuando un reenvío no obtuvo respuesta antes del timeout. Esa etiqueta NO demuestra una clave duplicada: la condición del script agrupa una respuesta ausente y una respuesta con ID distinto. Se detuvo conservadoramente el aumento de carga, aproximadamente a los 35 segundos de la etapa de diez usuarios, antes de completar el minuto del criterio de tasa de errores.

La revisión posterior directa de MySQL encontró 67 escrituras confirmadas, las mismas 67 filas, ningún ID distinto o ausente, ninguna clave duplicada y ningún autor/delegación incorrectos. Por ello esta ejecución no demuestra corrupción por idempotencia. Se conserva el script exactamente ejecutado para auditar esa limitación; la clasificación del informe usa las evidencias de base de datos y no esa etiqueta automática.

## Casos que esta ejecución no acredita

- Diez minutos completos con diez usuarios: la etapa se interrumpió.
- Escalones de veinte y cincuenta usuarios: se omitieron después de la degradación para evitar más afectación.
- Capacidad máxima del sistema: solo se observó degradación bajo el escenario combinado ensayado.
- Validación concurrente de evidencias al 10 %: se sustituyó por reenvíos idempotentes. El flujo funcional posterior se registra por separado.
- Caché fría: no se vaciaron cachés. Solo primera consulta observada y repeticiones.
- CloudWatch, CPU/créditos de RDS o conexiones de pico: solo se capturaron CPU y memoria de EC2 desde el sistema invitado.
- Disponibilidad mensual y RPO/RTO contractuales: la ventana corta no permite acreditarlos.
- Cálculos de metas/semáforos: siguen fuera de este alcance, conforme a la exclusión anterior del equipo.
