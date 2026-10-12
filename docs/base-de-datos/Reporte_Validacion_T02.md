# Reporte de Validación del Modelo de Datos (Tarea T02)

**Proyecto:** Sistema de Gestión de Resultados (SGR) — Delegación Municipal Las Compañías  
**Responsable:** Daniel Flores  
**Fecha:** 12 de Octubre de 2026  
**Rama Git:** `db/validacion-modelo`  
**Base de Datos Objetivo:** `sgr_prueba` en MySQL 8.0 (Local / MAMP)

---

## 1. Objetivo de la Tarea T02
Validar y alinear el modelo relacional del SGR en el motor MySQL local, verificando la correcta creación de todas las tablas, integridad referencial (claves foráneas), catálogos base y consistencia respecto a los requerimientos del sistema municipal.

---

## 2. Entorno de Validación
- **Servidor:** MySQL 8.0.x (MAMP Localhost)
- **Host / Puerto:** `127.0.0.1:8889`
- **Base de Datos:** `sgr_prueba`
- **Archivos SQL ejecutados:**
  1. `docs/base-de-datos/SGR_Para_DBeaver/01_Crear_Base_Completa_SGR.sql`
  2. `docs/base-de-datos/SGR_Para_DBeaver/02_Datos_Ficticios_Catalogos.sql`
  3. `docs/base-de-datos/SGR_Para_DBeaver/03_Consultas_Verificacion.sql`

---

## 3. Resultados de la Verificación Cuantitativa

| Indicador de Verificación | Resultado Esperado | Resultado Obtenido | Estado |
|---|:---:|:---:|:---:|
| **Total Tablas Base (`BASE TABLE`)** | 43 | **43** | ✅ Conforme |
| **Total Claves Foráneas (`FK`)** | 94 | **94** | ✅ Conforme |
| **Jerarquía de Catálogos (`ValorCatalogo`)** | Tipo -> Subatención | `DEMO-T01` -> `DEMO-S01` | ✅ Conforme |
| **Delegación Semilla (`Delegacion`)** | DEMO-01 (La Serena) | `DEMO-01` ACTIVO | ✅ Conforme |

---

## 4. Auditoría de Requisitos Críticos de Negocio

### 4.1. Separación de Delegación de Origen vs. Delegación Responsable
Se verificó que los modelos operacionales clave soportan la trazabilidad territorial independiente entre la delegación donde se registra el evento y la delegación responsable de su ejecución/resolución:
- **`Atencion`**: Contiene tanto `id_delegacion` (delegación de captura/origen) como `id_delegacion_responsable`.
- **`Compromiso`**: Contiene explícitamente `id_delegacion_origen` e `id_delegacion_responsable`.

### 4.2. Concurrencia Optimista e Idempotencia
- **`version_fila`**: Presente con valor por defecto `1` en tablas transaccionales clave (`Atencion`, `Compromiso`).
- **`clave_idempotencia`**: Índice único `UNI` validado en la tabla `Atencion` para prevenir duplicación accidental de atenciones en ventanilla.

### 4.3. Jerarquía Tipo y Sub-atención
- La tabla unificada `ValorCatalogo` gestiona la jerarquía recursiva mediante `id_valor_padre`.
- Se validó la consulta de relación padre-hijo sin anomalías de integridad.

---

## 5. Ajustes de Configuración Realizados
1. **`backend/.env.example`**: Se actualizó el nombre sugerido de base de datos a `DB_NAME=sgr_prueba`.
2. **`backend/requirements.txt`**: Se normalizó el archivo a codificación estándar ASCII/UTF-8 (removiendo artefactos UTF-16LE de Windows).
3. **`backend/.env` (Local)**: Configurado y verificado localmente con las credenciales del entorno de desarrollo (excluido de Git por seguridad).

---

## 6. Conclusión y Siguiente Paso
La tarea **T02 queda oficialmente completada y validada**. El esquema en `sgr_prueba` está 100% operativo y listo para servir como base para el modelado Django ORM y la definición del patrón común de API REST (**T04**).
