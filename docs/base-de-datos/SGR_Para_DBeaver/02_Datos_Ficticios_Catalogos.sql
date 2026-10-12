USE `sgr_prueba`;
START TRANSACTION;
INSERT INTO Delegacion (codigo,nombre,direccion,telefono,estado,creado_en,actualizado_en,comuna,version_fila)
VALUES ('DEMO-01','Delegación de prueba','Dirección ficticia','000000000','ACTIVO',UTC_TIMESTAMP(6),UTC_TIMESTAMP(6),'La Serena',1);
INSERT INTO Cargo (nombre,descripcion,estado,creado_en,actualizado_en) VALUES ('Cargo de prueba','Dato ficticio','ACTIVO',UTC_TIMESTAMP(6),UTC_TIMESTAMP(6));
INSERT INTO Rol (nombre,descripcion,estado,version_fila) VALUES ('Rol de prueba','Permisos por acordar','ACTIVO',1);
INSERT INTO Permiso (codigo,nombre,descripcion,estado) VALUES ('DEMO_CONSULTAR','Consultar prueba','No concede acceso sin backend','ACTIVO');
INSERT INTO RolPermiso (id_rol,id_permiso) SELECT r.id_rol,p.id_permiso FROM Rol r JOIN Permiso p ON p.codigo='DEMO_CONSULTAR' WHERE r.nombre='Rol de prueba';
INSERT INTO Catalogo (codigo,nombre,descripcion,estado) VALUES ('TIPO_ATENCION','Tipo de Atención','Catálogo padre','ACTIVO'),('SUB_ATENCION','Sub Atención','Catálogo hijo','ACTIVO');
INSERT INTO ValorCatalogo (id_catalogo,codigo,nombre,orden,estado,descripcion,id_valor_padre,vigente_desde,vigente_hasta,version_fila)
SELECT id_catalogo,'DEMO-T01','Tipo de prueba',1,'ACTIVO','Dato ficticio',NULL,UTC_TIMESTAMP(6),NULL,1 FROM Catalogo WHERE codigo='TIPO_ATENCION';
INSERT INTO ValorCatalogo (id_catalogo,codigo,nombre,orden,estado,descripcion,id_valor_padre,vigente_desde,vigente_hasta,version_fila)
SELECT c.id_catalogo,'DEMO-S01','Subatención de prueba',1,'ACTIVO','Dato ficticio',v.id_valor_catalogo,UTC_TIMESTAMP(6),NULL,1 FROM Catalogo c JOIN ValorCatalogo v ON v.codigo='DEMO-T01' WHERE c.codigo='SUB_ATENCION';
INSERT INTO Funcion (codigo,nombre,descripcion,unidad_medida,estado) VALUES ('DEMO-I01','Ítem de prueba','Dato ficticio','UNIDADES','ACTIVO');
COMMIT;
