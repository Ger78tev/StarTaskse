-- StarTask Database for Railway
-- Optimized version based on your existing database

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

-- Create database
CREATE DATABASE IF NOT EXISTS `startask` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `startask`;

-- --------------------------------------------------------

-- Table structure for table `comentarios_tareas`
CREATE TABLE IF NOT EXISTS `comentarios_tareas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_tarea` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `comentario` text NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  PRIMARY KEY (`id`),
  KEY `id_tarea` (`id_tarea`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

-- Table structure for table `config_sistema`
CREATE TABLE IF NOT EXISTS `config_sistema` (
  `id` int(11) NOT NULL DEFAULT 1,
  `nombre` varchar(100) DEFAULT 'StarTask',
  `logo_url` varchar(255) DEFAULT NULL,
  `version` VARCHAR(20) DEFAULT '1.0.0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert data for table `config_sistema`
INSERT IGNORE INTO `config_sistema` (`id`, `nombre`, `logo_url`) VALUES
(1, 'StarTask', NULL);

-- --------------------------------------------------------

-- Table structure for table `config_usuario`
CREATE TABLE IF NOT EXISTS `config_usuario` (
  `id_usuario` int(11) NOT NULL,
  `tema` varchar(20) DEFAULT 'auto',
  `notificaciones_email` tinyint(1) DEFAULT 1,
  `notificaciones_tareas` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert data for table `config_usuario`
INSERT IGNORE INTO `config_usuario` (`id_usuario`, `tema`, `notificaciones_email`, `notificaciones_tareas`) VALUES
(1, 'dark', 1, 1),
(2, 'light', 1, 1),
(3, 'oscuro', 1, 0);

-- --------------------------------------------------------

-- Table structure for table `historial_actividades`
CREATE TABLE IF NOT EXISTS `historial_actividades` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) DEFAULT NULL,
  `accion` varchar(200) NOT NULL,
  `tabla_afectada` varchar(50) DEFAULT NULL,
  `id_registro_afectado` int(11) DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert data for table `historial_actividades`
INSERT IGNORE INTO `historial_actividades` (`id`, `id_usuario`, `accion`, `tabla_afectada`, `id_registro_afectado`, `fecha`) VALUES
(1, 2, 'Inicio de sesión exitoso', NULL, NULL, '2025-11-01 12:30:55'),
(2, NULL, 'Usuario registrado: gerald@gmail.com', 'usuarios', NULL, '2025-11-02 21:44:22'),
-- ... (todos tus datos existentes aquí)
(59, 2, 'Envió un mensaje en el chat: ssssssssssssssssss...', 'chat', NULL, '2025-11-12 03:44:04');

-- --------------------------------------------------------

-- Table structure for table `mensajes_chat`
CREATE TABLE IF NOT EXISTS `mensajes_chat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) DEFAULT NULL,
  `mensaje` text NOT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` enum('activo','eliminado') DEFAULT 'activo',
  PRIMARY KEY (`id`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert data for table `mensajes_chat`
INSERT IGNORE INTO `mensajes_chat` (`id`, `id_usuario`, `mensaje`, `fecha_creacion`, `estado`) VALUES
(1, 2, 'ssss', '2025-11-05 13:46:57', 'activo'),
(2, 2, 'f', '2025-11-12 01:34:03', 'activo'),
(3, 2, 'ssss', '2025-11-12 01:35:03', 'activo'),
(4, 2, 'xxxx', '2025-11-12 03:43:38', 'activo'),
(5, 2, 'f', '2025-11-12 03:43:46', 'activo'),
(6, 2, 'aaaa', '2025-11-12 03:43:57', 'activo'),
(7, 2, 'ssssssssssssssssss', '2025-11-12 03:44:04', 'activo');

-- --------------------------------------------------------

-- Table structure for table `notificaciones`
CREATE TABLE IF NOT EXISTS `notificaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `tipo` enum('proyecto_asignado','fecha_limite','nuevo_mensaje','tarea_urgente') NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `mensaje` text NOT NULL,
  `enlace` varchar(500) DEFAULT NULL,
  `leida` tinyint(1) DEFAULT 0,
  `fecha_creacion` datetime DEFAULT current_timestamp(),
  `fecha_limite` date DEFAULT NULL,
  `prioridad` enum('baja','media','alta') DEFAULT 'media',
  PRIMARY KEY (`id`),
  KEY `idx_notificaciones_usuario` (`id_usuario`,`leida`,`fecha_creacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

-- Table structure for table `proyectos`
CREATE TABLE IF NOT EXISTS `proyectos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(200) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `estado` enum('activo','inactivo','completado') DEFAULT 'activo',
  `id_lider` int(11) DEFAULT NULL,
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `id_lider` (`id_lider`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert data for table `proyectos`
INSERT IGNORE INTO `proyectos` (`id`, `nombre`, `descripcion`, `fecha_inicio`, `fecha_fin`, `estado`, `id_lider`, `fecha_creacion`) VALUES
(1, 'Proyecto Demo StarTask', 'Proyecto de demostración del sistema', '2025-10-09', '2025-11-08', 'activo', 2, '2025-10-10 02:43:23'),
(2, '22', '4', NULL, NULL, 'activo', 2, '2025-11-11 02:57:33');

-- --------------------------------------------------------

-- Table structure for table `proyecto_miembros`
CREATE TABLE IF NOT EXISTS `proyecto_miembros` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_proyecto` int(11) DEFAULT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `rol` enum('Líder','Miembro') DEFAULT 'Miembro',
  `fecha_union` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_proyecto_usuario` (`id_proyecto`,`id_usuario`),
  KEY `id_usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

-- Table structure for table `tareas`
CREATE TABLE IF NOT EXISTS `tareas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `id_proyecto` int(11) DEFAULT NULL,
  `id_asignado` int(11) DEFAULT NULL,
  `estado` enum('pendiente','en_progreso','completada') DEFAULT 'pendiente',
  `prioridad` enum('baja','media','alta') DEFAULT 'media',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `fecha_vencimiento` date DEFAULT NULL,
  `estado_registro` enum('activo','inactivo') DEFAULT 'activo',
  PRIMARY KEY (`id`),
  KEY `id_proyecto` (`id_proyecto`),
  KEY `id_asignado` (`id_asignado`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert data for table `tareas`
INSERT IGNORE INTO `tareas` (`id`, `titulo`, `descripcion`, `id_proyecto`, `id_asignado`, `estado`, `prioridad`, `fecha_creacion`, `fecha_vencimiento`, `estado_registro`) VALUES
(1, 'Diseñar interfaz login', 'Crear diseño moderno para página de login', 1, 3, 'completada', 'alta', '2025-10-10 02:43:23', NULL, 'activo'),
(2, 'Configurar base de datos', 'Implementar modelos y conexión DB', 1, 2, 'en_progreso', 'baja', '2025-10-10 02:43:23', '2025-11-13', 'inactivo'),
(3, 'Documentación del sistema', 'Redactar manual de usuario', 1, 3, 'pendiente', 'media', '2025-10-10 02:43:23', NULL, 'activo'),
(4, 's', 's', 2, 2, 'pendiente', 'alta', '2025-11-12 01:34:37', '2025-11-10', 'activo'),
(5, 'A', 'A', 1, 1, 'pendiente', 'alta', '2025-11-12 01:55:25', '2025-11-19', 'activo');

-- --------------------------------------------------------

-- Table structure for table `usuarios`
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` enum('Administrador','Líder de Proyecto','Colaborador') NOT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `fecha_creacion` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert data for table `usuarios`
INSERT IGNORE INTO `usuarios` (`id`, `nombre`, `email`, `password`, `rol`, `estado`, `fecha_creacion`) VALUES
(1, 'Gerald Baños', 'gerald@startask.com', 'gerald123', 'Administrador', 'activo', '2025-10-10 02:43:23'),
(2, 'David Salazar', 'david@startask.com', 'david123', 'Líder de Proyecto', 'activo', '2025-10-10 02:43:23'),
(3, 'Sebastian Suarez', 'sebastian@startask.com', 'sebastian123', 'Colaborador', 'activo', '2025-10-10 02:43:23'),
(4, '22', 'gerald@gmail.com', '111111', 'Colaborador', 'activo', '2025-11-02 21:44:22');

-- Add foreign key constraints
ALTER TABLE `comentarios_tareas`
  ADD CONSTRAINT `comentarios_tareas_ibfk_1` FOREIGN KEY (`id_tarea`) REFERENCES `tareas` (`id`),
  ADD CONSTRAINT `comentarios_tareas_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`);

ALTER TABLE `config_usuario`
  ADD CONSTRAINT `config_usuario_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`);

ALTER TABLE `historial_actividades`
  ADD CONSTRAINT `historial_actividades_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`);

ALTER TABLE `mensajes_chat`
  ADD CONSTRAINT `mensajes_chat_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`);

ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

ALTER TABLE `proyectos`
  ADD CONSTRAINT `proyectos_ibfk_1` FOREIGN KEY (`id_lider`) REFERENCES `usuarios` (`id`);

ALTER TABLE `proyecto_miembros`
  ADD CONSTRAINT `proyecto_miembros_ibfk_1` FOREIGN KEY (`id_proyecto`) REFERENCES `proyectos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `proyecto_miembros_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

ALTER TABLE `tareas`
  ADD CONSTRAINT `tareas_ibfk_1` FOREIGN KEY (`id_proyecto`) REFERENCES `proyectos` (`id`),
  ADD CONSTRAINT `tareas_ibfk_2` FOREIGN KEY (`id_asignado`) REFERENCES `usuarios` (`id`);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;