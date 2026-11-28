# MT02 - Inventario de Campos Mínimos de los Mantenedores
**Responsable:** Matías | **Fecha:** 28/11/2026 | **Etapa:** 01. Preparación documental | **Estado:** Terminada

## 1. Propósito
Documentar la estructura de campos, tipos de datos, obligatoriedad y validaciones de cada entidad del catálogo del SGR para asegurar consistencia entre interfaz, backend y base de datos.

## 2. Inventario de Entidades y Campos

### 2.1 Delegaciones
- `codigo`: VARCHAR(10), obligatorio, único, formato mayúsculas sin espacios.
- `nombre`: VARCHAR(100), obligatorio.
- `direccion`: VARCHAR(255), opcional.
- `telefono`: VARCHAR(20), opcional.
- `activa`: BOOLEAN, por defecto True.

### 2.2 Territorios
- `codigo`: VARCHAR(20), obligatorio, único.
- `nombre`: VARCHAR(100), obligatorio.
- `delegacion`: FK Delegacion, obligatorio.
- `activo`: BOOLEAN, por defecto True.

### 2.3 Vecinos
- `rut`: VARCHAR(12), opcional en atenciones ocasionales; obligatorio en mantenedor maestro, con validación de dígito verificador módulo 11.
- `nombres`: VARCHAR(100), obligatorio.
- `apellidos`: VARCHAR(100), obligatorio.
- `telefono`: VARCHAR(20), opcional.
- `email`: VARCHAR(100), opcional con validación RFC 5322.
- `direccion`: VARCHAR(255), opcional.
- `territorio`: FK Territorio, opcional.
- `activo`: BOOLEAN, por defecto True.

### 2.4 Organizaciones Comunitarias
- `nombre`: VARCHAR(150), obligatorio.
- `tipo`: VARCHAR(50), obligatorio (Junta de Vecinos, Club Deportivo, Centro de Madres, Agrupación Cultural).
- `personalidad_juridica`: VARCHAR(50), opcional.
- `territorio`: FK Territorio, obligatorio.
- `direccion`: VARCHAR(255), opcional.
- `activa`: BOOLEAN, por defecto True.

### 2.5 Cargos de Dirigentes
- `organizacion`: FK Organizacion, obligatorio.
- `vecino`: FK Vecino, obligatorio.
- `cargo`: VARCHAR(50), obligatorio (Presidente, Vicepresidente, Secretario, Tesorero, Director).
- `fecha_inicio`: DATE, obligatorio.
- `fecha_termino`: DATE, opcional (nulo indica vigencia actual).
- `activo`: BOOLEAN, por defecto True.

### 2.6 Ítems de Meta
- `codigo`: VARCHAR(20), obligatorio, único.
- `nombre`: VARCHAR(150), obligatorio.
- `tipo`: VARCHAR(50), obligatorio (Cuantitativo, Cualitativo).
- `unidad_medida`: VARCHAR(50), obligatorio (Visitas, Atenciones, Informes, Talleres).
- `requiere_evidencia`: BOOLEAN, por defecto True.
- `prorrateable`: BOOLEAN, por defecto False (solo ausencias prorratean si True).
- `activo`: BOOLEAN, por defecto True.
