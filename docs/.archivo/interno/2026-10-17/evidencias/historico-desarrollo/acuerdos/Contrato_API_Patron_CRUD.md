# Contrato de API y Patrón Común de CRUD (SGR)

**Documento de Acuerdo Técnico — Tarea T04**
**Responsable:** Daniel Flores
**Revisor:** Daniel Angel
**Destinatarios:** Equipo SGR (Daniel Flores, Daniel Angel, Matías)
**Rama:** `backend/patron-crud`
**Estado:** Aprobado / Implementado y Verificado

---

## 1. Propósito y Alcance

Este contrato define el estándar oficial de comunicación e interfaces REST para todos los mantenedores y módulos del **Sistema de Gestión de Resultados (SGR)**.

El objetivo es garantizar que los tres desarrolladores (Daniel Flores, Daniel Angel y Matías) implementen sus respectivos CRUDs bajo un **patrón unificado y reutilizable**, eliminando discrepancias en:
1. Nombres y estructura de endpoints.
2. Formato de respuestas exitosas y de error (envoltorio JSON estándar).
3. Paginación y parámetros de búsqueda/filtrado.
4. Desactivación lógica (soft-delete) para preservar trazabilidad histórica municipal.

---

## 2. Convención de Endpoints REST

Cada recurso expone un conjunto uniforme de 5 operaciones bajo el prefijo `/api/<recurso>/`:

| Método HTTP | Ruta | Acción | Código Éxito |
|:---:|---|---|:---:|
| `GET` | `/api/<recurso>/` | Listado paginado con búsqueda y filtros | `200 OK` |
| `POST` | `/api/<recurso>/` | Crear nuevo registro | `201 Created` |
| `GET` | `/api/<recurso>/<id>/` | Obtener detalle de un registro específico | `200 OK` |
| `PUT` / `PATCH` | `/api/<recurso>/<id>/` | Actualización total (`PUT`) o parcial (`PATCH`) | `200 OK` |
| `DELETE` | `/api/<recurso>/<id>/` | Desactivación lógica (`estado = false`) | `200 OK` |
| `POST` | `/api/<recurso>/<id>/toggle-estado/` | Alternar estado activo $\leftrightarrow$ inactivo | `200 OK` |

---

## 3. Parámetros de Consulta Estándar (Query Parameters)

Todos los endpoints de listado (`GET /api/<recurso>/`) aceptan los siguientes parámetros:

| Parámetro | Tipo | Por Defecto | Descripción | Ejemplo |
|---|:---:|:---:|---|---|
| `search` | String | `""` | Búsqueda por coincidencia parcial (`icontains`) en campos clave | `?search=Compañías` |
| `estado` | String | `activos` | Filtro por vigencia: `activos`, `inactivos` o `todos` | `?estado=activos` |
| `page` | Entero | `1` | Número de página solicitada ($\ge 1$) | `?page=2` |
| `page_size` | Entero | `10` | Cantidad de registros por página (máximo 100) | `?page_size=20` |
| `ordering` | String | `-id` | Campo de ordenamiento (prefijo `-` para descendente) | `?ordering=nombre` |

---

## 4. Estructura Estándar de Respuestas JSON (Sobre Uniforme)

### 4.1. Listado Paginado (`GET /api/<recurso>/`)
```json
{
  "success": true,
  "count": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5,
  "results": [
    {
      "id": 1,
      "codigo": "TA-01",
      "nombre": "Consulta General",
      "descripcion": "Atención ciudadana estándar",
      "estado": true
    }
  ]
}
```

### 4.2. Creación Exitosa (`POST /api/<recurso>/`)
```json
{
  "success": true,
  "message": "Registro creado exitosamente.",
  "data": {
    "id": 2,
    "codigo": "TA-02",
    "nombre": "Atención Social",
    "descripcion": "Derivación a DIDECO",
    "estado": true
  }
}
```

### 4.3. Detalle y Actualización (`GET` / `PATCH /api/<recurso>/<id>/`)
```json
{
  "success": true,
  "message": "Registro actualizado exitosamente.",
  "data": {
    "id": 2,
    "codigo": "TA-02",
    "nombre": "Atención Social Modificada",
    "descripcion": "Nueva descripción",
    "estado": true
  }
}
```

### 4.4. Desactivación Lógica y Toggle (`DELETE` o `POST /toggle-estado/`)
```json
{
  "success": true,
  "message": "Registro desactivado exitosamente.",
  "data": {
    "id": 2,
    "estado": false
  }
}
```

---

## 5. Estructura Estándar de Errores

Cualquier falla en la petición retornará un objeto con `"success": false` y el objeto `"error"` detallando el tipo de fallo:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Error de validación en los datos enviados.",
    "details": {
      "codigo": ["Este campo es obligatorio."],
      "nombre": ["Este campo es obligatorio."]
    }
  }
}
```

### Códigos de Error Estandarizados:
* `VALIDATION_ERROR` (`400 Bad Request`): Datos faltantes, tipo incorrecto o validaciones de modelo fallidas.
* `INVALID_JSON` (`400 Bad Request`): El cuerpo enviado no tiene formato JSON válido.
* `NOT_FOUND` (`404 Not Found`): El ID consultado no existe en la base de datos.
* `DUPLICATE_ERROR` (`409 Conflict`): Violación de clave única (`unique=True` en base de datos).
* `UNAUTHORIZED` (`401 Unauthorized`): Usuario no autenticado (para tareas de Acceso T05-T08).
* `FORBIDDEN` (`403 Forbidden`): Usuario sin permisos suficientes para la acción.

---

## 6. Guía Rápida para Desarrolladores

### ¿Cómo crear un nuevo CRUD usando la clase base `BaseCRUDView`?

Tanto **Matías** (en `T13: CRUD Delegaciones`) como **Daniel Angel** (en `T09: CRUD Roles` y `T10: CRUD Usuarios`) solo deben definir una subclase de `BaseCRUDView`:

```python
# backend/core/views.py (Ejemplo para Matías - T13)
from .models import Delegacion
from .api import BaseCRUDView

class DelegacionCRUDView(BaseCRUDView):
    model = Delegacion
    fields = ["nombre", "direccion", "comuna", "estado"]
    search_fields = ["nombre", "direccion", "comuna"]
    ordering = ["nombre"]
```

Y registrar las rutas en `urls.py`:
```python
# backend/core/urls.py
path('delegaciones/', DelegacionCRUDView.as_view(), name='delegacion-list'),
path('delegaciones/<int:pk>/', DelegacionCRUDView.as_view(), name='delegacion-detail'),
path('delegaciones/<int:pk>/toggle-estado/', DelegacionCRUDView.as_view(), {'action': 'toggle-estado'}, name='delegacion-toggle'),
```

**¡Con estas 10 líneas de código, el mantenedor obtiene automáticamente listado, paginación, búsqueda, filtros, creación, detalle, edición y desactivación lógica!**

---

## 7. Mapeo con el Frontend Existente

Este contrato se alinea directamente con [`frontend/assets/js/modules/mantenedor-comun.js`](file:///Users/danielflores/Desktop/Proyecto%20Integrado/sgr-proyecto-integrado/frontend/assets/js/modules/mantenedor-comun.js):
- La búsqueda (`search-input`) envía `?search=...`.
- El selector de estado (`status-filter`) envía `?estado=activos|inactivos|todos`.
- El modal editor envía `POST` o `PATCH` con `application/json`.
- La alerta de desactivación invoca el endpoint `DELETE` o `toggle-estado`.
