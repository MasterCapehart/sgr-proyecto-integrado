-- SGR: modelo completo del dominio. MySQL 8.4. No contiene DROP.

-- El nombre nuevo evita sustituir una base existente. Si ya existe, detener y elegir otro nombre.

CREATE DATABASE `sgr_prueba` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE `sgr_prueba`;

SET time_zone = '+00:00';

CREATE TABLE `Delegacion` (
  `id_delegacion` BIGINT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `direccion` VARCHAR(255) NOT NULL,
  `telefono` VARCHAR(255) NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `creado_en` DATETIME(6) NOT NULL,
  `actualizado_en` DATETIME(6) NOT NULL,
  `comuna` VARCHAR(255) NOT NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_delegacion`),
  UNIQUE KEY `uq_Delegacion_1` (`codigo`),
  CONSTRAINT `ck_Delegacion_1` CHECK (version_fila > 0)
) ENGINE=InnoDB;

CREATE TABLE `Cargo` (
  `id_cargo` BIGINT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `creado_en` DATETIME(6) NOT NULL,
  `actualizado_en` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id_cargo`),
  UNIQUE KEY `uq_Cargo_1` (`nombre`)
) ENGINE=InnoDB;

CREATE TABLE `Funcionario` (
  `id_funcionario` BIGINT NOT NULL AUTO_INCREMENT,
  `identificador_interno` VARCHAR(255) NOT NULL,
  `nombre_completo` VARCHAR(255) NOT NULL,
  `correo_institucional` VARCHAR(255) NOT NULL,
  `telefono_protegido` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `creado_en` DATETIME(6) NOT NULL,
  `actualizado_en` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id_funcionario`),
  UNIQUE KEY `uq_Funcionario_1` (`identificador_interno`)
) ENGINE=InnoDB;

CREATE TABLE `Usuario` (
  `id_usuario` BIGINT NOT NULL AUTO_INCREMENT,
  `id_funcionario` BIGINT NOT NULL,
  `nombre_usuario` VARCHAR(255) NOT NULL,
  `correo` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `activo` BOOLEAN NOT NULL,
  `ultimo_acceso` DATETIME(6) NULL,
  `creado_en` DATETIME(6) NOT NULL,
  `actualizado_en` DATETIME(6) NOT NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `uq_Usuario_1` (`id_funcionario`),
  UNIQUE KEY `uq_Usuario_2` (`nombre_usuario`),
  UNIQUE KEY `uq_Usuario_3` (`correo`),
  CONSTRAINT `ck_Usuario_1` CHECK (activo IN (0,1)),
  CONSTRAINT `ck_Usuario_2` CHECK (version_fila > 0)
) ENGINE=InnoDB;

CREATE TABLE `AsignacionFuncionario` (
  `id_asignacion` BIGINT NOT NULL AUTO_INCREMENT,
  `id_funcionario` BIGINT NOT NULL,
  `id_delegacion` BIGINT NOT NULL,
  `id_cargo` BIGINT NOT NULL,
  `fecha_desde` DATE NOT NULL,
  `fecha_hasta` DATE NULL,
  `activo` BOOLEAN NOT NULL,
  `motivo_cambio` TEXT NOT NULL,
  PRIMARY KEY (`id_asignacion`),
  CONSTRAINT `ck_AsignacionFuncionario_1` CHECK (fecha_hasta IS NULL OR fecha_hasta >= fecha_desde),
  CONSTRAINT `ck_AsignacionFuncionario_2` CHECK (activo IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE `UsuarioRol` (
  `id_usuario_rol` BIGINT NOT NULL AUTO_INCREMENT,
  `id_usuario` BIGINT NOT NULL,
  `id_rol` BIGINT NOT NULL,
  `id_delegacion` BIGINT NULL,
  `fecha_desde` DATE NOT NULL,
  `fecha_hasta` DATE NULL,
  `activo` BOOLEAN NOT NULL,
  PRIMARY KEY (`id_usuario_rol`),
  CONSTRAINT `ck_UsuarioRol_1` CHECK (fecha_hasta IS NULL OR fecha_hasta >= fecha_desde),
  CONSTRAINT `ck_UsuarioRol_2` CHECK (activo IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE `Rol` (
  `id_rol` BIGINT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_rol`),
  UNIQUE KEY `uq_Rol_1` (`nombre`),
  CONSTRAINT `ck_Rol_1` CHECK (version_fila > 0)
) ENGINE=InnoDB;

CREATE TABLE `Permiso` (
  `id_permiso` BIGINT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id_permiso`),
  UNIQUE KEY `uq_Permiso_1` (`codigo`)
) ENGINE=InnoDB;

CREATE TABLE `RolPermiso` (
  `id_rol_permiso` BIGINT NOT NULL AUTO_INCREMENT,
  `id_rol` BIGINT NOT NULL,
  `id_permiso` BIGINT NOT NULL,
  PRIMARY KEY (`id_rol_permiso`),
  UNIQUE KEY `uq_RolPermiso_1` (`id_rol`, `id_permiso`)
) ENGINE=InnoDB;

CREATE TABLE `AreaApoyo` (
  `id_area_apoyo` BIGINT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id_area_apoyo`),
  UNIQUE KEY `uq_AreaApoyo_1` (`nombre`)
) ENGINE=InnoDB;

CREATE TABLE `Territorio` (
  `id_territorio` BIGINT NOT NULL AUTO_INCREMENT,
  `id_delegacion` BIGINT NOT NULL,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `tipo` VARCHAR(255) NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id_territorio`),
  UNIQUE KEY `uq_Territorio_1` (`codigo`),
  UNIQUE KEY `uq_Territorio_2` (`id_territorio`, `id_delegacion`)
) ENGINE=InnoDB;

CREATE TABLE `Catalogo` (
  `id_catalogo` BIGINT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id_catalogo`),
  UNIQUE KEY `uq_Catalogo_1` (`codigo`)
) ENGINE=InnoDB;

