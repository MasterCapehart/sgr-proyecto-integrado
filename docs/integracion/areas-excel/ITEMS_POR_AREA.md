# Ítems asociados a las áreas operativas

Fuente: `Copia INACAP 3ER COMPAÑIAS MATRIZ SGR TRIMESTRE 2026 REV.xlsx`.
SHA-256: `65d2f3616fb547491a42b7823159a08e9d8cff09db531074c47f331a682beb05`.

Se documentan 22 ítems de captura únicos y 73 asociaciones a las doce áreas. Las celdas de cada planilla y sus validaciones determinan la asociación; no se deduce de los nombres de personas. El detalle verificable está en `backend/core/data/area_items.json`.

| Área operativa | Ítems | Procedencia |
| --- | --- | --- |
| GESTOR SOCIAL 1 | ATENCIÓN SOCIAL A USUARIO PRESENCIAL; VISITA TERRENO; ENTREGA INFORME; ENTREGA BENEFICIO; EMERGENCIA; OTRAS GESTIONES | G SOC 1!C3; G SOC 1!C4; G SOC 1!C5; G SOC 1!C6; G SOC 1!C7; G SOC 1!validación J21:J510 |
| GESTOR SOCIAL 2 | ATENCIÓN SOCIAL A USUARIO PRESENCIAL; VISITA TERRENO; ENTREGA INFORME; ENTREGA BENEFICIO; EMERGENCIA; OTRAS GESTIONES | G SOC2!C3; G SOC2!C4; G SOC2!C5; G SOC2!C6; G SOC2!C7; G SOC2!validación J16:J459 |
| GESTOR SOCIAL 3 | ATENCIÓN SOCIAL A USUARIO PRESENCIAL; VISITA TERRENO; ENTREGA INFORME; ENTREGA BENEFICIO; EMERGENCIA; OTRAS GESTIONES | G SOC3!C3; G SOC3!C4; G SOC3!C5; G SOC3!C6; G SOC3!C7; G SOC3!validación J16:J459 |
| GESTOR SOCIAL 4 | ATENCIÓN SOCIAL A USUARIO PRESENCIAL; VISITA TERRENO; ENTREGA INFORME; ENTREGA BENEFICIO; EMERGENCIA; OTRAS GESTIONES | G SOC4!C3; G SOC4!C4; G SOC4!C5; G SOC4!C6; G SOC4!C7; G SOC4!validación J16:J459 |
| GESTOR SOCIAL 5 | ATENCIÓN SOCIAL A USUARIO PRESENCIAL; VISITA TERRENO; ENTREGA INFORME; ENTREGA BENEFICIO; EMERGENCIA; OTRAS GESTIONES |  G SOC5!C3;  G SOC5!C4;  G SOC5!C5;  G SOC5!C6;  G SOC5!C7;  G SOC5!validación J16:J459 |
| TERRITORIAL OO.CC. 1 | EMERGENCIA; OTRAS GESTIONES; ATENCION DE USUARIO TELEFONO Y PRESENCIAL; VISITAS, REUNIONES CON ORGANIZACIONES; CONFORMACION DE ORGANIZACIONES; GESTION DE TALLERES Y ACTIVIDADES | T OC1!B7; T OC1!validación I18:I223; T OC1!B3; T OC1!B4; T OC1!B5; T OC1!B6 |
| TERRITORIAL OO.CC. 2 | EMERGENCIA; OTRAS GESTIONES; ATENCION DE USUARIO TELEFONO Y PRESENCIAL; VISITAS, REUNIONES CON ORGANIZACIONES; CONFORMACION DE ORGANIZACIONES; GESTION DE TALLERES Y ACTIVIDADES | T OC 2!B7; T OC 2!validación I17:I224; T OC 2!B3; T OC 2!B4; T OC 2!B5; T OC 2!B6 |
| TERRITORIAL OO.CC. 3 | EMERGENCIA; OTRAS GESTIONES; ATENCION DE USUARIO TELEFONO Y PRESENCIAL; VISITAS, REUNIONES CON ORGANIZACIONES; CONFORMACION DE ORGANIZACIONES; GESTION DE TALLERES Y ACTIVIDADES | T OC 3!B7; T OC 3!validación I17:I224; T OC 3!B3; T OC 3!B4; T OC 3!B5; T OC 3!B6 |
| TERRITORIAL OO.CC. 4 | EMERGENCIA; OTRAS GESTIONES; ATENCION DE USUARIO TELEFONO Y PRESENCIAL; VISITAS, REUNIONES CON ORGANIZACIONES; CONFORMACION DE ORGANIZACIONES; GESTION DE TALLERES Y ACTIVIDADES | T OC 4!B7; T OC 4!validación I17:I224; T OC 4!B3; T OC 4!B4; T OC 4!B5; T OC 4!B6 |
| APOYO ADMINISTRATIVO | EMERGENCIA; OTRAS GESTIONES; ATENCION DE USUARIO TELEFONO Y PRESENCIAL; LLAMADAS PREVENTIVAS A USUARIOS; INFORME DE INVENTARIOS; INFORME A COMUNICACIONES | AP ADM.!B7; AP ADM.!validación H16:H962; AP ADM.!B3; AP ADM.!B4; AP ADM.!B5; AP ADM.!B6 |
| COOR SERV. COMU | EMERGENCIA; OTRAS GESTIONES; INFORMES PERSONAL; INFORME TRABAJO; OPERATIVO DELEGACION; OPERATIVO DISERCO; TALLERES; TERRENO; ATENCION REQUERIMIENTO USUARIO | COOR DISERCO!C10; COOR DISERCO!validación I20:I218; COOR DISERCO!C3; COOR DISERCO!C4; COOR DISERCO!C5; COOR DISERCO!C6; COOR DISERCO!C7; COOR DISERCO!C8; COOR DISERCO!C9 |
| PLANIFICACIÓN Y GESTIÓN | EMERGENCIA; OTRAS GESTIONES; REUNION SEMANAL CON EL EQUIPO; SOLUCION DE PROBLEMAS A USUARIOS PARTICULARES | PLAN y CON!B5; PLAN y CON!validación G16:G231; PLAN y CON!B3; PLAN y CON!B4 |

