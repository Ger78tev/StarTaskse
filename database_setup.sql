-- [file name]: database_setup.sql
-- Script de creación completa de la base de datos StarTask
-- Ubicar este archivo en la raíz del proyecto Flask

SET FOREIGN_KEY_CHECKS=0;

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS `startask` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `startask`;

-- Tabla: usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `rol` ENUM('Administrador', 'Líder de Proyecto', 'Colaborador') NOT NULL DEFAULT 'Colaborador',
  `estado` ENUM('activo', 'inactivo') DEFAULT 'activo',
  `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

-- Tabla: proyectos
CREATE TABLE IF NOT EXISTS `proyectos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(200) NOT NULL,
  `descripcion` TEXT NULL,
  `fecha_inicio` DATE NULL,
  `fecha_fin` DATE NULL,
  `estado` ENUM('activo', 'inactivo', 'completado') DEFAULT 'activo',
  `id_lider` INT NULL,
  `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_lider`) REFERENCES `usuarios`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabla: tareas
CREATE TABLE IF NOT EXISTS `tareas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(200) NOT NULL,
  `descripcion` TEXT NULL,
  `id_proyecto` INT NULL,
  `id_asignado` INT NULL,
  `estado` ENUM('pendiente', 'en_progreso', 'completada') DEFAULT 'pendiente',
  `prioridad` ENUM('baja', 'media', 'alta') DEFAULT 'media',
  `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `fecha_vencimiento` DATE NULL,
  `estado_registro` ENUM('activo', 'inactivo') DEFAULT 'activo',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_proyecto`) REFERENCES `proyectos`(`id`) ON DELETE SET NULL,
  FOREIGN KEY (`id_asignado`) REFERENCES `usuarios`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabla: proyecto_miembros
CREATE TABLE IF NOT EXISTS `proyecto_miembros` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_proyecto` INT NOT NULL,
  `id_usuario` INT NOT NULL,
  `rol` ENUM('Líder', 'Miembro') DEFAULT 'Miembro',
  `fecha_union` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_proyecto_usuario` (`id_proyecto`, `id_usuario`),
  FOREIGN KEY (`id_proyecto`) REFERENCES `proyectos`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla: comentarios_tareas
CREATE TABLE IF NOT EXISTS `comentarios_tareas` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_tarea` INT NOT NULL,
  `id_usuario` INT NOT NULL,
  `comentario` TEXT NOT NULL,
  `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `estado` ENUM('activo', 'inactivo') DEFAULT 'activo',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_tarea`) REFERENCES `tareas`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla: mensajes_chat
CREATE TABLE IF NOT EXISTS `mensajes_chat` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_usuario` INT NOT NULL,
  `mensaje` TEXT NOT NULL,
  `fecha_creacion` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `estado` ENUM('activo', 'eliminado') DEFAULT 'activo',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla: notificaciones
CREATE TABLE IF NOT EXISTS `notificaciones` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_usuario` INT NOT NULL,
  `tipo` ENUM('proyecto_asignado', 'fecha_limite', 'nuevo_mensaje', 'tarea_urgente') NOT NULL,
  `titulo` VARCHAR(255) NOT NULL,
  `mensaje` TEXT NOT NULL,
  `enlace` VARCHAR(500) NULL,
  `leida` TINYINT(1) DEFAULT 0,
  `fecha_creacion` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `fecha_limite` DATE NULL,
  `prioridad` ENUM('baja', 'media', 'alta') DEFAULT 'media',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  INDEX `idx_notificaciones_usuario` (`id_usuario`, `leida`, `fecha_creacion`)
) ENGINE=InnoDB;

-- Tabla: historial_actividades
CREATE TABLE IF NOT EXISTS `historial_actividades` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `id_usuario` INT NULL,
  `accion` VARCHAR(200) NOT NULL,
  `tabla_afectada` VARCHAR(50) NULL,
  `id_registro_afectado` INT NULL,
  `fecha` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Tabla: config_sistema
CREATE TABLE IF NOT EXISTS `config_sistema` (
  `id` INT NOT NULL DEFAULT 1,
  `nombre` VARCHAR(100) DEFAULT 'StarTask',
  `logo_url` VARCHAR(255) NULL,
  `version` VARCHAR(20) DEFAULT '1.0.0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

-- Tabla: config_usuario
CREATE TABLE IF NOT EXISTS `config_usuario` (
  `id_usuario` INT NOT NULL,
  `tema` VARCHAR(20) DEFAULT 'light',
  `notificaciones_email` TINYINT(1) DEFAULT 1,
  `notificaciones_tareas` TINYINT(1) DEFAULT 1,
  PRIMARY KEY (`id_usuario`),
  FOREIGN KEY (`id_usuario`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Insertar datos iniciales
INSERT IGNORE INTO `config_sistema` (`id`, `nombre`, `logo_url`, `version`) VALUES 
(1, 'StarTask', NULL, '1.0.0');

-- Usuarios de ejemplo
INSERT IGNORE INTO `usuarios` (`id`, `nombre`, `email`, `password`, `rol`, `estado`) VALUES 
(1, 'Gerald Baños', 'gerald@startask.com', 'gerald123', 'Administrador', 'activo'),
(2, 'David Salazar', 'david@startask.com', 'david123', 'Líder de Proyecto', 'activo'),
(3, 'Sebastian Suarez', 'sebastian@startask.com', 'sebastian123', 'Colaborador', 'activo');

-- Configuración de usuarios
INSERT IGNORE INTO `config_usuario` (`id_usuario`, `tema`, `notificaciones_email`, `notificaciones_tareas`) VALUES 
(1, 'dark', 1, 1),
(2, 'light', 1, 1),
(3, 'light', 1, 1);

-- Proyectos de ejemplo
INSERT IGNORE INTO `proyectos` (`id`, `nombre`, `descripcion`, `fecha_inicio`, `fecha_fin`, `id_lider`) VALUES 
(1, 'Proyecto Demo StarTask', 'Proyecto de demostración del sistema', '2025-10-09', '2025-11-08', 2);

-- Tareas de ejemplo
INSERT IGNORE INTO `tareas` (`id`, `titulo`, `descripcion`, `id_proyecto`, `id_asignado`, `estado`, `prioridad`) VALUES 
(1, 'Diseñar interfaz login', 'Crear diseño moderno para página de login', 1, 3, 'pendiente', 'alta'),
(2, 'Configurar base de datos', 'Implementar modelos y conexión DB', 1, 2, 'en_progreso', 'media'),
(3, 'Documentación del sistema', 'Redactar manual de usuario', 1, 3, 'pendiente', 'baja');

-- Actividad inicial
INSERT IGNORE INTO `historial_actividades` (`id_usuario`, `accion`) VALUES 
(1, 'Sistema inicializado');

SET FOREIGN_KEY_CHECKS=1;

SELECT '✅ Base de datos StarTask creada exitosamente!' as Mensaje;