CREATE TABLE `ValorCatalogo` (
  `id_valor_catalogo` BIGINT NOT NULL AUTO_INCREMENT,
  `id_catalogo` BIGINT NOT NULL,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `orden` INT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `id_valor_padre` BIGINT NULL,
  `vigente_desde` DATETIME(6) NOT NULL,
  `vigente_hasta` DATETIME(6) NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_valor_catalogo`),
  UNIQUE KEY `uq_ValorCatalogo_1` (`id_catalogo`, `codigo`),
  UNIQUE KEY `uq_ValorCatalogo_2` (`id_valor_catalogo`, `id_valor_padre`),
  CONSTRAINT `ck_ValorCatalogo_1` CHECK (version_fila > 0)
) ENGINE=InnoDB;

CREATE TABLE `PeriodoMedicion` (
  `id_periodo` BIGINT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(255) NOT NULL,
  `fecha_inicio` DATE NOT NULL,
  `fecha_fin` DATE NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `cerrado_en` DATETIME(6) NULL,
  `reabierto_en` DATETIME(6) NULL,
  `calendario_config` JSON NOT NULL,
  `zona_horaria` VARCHAR(64) NOT NULL,
  PRIMARY KEY (`id_periodo`),
  UNIQUE KEY `uq_PeriodoMedicion_1` (`nombre`),
  CONSTRAINT `ck_PeriodoMedicion_1` CHECK (fecha_fin >= fecha_inicio)
) ENGINE=InnoDB;

CREATE TABLE `VersionConfiguracion` (
  `id_version_config` BIGINT NOT NULL AUTO_INCREMENT,
  `id_periodo` BIGINT NOT NULL,
  `numero_version` INT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `vigente_desde` DATETIME(6) NOT NULL,
  `vigente_hasta` DATETIME(6) NULL,
  `creado_por_usuario` BIGINT NOT NULL,
  `motivo_cambio` TEXT NOT NULL,
  `umbral_colectivo` DECIMAL(18,6) NOT NULL,
  `parametros_calculo` JSON NOT NULL,
  PRIMARY KEY (`id_version_config`),
  UNIQUE KEY `uq_VersionConfiguracion_1` (`id_periodo`, `numero_version`),
  CONSTRAINT `ck_VersionConfiguracion_1` CHECK (numero_version > 0)
) ENGINE=InnoDB;

CREATE TABLE `Funcion` (
  `id_funcion` BIGINT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `unidad_medida` VARCHAR(255) NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id_funcion`),
  UNIQUE KEY `uq_Funcion_1` (`codigo`)
) ENGINE=InnoDB;

CREATE TABLE `Indicador` (
  `id_indicador` BIGINT NOT NULL AUTO_INCREMENT,
  `id_funcion` BIGINT NOT NULL,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `tipo_calculo` VARCHAR(255) NOT NULL,
  `unidad_medida` VARCHAR(255) NOT NULL,
  `umbral_verde` DECIMAL(18,6) NOT NULL,
  `umbral_ambar` DECIMAL(18,6) NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_indicador`),
  UNIQUE KEY `uq_Indicador_1` (`codigo`),
  CONSTRAINT `ck_Indicador_1` CHECK (version_fila > 0)
) ENGINE=InnoDB;

CREATE TABLE `ConfiguracionMeta` (
  `id_configuracion_meta` BIGINT NOT NULL AUTO_INCREMENT,
  `id_version_config` BIGINT NOT NULL,
  `id_indicador` BIGINT NOT NULL,
  `id_asignacion` BIGINT NOT NULL,
  `valor_meta` DECIMAL(18,6) NOT NULL,
  `ponderador` DECIMAL(18,6) NOT NULL,
  `meta_diaria` DECIMAL(18,6) NOT NULL,
  `fecha_inicio` DATE NOT NULL,
  `fecha_fin` DATE NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `maximo_computable` DECIMAL(18,6) NOT NULL,
  `formula_aplicada` TEXT NOT NULL,
  `tipo_calculo_aplicado` VARCHAR(255) NOT NULL,
  `unidad_medida_aplicada` VARCHAR(255) NOT NULL,
  `umbral_verde_aplicado` DECIMAL(18,6) NOT NULL,
  `umbral_ambar_aplicado` DECIMAL(18,6) NOT NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_configuracion_meta`),
  UNIQUE KEY `uq_ConfiguracionMeta_1` (`id_configuracion_meta`, `id_asignacion`),
  CONSTRAINT `ck_ConfiguracionMeta_1` CHECK (fecha_fin >= fecha_inicio),
  CONSTRAINT `ck_ConfiguracionMeta_2` CHECK (version_fila > 0),
  CONSTRAINT `ck_ConfiguracionMeta_3` CHECK (valor_meta > 0),
  CONSTRAINT `ck_ConfiguracionMeta_4` CHECK (ponderador BETWEEN 0 AND 100),
  CONSTRAINT `ck_ConfiguracionMeta_5` CHECK (maximo_computable > 0),
  CONSTRAINT `ck_ConfiguracionMeta_6` CHECK (umbral_ambar_aplicado <= umbral_verde_aplicado)
) ENGINE=InnoDB;

CREATE TABLE `AporteIndicador` (
  `id_aporte` BIGINT NOT NULL AUTO_INCREMENT,
  `id_configuracion_meta` BIGINT NOT NULL,
  `id_actividad` BIGINT NULL,
  `id_compromiso` BIGINT NULL,
  `valor_aporte` DECIMAL(18,6) NOT NULL,
  `fecha_aporte` DATETIME(6) NOT NULL,
  `estado_validacion` VARCHAR(255) NOT NULL,
  `id_asignacion_historica` BIGINT NOT NULL,
  `version_registro` INT NOT NULL,
  PRIMARY KEY (`id_aporte`),
  UNIQUE KEY `uq_AporteIndicador_1` (`id_configuracion_meta`, `id_actividad`),
  UNIQUE KEY `uq_AporteIndicador_2` (`id_configuracion_meta`, `id_compromiso`),
  CONSTRAINT `ck_AporteIndicador_1` CHECK (version_registro > 0),
  CONSTRAINT `ck_AporteIndicador_2` CHECK ((id_actividad IS NOT NULL AND id_compromiso IS NULL) OR (id_actividad IS NULL AND id_compromiso IS NOT NULL))
) ENGINE=InnoDB;

