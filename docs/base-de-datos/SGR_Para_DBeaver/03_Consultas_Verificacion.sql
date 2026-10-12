USE `sgr_prueba`;
SELECT COUNT(*) AS tablas_esperadas_43 FROM information_schema.tables WHERE table_schema=DATABASE() AND table_type='BASE TABLE';
SELECT COUNT(*) AS claves_foraneas_esperadas_94 FROM information_schema.referential_constraints WHERE constraint_schema=DATABASE();
SELECT table_name,column_name,column_type,is_nullable FROM information_schema.columns WHERE table_schema=DATABASE() ORDER BY table_name,ordinal_position;
SELECT s.codigo AS subcodigo,s.nombre AS subatencion,p.codigo AS tipocodigo,p.nombre AS tipo FROM ValorCatalogo s JOIN ValorCatalogo p ON p.id_valor_catalogo=s.id_valor_padre;
SELECT codigo,nombre,comuna,estado FROM Delegacion;
