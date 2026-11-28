# MT05 - Guion de Gestión Social de Tres Gestiones y Tiempos de Atención
**Responsable:** Matías | **Fecha:** 28/11/2026 | **Etapa:** 01. Preparación documental | **Estado:** Terminada

## 1. Propósito
Validar el cálculo automatizado de los 4 intervalos de tiempo en el expediente social según las reglas del D12.

## 2. Definición de los 4 Tiempos de Gestión Social
1. **T1: Ingreso a Primera Gestión:** Días transcurridos entre la fecha de ingreso de la solicitud y la fecha de realización de la primera gestión efectiva.
2. **T2: Primera Gestión a Visita Domiciliaria:** Días transcurridos entre la primera gestión y la fecha en que se realiza la visita en terreno (`fecha_visita_realizada`).
3. **T3: Visita a Informe Social:** Días transcurridos entre la visita realizada y la emisión del informe social respectivo.
4. **T4: Ingreso a Cierre del Caso:** Días transcurridos desde el ingreso inicial hasta la resolución y cierre del expediente social.

## 3. Escenarios de Prueba

### Escenario A: Expediente Completo con Fechas Reales
- `fecha_ingreso`: 05/01/2026
- `gestion_1` (Entrevista inicial): realizada 07/01/2026 -> **T1 = 2 días**
- `gestion_2` (Visita domiciliaria): realizada 12/01/2026 -> **T2 = 5 días**
- `gestion_3` (Informe y entrega de subsidio): 16/01/2026 -> **T3 = 4 días**
- `fecha_cierre`: 16/01/2026 -> **T4 = 11 días**

### Escenario B: Expediente Incompleto o Fechas Futuras
- Caso con visita agendada a futuro o informe pendiente.
- Resultado esperado: El sistema no calcula intervalos negativos ni proyecta tiempos futuros; muestra `"No calculable"` conforme al acuerdo D12.