CREATE TABLE `ResultadoIndicador` (
  `id_resultado` BIGINT NOT NULL AUTO_INCREMENT,
  `id_configuracion_meta` BIGINT NOT NULL,
  `fecha_calculo` DATETIME(6) NOT NULL,
  `avance_acumulado` DECIMAL(18,6) NOT NULL,
  `cumplimiento_porcentaje` DECIMAL(18,6) NOT NULL,
  `puntaje_ponderado` DECIMAL(18,6) NOT NULL,
  `meta_esperada_dia` DECIMAL(18,6) NOT NULL,
  `color_semaforo` VARCHAR(255) NOT NULL,
  `id_asignacion_historica` BIGINT NOT NULL,
  PRIMARY KEY (`id_resultado`)
) ENGINE=InnoDB;

CREATE TABLE `Actividad` (
  `id_actividad` BIGINT NOT NULL AUTO_INCREMENT,
  `codigo_actividad` VARCHAR(64) NOT NULL,
  `id_funcionario` BIGINT NOT NULL,
  `id_delegacion` BIGINT NOT NULL,
  `id_territorio` BIGINT NULL,
  `id_tipo_actividad` BIGINT NOT NULL,
  `fecha_actividad` DATE NOT NULL,
  `descripcion_solicitud_problema` TEXT NOT NULL,
  `accion_realizada` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `creado_en` DATETIME(6) NOT NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_actividad`),
  UNIQUE KEY `uq_Actividad_1` (`codigo_actividad`),
  UNIQUE KEY `uq_Actividad_2` (`id_actividad`, `id_delegacion`),
  CONSTRAINT `ck_Actividad_1` CHECK (version_fila > 0)
) ENGINE=InnoDB;

CREATE TABLE `Servicio` (
  `id_servicio` BIGINT NOT NULL AUTO_INCREMENT,
  `id_tipo_servicio` BIGINT NOT NULL,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `id_subtipo_servicio` BIGINT NULL,
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB;

CREATE TABLE `Atencion` (
  `id_atencion` BIGINT NOT NULL AUTO_INCREMENT,
  `id_actividad` BIGINT NOT NULL,
  `id_servicio` BIGINT NOT NULL,
  `id_persona` BIGINT NOT NULL,
  `fecha_atencion` DATETIME(6) NOT NULL,
  `tipo_gestion` VARCHAR(255) NOT NULL,
  `resultado` VARCHAR(255) NOT NULL,
  `observacion` TEXT NOT NULL,
  `codigo_atencion` VARCHAR(64) NOT NULL,
  `id_tipo_atencion` BIGINT NOT NULL,
  `id_sub_atencion` BIGINT NOT NULL,
  `id_delegacion` BIGINT NOT NULL,
  `creado_por_usuario` BIGINT NOT NULL,
  `descripcion` TEXT NOT NULL,
  `clave_idempotencia` VARCHAR(64) NOT NULL,
  `id_caso_social` BIGINT NULL,
  `numero_gestion` TINYINT NULL,
  `nombre_tipo_registrado` VARCHAR(255) NOT NULL,
  `nombre_sub_atencion_registrado` VARCHAR(255) NOT NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  `id_delegacion_responsable` BIGINT NOT NULL,
  PRIMARY KEY (`id_atencion`),
  UNIQUE KEY `uq_Atencion_1` (`codigo_atencion`),
  UNIQUE KEY `uq_Atencion_2` (`clave_idempotencia`),
  UNIQUE KEY `uq_Atencion_3` (`id_caso_social`, `numero_gestion`),
  CONSTRAINT `ck_Atencion_1` CHECK (version_fila > 0),
  CONSTRAINT `ck_Atencion_2` CHECK ((id_caso_social IS NULL AND numero_gestion IS NULL) OR (id_caso_social IS NOT NULL AND numero_gestion IS NOT NULL AND numero_gestion BETWEEN 1 AND 3))
) ENGINE=InnoDB;

CREATE TABLE `PersonaSolicitante` (
  `id_persona` BIGINT NOT NULL AUTO_INCREMENT,
  `nombre_referencia` VARCHAR(255) NOT NULL,
  `telefono_protegido` TEXT NOT NULL,
  `correo_protegido` TEXT NOT NULL,
  `base_acceso_datos` VARCHAR(255) NOT NULL,
  `anonimizado_en` DATETIME(6) NULL,
  PRIMARY KEY (`id_persona`)
) ENGINE=InnoDB;

CREATE TABLE `Compromiso` (
  `id_compromiso` BIGINT NOT NULL AUTO_INCREMENT,
  `id_actividad_origen` BIGINT NULL,
  `id_persona_solicitante` BIGINT NOT NULL,
  `id_territorio` BIGINT NOT NULL,
  `id_area_apoyo` BIGINT NULL,
  `id_estado_actual` BIGINT NOT NULL,
  `descripcion` TEXT NOT NULL,
  `fecha_comprometida` DATE NOT NULL,
  `prioridad` VARCHAR(255) NOT NULL,
  `creado_en` DATETIME(6) NOT NULL,
  `cerrado_en` DATETIME(6) NULL,
  `version_fila` INT NOT NULL DEFAULT 1,
  `id_delegacion_origen` BIGINT NOT NULL,
  `id_delegacion_responsable` BIGINT NOT NULL,
  PRIMARY KEY (`id_compromiso`),
  CONSTRAINT `ck_Compromiso_1` CHECK (version_fila > 0)
) ENGINE=InnoDB;

CREATE TABLE `AsignacionCompromiso` (
  `id_asignacion_compromiso` BIGINT NOT NULL AUTO_INCREMENT,
  `id_compromiso` BIGINT NOT NULL,
  `id_funcionario_responsable` BIGINT NOT NULL,
  `asignado_por_usuario` BIGINT NOT NULL,
  `fecha_desde` DATE NOT NULL,
  `fecha_hasta` DATE NULL,
  `motivo_reasignacion` VARCHAR(255) NOT NULL,
  `activo` BOOLEAN NOT NULL,
  PRIMARY KEY (`id_asignacion_compromiso`),
  CONSTRAINT `ck_AsignacionCompromiso_1` CHECK (fecha_hasta IS NULL OR fecha_hasta >= fecha_desde),
  CONSTRAINT `ck_AsignacionCompromiso_2` CHECK (activo IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE `EstadoCompromiso` (
  `id_estado_compromiso` BIGINT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(64) NOT NULL,
  `nombre` VARCHAR(255) NOT NULL,
  `orden` INT NOT NULL,
  `es_estado_final` BOOLEAN NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id_estado_compromiso`),
  UNIQUE KEY `uq_EstadoCompromiso_1` (`codigo`),
  CONSTRAINT `ck_EstadoCompromiso_1` CHECK (es_estado_final IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE `HistorialEstadoCompromiso` (
  `id_historial_estado` BIGINT NOT NULL AUTO_INCREMENT,
  `id_compromiso` BIGINT NOT NULL,
  `id_estado_anterior` BIGINT NULL,
  `id_estado_nuevo` BIGINT NOT NULL,
  `id_usuario_autor` BIGINT NOT NULL,
  `fecha_cambio` DATETIME(6) NOT NULL,
  `observacion` TEXT NOT NULL,
  `motivo_incumplimiento` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id_historial_estado`)
) ENGINE=InnoDB;

CREATE TABLE `SeguimientoCompromiso` (
  `id_seguimiento` BIGINT NOT NULL AUTO_INCREMENT,
  `id_compromiso` BIGINT NOT NULL,
  `id_usuario_autor` BIGINT NOT NULL,
  `fecha_seguimiento` DATETIME(6) NOT NULL,
  `observacion_avance` TEXT NOT NULL,
  `porcentaje_avance` DECIMAL(18,6) NULL,
  `nueva_fecha` VARCHAR(255) NULL,
  `comunicado_en` DATETIME(6) NULL,
  PRIMARY KEY (`id_seguimiento`)
) ENGINE=InnoDB;

CREATE TABLE `Evidencia` (
  `id_evidencia` BIGINT NOT NULL AUTO_INCREMENT,
  `id_actividad` BIGINT NOT NULL,
  `codigo_evidencia` VARCHAR(64) NOT NULL,
  `nombre_archivo` VARCHAR(255) NOT NULL,
  `ruta_controlada` VARCHAR(255) NOT NULL,
  `tipo_mime` VARCHAR(255) NOT NULL,
  `tamano_bytes` BIGINT NOT NULL,
  `hash_archivo` CHAR(64) NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `cargado_por_usuario` BIGINT NOT NULL,
  `cargado_en` DATETIME(6) NOT NULL,
  `version_archivo` INT NOT NULL,
  PRIMARY KEY (`id_evidencia`),
  UNIQUE KEY `uq_Evidencia_1` (`codigo_evidencia`),
  CONSTRAINT `ck_Evidencia_1` CHECK (tamano_bytes >= 0),
  CONSTRAINT `ck_Evidencia_2` CHECK (version_archivo > 0)
) ENGINE=InnoDB;

CREATE TABLE `ValidacionEvidencia` (
  `id_validacion` BIGINT NOT NULL AUTO_INCREMENT,
  `id_evidencia` BIGINT NOT NULL,
  `id_verificador_usuario` BIGINT NOT NULL,
  `resultado` VARCHAR(255) NOT NULL,
  `observacion` TEXT NOT NULL,
  `fecha_revision` DATETIME(6) NOT NULL,
  `version_evidencia` INT NOT NULL,
  `vigente` BOOLEAN NOT NULL,
  PRIMARY KEY (`id_validacion`),
  CONSTRAINT `ck_ValidacionEvidencia_1` CHECK (version_evidencia > 0),
  CONSTRAINT `ck_ValidacionEvidencia_2` CHECK (vigente IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE `Alerta` (
  `id_alerta` BIGINT NOT NULL AUTO_INCREMENT,
  `id_compromiso` BIGINT NULL,
  `id_resultado` BIGINT NULL,
  `id_usuario_destino` BIGINT NOT NULL,
  `tipo` VARCHAR(255) NOT NULL,
  `nivel` VARCHAR(255) NOT NULL,
  `mensaje` VARCHAR(255) NOT NULL,
  `generada_en` DATETIME(6) NOT NULL,
  `leida_en` DATETIME(6) NULL,
  `estado` VARCHAR(32) NOT NULL,
  `id_regla_alerta` BIGINT NOT NULL,
  `id_evidencia` BIGINT NULL,
  `id_funcionario` BIGINT NULL,
  PRIMARY KEY (`id_alerta`)
) ENGINE=InnoDB;

CREATE TABLE `Conversacion` (
  `id_conversacion` BIGINT NOT NULL AUTO_INCREMENT,
  `id_actividad` BIGINT NULL,
  `id_compromiso` BIGINT NULL,
  `id_evidencia` BIGINT NULL,
  `asunto` VARCHAR(255) NOT NULL,
  `estado` VARCHAR(32) NOT NULL,
  `creado_en` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id_conversacion`),
  CONSTRAINT `ck_Conversacion_1` CHECK ((id_actividad IS NOT NULL) + (id_compromiso IS NOT NULL) + (id_evidencia IS NOT NULL) = 1)
) ENGINE=InnoDB;