## Criterios aplicados

- «VISITAS, REUNIONES CON ORGANIZACIONES» es un solo ítem: la coma forma parte del nombre en B4 de las cuatro hojas territoriales. No se usa la coma para separar ese nombre en dos opciones.
- «OTRAS GESTIONES» está en las validaciones de captura y se asocia donde está documentada. «1RA / 2DA / 3RA GESTION» son etapas sociales y no se crean como ítems. «OTROS» sigue siendo una opción de etapa; no se convierte en un ítem adicional por inferencia.
- Se excluyen porcentajes del tubo, totales, felicitaciones y reclamos como ítems de captura de actividades. Sus módulos y cálculos no se modifican.
- La unidad utilizada es **Cantidad**, el conteo genérico representado por UNIDAD / unidad (1). El libro no especifica una unidad física distinta por cada ítem; no se inventan unidades como horas o metros.
- Se reutilizan nombres existentes inequívocos normalizando espacios y mayúsculas. Se conservan código, descripción y asociaciones anteriores. Un nombre duplicado, un área ausente/inactiva, una unidad incompatible o un código ocupado detiene toda la operación.
- Cada cambio genera versión y auditoría. Antes de ampliar vínculos se conservan referencias históricas sin captura, marcadas como observadas.
- No se asignan áreas a usuarios reales ni se cambian roles. Los ítems generales existentes siguen disponibles según la regla actual del sistema; no se eliminan registros QA ni ítems antiguos.
- Gestión social conserva su pantalla de casos y etapas. Esta configuración no cambia esa pantalla por una planilla genérica de actividades.

## Preparación de otro entorno

Sin guardar:

```sh
python manage.py configurar_items_areas --usuario ADMINISTRADOR
```

Para aplicar expresamente, agregar `--aplicar`. Requiere las doce áreas previamente configuradas y un superusuario activo. La operación es transaccional y repetible sin duplicados. No requiere migración del esquema ni acceso al Excel en ejecución.

## Resultado local del 20/10/2026

Base MAMP: se reutilizaron 17 ítems, se crearon 5 faltantes y se añadieron las 73 asociaciones. En la repetición: cero altas y cero vínculos adicionales. También se configuró la base independiente de demostración del puerto 8013 (22 ítems, 73 asociaciones).

Verificación: 48 pruebas aprobadas de áreas, asignación y filtrado de ítems, planillas y flujo Excel. Incluyen rechazo de un ítem ajeno mediante la API y aceptación de uno autorizado. `manage.py check` sin incidencias. AWS no fue modificado.