CREATE TABLE `Mensaje` (
  `id_mensaje` BIGINT NOT NULL AUTO_INCREMENT,
  `id_conversacion` BIGINT NOT NULL,
  `id_usuario_autor` BIGINT NOT NULL,
  `id_mensaje_padre` BIGINT NULL,
  `contenido` TEXT NOT NULL,
  `creado_en` DATETIME(6) NOT NULL,
  `editado_en` DATETIME(6) NULL,
  `estado` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`id_mensaje`),
  UNIQUE KEY `uq_Mensaje_1` (`id_mensaje`, `id_conversacion`)
) ENGINE=InnoDB;

CREATE TABLE `EventoAuditoria` (
  `id_evento_auditoria` BIGINT NOT NULL AUTO_INCREMENT,
  `id_usuario` BIGINT NULL,
  `fecha_evento` DATETIME(6) NOT NULL,
  `accion` VARCHAR(255) NOT NULL,
  `tipo_entidad` VARCHAR(255) NOT NULL,
  `identificador_entidad` VARCHAR(255) NOT NULL,
  `valor_anterior_protegido` TEXT NOT NULL,
  `valor_nuevo_protegido` TEXT NOT NULL,
  `direccion_ip` VARCHAR(45) NOT NULL,
  `resultado` VARCHAR(255) NOT NULL,
  `motivo` TEXT NOT NULL,
  `hash_integridad` CHAR(64) NOT NULL,
  PRIMARY KEY (`id_evento_auditoria`)
) ENGINE=InnoDB;

CREATE TABLE `RecuperacionAcceso` (
  `id_recuperacion` BIGINT NOT NULL AUTO_INCREMENT,
  `id_usuario` BIGINT NOT NULL,
  `codigo_hash` VARCHAR(255) NOT NULL,
  `solicitado_en` DATETIME(6) NOT NULL,
  `expira_en` DATETIME(6) NOT NULL,
  `verificado_en` DATETIME(6) NULL,
  `consumido_en` DATETIME(6) NULL,
  `invalidado_en` DATETIME(6) NULL,
  `intentos_fallidos` INT NOT NULL,
  `max_intentos` INT NOT NULL,
  `reenvio_permitido_desde` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id_recuperacion`),
  CONSTRAINT `ck_RecuperacionAcceso_1` CHECK (intentos_fallidos >= 0),
  CONSTRAINT `ck_RecuperacionAcceso_2` CHECK (max_intentos > 0),
  CONSTRAINT `ck_RecuperacionAcceso_3` CHECK (expira_en > solicitado_en),
  CONSTRAINT `ck_RecuperacionAcceso_4` CHECK (intentos_fallidos <= max_intentos)
) ENGINE=InnoDB;

CREATE TABLE `CasoSocial` (
  `id_caso_social` BIGINT NOT NULL AUTO_INCREMENT,
  `codigo` VARCHAR(64) NOT NULL,
  `id_persona` BIGINT NOT NULL,
  `abierto_en` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id_caso_social`),
  UNIQUE KEY `uq_CasoSocial_1` (`codigo`),
  UNIQUE KEY `uq_CasoSocial_2` (`id_caso_social`, `id_persona`)
) ENGINE=InnoDB;

CREATE TABLE `ValidacionCompromiso` (
  `id_validacion_compromiso` BIGINT NOT NULL AUTO_INCREMENT,
  `id_compromiso` BIGINT NOT NULL,
  `id_verificador_usuario` BIGINT NOT NULL,
  `decision` VARCHAR(255) NOT NULL,
  `motivo` TEXT NOT NULL,
  `fecha_revision` DATETIME(6) NOT NULL,
  `version_registro` INT NOT NULL,
  `vigente` BOOLEAN NOT NULL,
  PRIMARY KEY (`id_validacion_compromiso`),
  CONSTRAINT `ck_ValidacionCompromiso_1` CHECK (version_registro > 0),
  CONSTRAINT `ck_ValidacionCompromiso_2` CHECK (vigente IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE `ReglaAjuste` (
  `id_regla_ajuste` BIGINT NOT NULL AUTO_INCREMENT,
  `id_version_config` BIGINT NOT NULL,
  `concepto` VARCHAR(255) NOT NULL,
  `tipo` VARCHAR(255) NOT NULL,
  `valor` DECIMAL(18,6) NOT NULL,
  `activo` BOOLEAN NOT NULL,
  PRIMARY KEY (`id_regla_ajuste`),
  CONSTRAINT `ck_ReglaAjuste_1` CHECK (activo IN (0,1))
) ENGINE=InnoDB;

CREATE TABLE `AjusteResultado` (
  `id_ajuste_resultado` BIGINT NOT NULL AUTO_INCREMENT,
  `id_resultado` BIGINT NOT NULL,
  `id_regla_ajuste` BIGINT NOT NULL,
  `id_usuario_responsable` BIGINT NOT NULL,
  `valor_aplicado` DECIMAL(18,6) NOT NULL,
  `motivo` TEXT NOT NULL,
  `fecha` DATETIME(6) NOT NULL,
  PRIMARY KEY (`id_ajuste_resultado`)
) ENGINE=InnoDB;

CREATE TABLE `ReglaAlerta` (
  `id_regla_alerta` BIGINT NOT NULL AUTO_INCREMENT,
  `id_version_config` BIGINT NOT NULL,
  `codigo` VARCHAR(64) NOT NULL,
  `condicion` TEXT NOT NULL,
  `umbral` DECIMAL(18,6) NULL,
  `dias_anticipacion` INT NULL,
  `vigente_desde` DATETIME(6) NOT NULL,
  `vigente_hasta` DATETIME(6) NULL,
  PRIMARY KEY (`id_regla_alerta`)
) ENGINE=InnoDB;

CREATE TABLE `CargoFuncion` (
  `id_cargo_funcion` BIGINT NOT NULL AUTO_INCREMENT,
  `id_cargo` BIGINT NOT NULL,
  `id_funcion` BIGINT NOT NULL,
  `fecha_desde` DATE NOT NULL,
  `fecha_hasta` DATE NULL,
  PRIMARY KEY (`id_cargo_funcion`),
  UNIQUE KEY `uq_CargoFuncion_1` (`id_cargo`, `id_funcion`, `fecha_desde`),
  CONSTRAINT `ck_CargoFuncion_1` CHECK (fecha_hasta IS NULL OR fecha_hasta >= fecha_desde)
) ENGINE=InnoDB;

CREATE TABLE `VersionEvidencia` (
  `id_version_evidencia` BIGINT NOT NULL AUTO_INCREMENT,
  `id_evidencia` BIGINT NOT NULL,
  `numero_version` INT NOT NULL,
  `nombre_archivo` VARCHAR(255) NOT NULL,
  `ruta_controlada` VARCHAR(1024) NOT NULL,
  `tipo_mime` VARCHAR(127) NOT NULL,
  `tamano_bytes` BIGINT NOT NULL,
  `hash_archivo` CHAR(64) NOT NULL,
  `cargado_en` DATETIME(6) NOT NULL,
  `cargado_por_usuario` BIGINT NOT NULL,
  PRIMARY KEY (`id_version_evidencia`),
  UNIQUE KEY `uq_VersionEvidencia_1` (`id_evidencia`, `numero_version`),
  CONSTRAINT `ck_VersionEvidencia_1` CHECK (numero_version > 0),
  CONSTRAINT `ck_VersionEvidencia_2` CHECK (tamano_bytes >= 0)
) ENGINE=InnoDB;

ALTER TABLE `Usuario` ADD CONSTRAINT `fk_sgr_1` FOREIGN KEY (`id_funcionario`) REFERENCES `Funcionario` (`id_funcionario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AsignacionFuncionario` ADD CONSTRAINT `fk_sgr_2` FOREIGN KEY (`id_funcionario`) REFERENCES `Funcionario` (`id_funcionario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AsignacionFuncionario` ADD CONSTRAINT `fk_sgr_3` FOREIGN KEY (`id_delegacion`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AsignacionFuncionario` ADD CONSTRAINT `fk_sgr_4` FOREIGN KEY (`id_cargo`) REFERENCES `Cargo` (`id_cargo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `UsuarioRol` ADD CONSTRAINT `fk_sgr_5` FOREIGN KEY (`id_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `UsuarioRol` ADD CONSTRAINT `fk_sgr_6` FOREIGN KEY (`id_rol`) REFERENCES `Rol` (`id_rol`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `UsuarioRol` ADD CONSTRAINT `fk_sgr_7` FOREIGN KEY (`id_delegacion`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `RolPermiso` ADD CONSTRAINT `fk_sgr_8` FOREIGN KEY (`id_rol`) REFERENCES `Rol` (`id_rol`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `RolPermiso` ADD CONSTRAINT `fk_sgr_9` FOREIGN KEY (`id_permiso`) REFERENCES `Permiso` (`id_permiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Territorio` ADD CONSTRAINT `fk_sgr_10` FOREIGN KEY (`id_delegacion`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ValorCatalogo` ADD CONSTRAINT `fk_sgr_11` FOREIGN KEY (`id_catalogo`) REFERENCES `Catalogo` (`id_catalogo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ValorCatalogo` ADD CONSTRAINT `fk_sgr_12` FOREIGN KEY (`id_valor_padre`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `VersionConfiguracion` ADD CONSTRAINT `fk_sgr_13` FOREIGN KEY (`id_periodo`) REFERENCES `PeriodoMedicion` (`id_periodo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `VersionConfiguracion` ADD CONSTRAINT `fk_sgr_14` FOREIGN KEY (`creado_por_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Indicador` ADD CONSTRAINT `fk_sgr_15` FOREIGN KEY (`id_funcion`) REFERENCES `Funcion` (`id_funcion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ConfiguracionMeta` ADD CONSTRAINT `fk_sgr_16` FOREIGN KEY (`id_version_config`) REFERENCES `VersionConfiguracion` (`id_version_config`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ConfiguracionMeta` ADD CONSTRAINT `fk_sgr_17` FOREIGN KEY (`id_indicador`) REFERENCES `Indicador` (`id_indicador`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ConfiguracionMeta` ADD CONSTRAINT `fk_sgr_18` FOREIGN KEY (`id_asignacion`) REFERENCES `AsignacionFuncionario` (`id_asignacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AporteIndicador` ADD CONSTRAINT `fk_sgr_19` FOREIGN KEY (`id_configuracion_meta`) REFERENCES `ConfiguracionMeta` (`id_configuracion_meta`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AporteIndicador` ADD CONSTRAINT `fk_sgr_20` FOREIGN KEY (`id_actividad`) REFERENCES `Actividad` (`id_actividad`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AporteIndicador` ADD CONSTRAINT `fk_sgr_21` FOREIGN KEY (`id_compromiso`) REFERENCES `Compromiso` (`id_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AporteIndicador` ADD CONSTRAINT `fk_sgr_22` FOREIGN KEY (`id_asignacion_historica`) REFERENCES `AsignacionFuncionario` (`id_asignacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ResultadoIndicador` ADD CONSTRAINT `fk_sgr_23` FOREIGN KEY (`id_configuracion_meta`) REFERENCES `ConfiguracionMeta` (`id_configuracion_meta`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ResultadoIndicador` ADD CONSTRAINT `fk_sgr_24` FOREIGN KEY (`id_asignacion_historica`) REFERENCES `AsignacionFuncionario` (`id_asignacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Actividad` ADD CONSTRAINT `fk_sgr_25` FOREIGN KEY (`id_funcionario`) REFERENCES `Funcionario` (`id_funcionario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Actividad` ADD CONSTRAINT `fk_sgr_26` FOREIGN KEY (`id_delegacion`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Actividad` ADD CONSTRAINT `fk_sgr_27` FOREIGN KEY (`id_territorio`) REFERENCES `Territorio` (`id_territorio`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Actividad` ADD CONSTRAINT `fk_sgr_28` FOREIGN KEY (`id_tipo_actividad`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Servicio` ADD CONSTRAINT `fk_sgr_29` FOREIGN KEY (`id_tipo_servicio`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Servicio` ADD CONSTRAINT `fk_sgr_30` FOREIGN KEY (`id_subtipo_servicio`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_31` FOREIGN KEY (`id_actividad`) REFERENCES `Actividad` (`id_actividad`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_32` FOREIGN KEY (`id_servicio`) REFERENCES `Servicio` (`id_servicio`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_33` FOREIGN KEY (`id_persona`) REFERENCES `PersonaSolicitante` (`id_persona`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_34` FOREIGN KEY (`id_tipo_atencion`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_35` FOREIGN KEY (`id_sub_atencion`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_36` FOREIGN KEY (`id_delegacion`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_37` FOREIGN KEY (`creado_por_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_38` FOREIGN KEY (`id_caso_social`) REFERENCES `CasoSocial` (`id_caso_social`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Compromiso` ADD CONSTRAINT `fk_sgr_39` FOREIGN KEY (`id_actividad_origen`) REFERENCES `Actividad` (`id_actividad`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Compromiso` ADD CONSTRAINT `fk_sgr_40` FOREIGN KEY (`id_persona_solicitante`) REFERENCES `PersonaSolicitante` (`id_persona`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Compromiso` ADD CONSTRAINT `fk_sgr_41` FOREIGN KEY (`id_territorio`) REFERENCES `Territorio` (`id_territorio`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Compromiso` ADD CONSTRAINT `fk_sgr_42` FOREIGN KEY (`id_area_apoyo`) REFERENCES `AreaApoyo` (`id_area_apoyo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Compromiso` ADD CONSTRAINT `fk_sgr_43` FOREIGN KEY (`id_estado_actual`) REFERENCES `EstadoCompromiso` (`id_estado_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AsignacionCompromiso` ADD CONSTRAINT `fk_sgr_44` FOREIGN KEY (`id_compromiso`) REFERENCES `Compromiso` (`id_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AsignacionCompromiso` ADD CONSTRAINT `fk_sgr_45` FOREIGN KEY (`id_funcionario_responsable`) REFERENCES `Funcionario` (`id_funcionario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AsignacionCompromiso` ADD CONSTRAINT `fk_sgr_46` FOREIGN KEY (`asignado_por_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `HistorialEstadoCompromiso` ADD CONSTRAINT `fk_sgr_47` FOREIGN KEY (`id_compromiso`) REFERENCES `Compromiso` (`id_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `HistorialEstadoCompromiso` ADD CONSTRAINT `fk_sgr_48` FOREIGN KEY (`id_estado_anterior`) REFERENCES `EstadoCompromiso` (`id_estado_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `HistorialEstadoCompromiso` ADD CONSTRAINT `fk_sgr_49` FOREIGN KEY (`id_estado_nuevo`) REFERENCES `EstadoCompromiso` (`id_estado_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `HistorialEstadoCompromiso` ADD CONSTRAINT `fk_sgr_50` FOREIGN KEY (`id_usuario_autor`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `SeguimientoCompromiso` ADD CONSTRAINT `fk_sgr_51` FOREIGN KEY (`id_compromiso`) REFERENCES `Compromiso` (`id_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `SeguimientoCompromiso` ADD CONSTRAINT `fk_sgr_52` FOREIGN KEY (`id_usuario_autor`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Evidencia` ADD CONSTRAINT `fk_sgr_53` FOREIGN KEY (`id_actividad`) REFERENCES `Actividad` (`id_actividad`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Evidencia` ADD CONSTRAINT `fk_sgr_54` FOREIGN KEY (`cargado_por_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ValidacionEvidencia` ADD CONSTRAINT `fk_sgr_55` FOREIGN KEY (`id_evidencia`) REFERENCES `Evidencia` (`id_evidencia`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ValidacionEvidencia` ADD CONSTRAINT `fk_sgr_56` FOREIGN KEY (`id_verificador_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Alerta` ADD CONSTRAINT `fk_sgr_57` FOREIGN KEY (`id_compromiso`) REFERENCES `Compromiso` (`id_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Alerta` ADD CONSTRAINT `fk_sgr_58` FOREIGN KEY (`id_resultado`) REFERENCES `ResultadoIndicador` (`id_resultado`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Alerta` ADD CONSTRAINT `fk_sgr_59` FOREIGN KEY (`id_usuario_destino`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Alerta` ADD CONSTRAINT `fk_sgr_60` FOREIGN KEY (`id_regla_alerta`) REFERENCES `ReglaAlerta` (`id_regla_alerta`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Alerta` ADD CONSTRAINT `fk_sgr_61` FOREIGN KEY (`id_evidencia`) REFERENCES `Evidencia` (`id_evidencia`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Alerta` ADD CONSTRAINT `fk_sgr_62` FOREIGN KEY (`id_funcionario`) REFERENCES `Funcionario` (`id_funcionario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Conversacion` ADD CONSTRAINT `fk_sgr_63` FOREIGN KEY (`id_actividad`) REFERENCES `Actividad` (`id_actividad`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Conversacion` ADD CONSTRAINT `fk_sgr_64` FOREIGN KEY (`id_compromiso`) REFERENCES `Compromiso` (`id_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Conversacion` ADD CONSTRAINT `fk_sgr_65` FOREIGN KEY (`id_evidencia`) REFERENCES `Evidencia` (`id_evidencia`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Mensaje` ADD CONSTRAINT `fk_sgr_66` FOREIGN KEY (`id_conversacion`) REFERENCES `Conversacion` (`id_conversacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Mensaje` ADD CONSTRAINT `fk_sgr_67` FOREIGN KEY (`id_usuario_autor`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Mensaje` ADD CONSTRAINT `fk_sgr_68` FOREIGN KEY (`id_mensaje_padre`) REFERENCES `Mensaje` (`id_mensaje`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `EventoAuditoria` ADD CONSTRAINT `fk_sgr_69` FOREIGN KEY (`id_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `RecuperacionAcceso` ADD CONSTRAINT `fk_sgr_70` FOREIGN KEY (`id_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `CasoSocial` ADD CONSTRAINT `fk_sgr_71` FOREIGN KEY (`id_persona`) REFERENCES `PersonaSolicitante` (`id_persona`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ValidacionCompromiso` ADD CONSTRAINT `fk_sgr_72` FOREIGN KEY (`id_compromiso`) REFERENCES `Compromiso` (`id_compromiso`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ValidacionCompromiso` ADD CONSTRAINT `fk_sgr_73` FOREIGN KEY (`id_verificador_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ReglaAjuste` ADD CONSTRAINT `fk_sgr_74` FOREIGN KEY (`id_version_config`) REFERENCES `VersionConfiguracion` (`id_version_config`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AjusteResultado` ADD CONSTRAINT `fk_sgr_75` FOREIGN KEY (`id_resultado`) REFERENCES `ResultadoIndicador` (`id_resultado`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AjusteResultado` ADD CONSTRAINT `fk_sgr_76` FOREIGN KEY (`id_regla_ajuste`) REFERENCES `ReglaAjuste` (`id_regla_ajuste`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AjusteResultado` ADD CONSTRAINT `fk_sgr_77` FOREIGN KEY (`id_usuario_responsable`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ReglaAlerta` ADD CONSTRAINT `fk_sgr_78` FOREIGN KEY (`id_version_config`) REFERENCES `VersionConfiguracion` (`id_version_config`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `CargoFuncion` ADD CONSTRAINT `fk_sgr_79` FOREIGN KEY (`id_cargo`) REFERENCES `Cargo` (`id_cargo`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `CargoFuncion` ADD CONSTRAINT `fk_sgr_80` FOREIGN KEY (`id_funcion`) REFERENCES `Funcion` (`id_funcion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `VersionEvidencia` ADD CONSTRAINT `fk_sgr_81` FOREIGN KEY (`id_evidencia`) REFERENCES `Evidencia` (`id_evidencia`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `VersionEvidencia` ADD CONSTRAINT `fk_sgr_82` FOREIGN KEY (`cargado_por_usuario`) REFERENCES `Usuario` (`id_usuario`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_83` FOREIGN KEY (`id_sub_atencion`, `id_tipo_atencion`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`, `id_valor_padre`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_84` FOREIGN KEY (`id_caso_social`, `id_persona`) REFERENCES `CasoSocial` (`id_caso_social`, `id_persona`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Servicio` ADD CONSTRAINT `fk_sgr_85` FOREIGN KEY (`id_subtipo_servicio`, `id_tipo_servicio`) REFERENCES `ValorCatalogo` (`id_valor_catalogo`, `id_valor_padre`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Actividad` ADD CONSTRAINT `fk_sgr_86` FOREIGN KEY (`id_territorio`, `id_delegacion`) REFERENCES `Territorio` (`id_territorio`, `id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_87` FOREIGN KEY (`id_actividad`, `id_delegacion`) REFERENCES `Actividad` (`id_actividad`, `id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `AporteIndicador` ADD CONSTRAINT `fk_sgr_88` FOREIGN KEY (`id_configuracion_meta`, `id_asignacion_historica`) REFERENCES `ConfiguracionMeta` (`id_configuracion_meta`, `id_asignacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ResultadoIndicador` ADD CONSTRAINT `fk_sgr_89` FOREIGN KEY (`id_configuracion_meta`, `id_asignacion_historica`) REFERENCES `ConfiguracionMeta` (`id_configuracion_meta`, `id_asignacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Mensaje` ADD CONSTRAINT `fk_sgr_90` FOREIGN KEY (`id_mensaje_padre`, `id_conversacion`) REFERENCES `Mensaje` (`id_mensaje`, `id_conversacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `ValidacionEvidencia` ADD CONSTRAINT `fk_sgr_91` FOREIGN KEY (`id_evidencia`, `version_evidencia`) REFERENCES `VersionEvidencia` (`id_evidencia`, `numero_version`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Atencion` ADD CONSTRAINT `fk_sgr_92` FOREIGN KEY (`id_delegacion_responsable`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Compromiso` ADD CONSTRAINT `fk_sgr_93` FOREIGN KEY (`id_delegacion_origen`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `Compromiso` ADD CONSTRAINT `fk_sgr_94` FOREIGN KEY (`id_delegacion_responsable`) REFERENCES `Delegacion` (`id_delegacion`) ON DELETE RESTRICT ON UPDATE RESTRICT;

CREATE INDEX `ix_Atencion_consulta` ON `Atencion` (`id_delegacion`, `fecha_atencion`, `id_atencion`);

CREATE INDEX `ix_Actividad_consulta` ON `Actividad` (`id_delegacion`, `fecha_actividad`, `id_actividad`);

CREATE INDEX `ix_Compromiso_consulta` ON `Compromiso` (`id_estado_actual`, `fecha_comprometida`, `id_compromiso`);

CREATE INDEX `ix_EventoAuditoria_consulta` ON `EventoAuditoria` (`tipo_entidad`, `identificador_entidad`, `fecha_evento`);

CREATE INDEX `ix_RecuperacionAcceso_consulta` ON `RecuperacionAcceso` (`id_usuario`, `solicitado_en`);

CREATE INDEX `ix_Mensaje_consulta` ON `Mensaje` (`id_conversacion`, `creado_en`, `id_mensaje`);
