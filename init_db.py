#!/usr/bin/env python3
"""
init_db.py
Crea la base de datos `startask`, tablas y datos iniciales de forma idempotente.
Diseñado para usarse en Railway (o localmente) usando variables de entorno.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error

# -----------------------
# Config (leer env)
# -----------------------
DB_NAME = os.getenv("MYSQLDATABASE", "startask")
config = {
    "host": os.getenv("MYSQLHOST", "localhost"),
    "user": os.getenv("MYSQLUSER", "root"),
    "password": os.getenv("MYSQLPASSWORD", ""),
    "port": int(os.getenv("MYSQLPORT", 3306)),
    # don't include database here for initial connection
}

def connect_no_db():
    return mysql.connector.connect(**config)

def connect_with_db():
    cfg = config.copy()
    cfg["database"] = DB_NAME
    return mysql.connector.connect(**cfg)

# -----------------------
# Statements
# -----------------------
CREATE_DB_SQL = f"""
CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
"""

# Table creation statements (ordered to satisfy FKs)
TABLES = [
# usuarios
"""
CREATE TABLE IF NOT EXISTS usuarios (
  id INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  rol ENUM('Administrador','Líder de Proyecto','Colaborador') NOT NULL,
  estado ENUM('activo','inactivo') DEFAULT 'activo',
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# proyectos
"""
CREATE TABLE IF NOT EXISTS proyectos (
  id INT NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(200) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  fecha_inicio DATE DEFAULT NULL,
  fecha_fin DATE DEFAULT NULL,
  estado ENUM('activo','inactivo','completado') DEFAULT 'activo',
  id_lider INT DEFAULT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY id_lider (id_lider),
  CONSTRAINT proyectos_ibfk_1 FOREIGN KEY (id_lider) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# tareas
"""
CREATE TABLE IF NOT EXISTS tareas (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(200) NOT NULL,
  descripcion TEXT DEFAULT NULL,
  id_proyecto INT DEFAULT NULL,
  id_asignado INT DEFAULT NULL,
  estado ENUM('pendiente','en_progreso','completada') DEFAULT 'pendiente',
  prioridad ENUM('baja','media','alta') DEFAULT 'media',
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_vencimiento DATE DEFAULT NULL,
  estado_registro ENUM('activo','inactivo') DEFAULT 'activo',
  PRIMARY KEY (id),
  KEY id_proyecto (id_proyecto),
  KEY id_asignado (id_asignado),
  CONSTRAINT tareas_ibfk_1 FOREIGN KEY (id_proyecto) REFERENCES proyectos (id),
  CONSTRAINT tareas_ibfk_2 FOREIGN KEY (id_asignado) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# comentarios_tareas
"""
CREATE TABLE IF NOT EXISTS comentarios_tareas (
  id INT NOT NULL AUTO_INCREMENT,
  id_tarea INT DEFAULT NULL,
  id_usuario INT DEFAULT NULL,
  comentario TEXT NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado ENUM('activo','inactivo') DEFAULT 'activo',
  PRIMARY KEY (id),
  KEY id_tarea (id_tarea),
  KEY id_usuario (id_usuario),
  CONSTRAINT comentarios_tareas_ibfk_1 FOREIGN KEY (id_tarea) REFERENCES tareas (id),
  CONSTRAINT comentarios_tareas_ibfk_2 FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# config_sistema
"""
CREATE TABLE IF NOT EXISTS config_sistema (
  id INT NOT NULL DEFAULT 1,
  nombre VARCHAR(100) DEFAULT 'StarTask',
  logo_url VARCHAR(255) DEFAULT NULL,
  version VARCHAR(20) DEFAULT '1.0.0',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# config_usuario
"""
CREATE TABLE IF NOT EXISTS config_usuario (
  id_usuario INT NOT NULL,
  tema VARCHAR(20) DEFAULT 'auto',
  notificaciones_email TINYINT(1) DEFAULT 1,
  notificaciones_tareas TINYINT(1) DEFAULT 1,
  PRIMARY KEY (id_usuario),
  CONSTRAINT config_usuario_ibfk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# historial_actividades
"""
CREATE TABLE IF NOT EXISTS historial_actividades (
  id INT NOT NULL AUTO_INCREMENT,
  id_usuario INT DEFAULT NULL,
  accion VARCHAR(200) NOT NULL,
  tabla_afectada VARCHAR(50) DEFAULT NULL,
  id_registro_afectado INT DEFAULT NULL,
  fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY id_usuario (id_usuario),
  CONSTRAINT historial_actividades_ibfk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# mensajes_chat
"""
CREATE TABLE IF NOT EXISTS mensajes_chat (
  id INT NOT NULL AUTO_INCREMENT,
  id_usuario INT DEFAULT NULL,
  mensaje TEXT NOT NULL,
  fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado ENUM('activo','eliminado') DEFAULT 'activo',
  PRIMARY KEY (id),
  KEY id_usuario (id_usuario),
  CONSTRAINT mensajes_chat_ibfk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# notificaciones
"""
CREATE TABLE IF NOT EXISTS notificaciones (
  id INT NOT NULL AUTO_INCREMENT,
  id_usuario INT NOT NULL,
  tipo ENUM('proyecto_asignado','fecha_limite','nuevo_mensaje','tarea_urgente') NOT NULL,
  titulo VARCHAR(255) NOT NULL,
  mensaje TEXT NOT NULL,
  enlace VARCHAR(500) DEFAULT NULL,
  leida TINYINT(1) DEFAULT 0,
  fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
  fecha_limite DATE DEFAULT NULL,
  prioridad ENUM('baja','media','alta') DEFAULT 'media',
  PRIMARY KEY (id),
  KEY idx_notificaciones_usuario (id_usuario, leida, fecha_creacion),
  CONSTRAINT notificaciones_ibfk_1 FOREIGN KEY (id_usuario) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""",
# proyecto_miembros
"""
CREATE TABLE IF NOT EXISTS proyecto_miembros (
  id INT NOT NULL AUTO_INCREMENT,
  id_proyecto INT DEFAULT NULL,
  id_usuario INT DEFAULT NULL,
  rol ENUM('Líder','Miembro') DEFAULT 'Miembro',
  fecha_union TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY unique_proyecto_usuario (id_proyecto,id_usuario),
  KEY id_usuario (id_usuario),
  CONSTRAINT proyecto_miembros_ibfk_1 FOREIGN KEY (id_proyecto) REFERENCES proyectos (id) ON DELETE CASCADE,
  CONSTRAINT proyecto_miembros_ibfk_2 FOREIGN KEY (id_usuario) REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""
]

# Data inserts (idempotente: INSERT IGNORE)
INITS = [
    # config_sistema
    ("INSERT IGNORE INTO config_sistema (id, nombre, logo_url) VALUES (%s, %s, %s);",
     (1, 'StarTask', None)),

    # config_usuario (few examples)
    ("INSERT IGNORE INTO config_usuario (id_usuario, tema, notificaciones_email, notificaciones_tareas) VALUES (%s, %s, %s, %s);",
     (1, 'dark', 1, 1)),
    ("INSERT IGNORE INTO config_usuario (id_usuario, tema, notificaciones_email, notificaciones_tareas) VALUES (%s, %s, %s, %s);",
     (2, 'light', 1, 1)),
    ("INSERT IGNORE INTO config_usuario (id_usuario, tema, notificaciones_email, notificaciones_tareas) VALUES (%s, %s, %s, %s);",
     (3, 'oscuro', 1, 0)),

    # usuarios (samples from your dump)
    ("INSERT IGNORE INTO usuarios (id, nombre, email, password, rol, estado, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s);",
     (1, 'Gerald Baños', 'gerald@startask.com', 'gerald123', 'Administrador', 'activo', '2025-10-10 02:43:23')),
    ("INSERT IGNORE INTO usuarios (id, nombre, email, password, rol, estado, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s);",
     (2, 'David Salazar', 'david@startask.com', 'david123', 'Líder de Proyecto', 'activo', '2025-10-10 02:43:23')),
    ("INSERT IGNORE INTO usuarios (id, nombre, email, password, rol, estado, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s);",
     (3, 'Sebastian Suarez', 'sebastian@startask.com', 'sebastian123', 'Colaborador', 'activo', '2025-10-10 02:43:23')),
    ("INSERT IGNORE INTO usuarios (id, nombre, email, password, rol, estado, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s);",
     (4, '22', 'gerald@gmail.com', '111111', 'Colaborador', 'activo', '2025-11-02 21:44:22')),

    # proyectos
    ("INSERT IGNORE INTO proyectos (id, nombre, descripcion, fecha_inicio, fecha_fin, estado, id_lider, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
     (1, 'Proyecto Demo StarTask', 'Proyecto de demostración del sistema', '2025-10-09', '2025-11-08', 'activo', 2, '2025-10-10 02:43:23')),
    ("INSERT IGNORE INTO proyectos (id, nombre, descripcion, fecha_creacion, estado, id_lider) VALUES (%s, %s, %s, %s, %s, %s);",
     (2, '22', '4', '2025-11-11 02:57:33', 'activo', 2)),

    # tareas
    ("INSERT IGNORE INTO tareas (id, titulo, descripcion, id_proyecto, id_asignado, estado, prioridad, fecha_creacion, fecha_vencimiento, estado_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
     (1, 'Diseñar interfaz login', 'Crear diseño moderno para página de login', 1, 3, 'completada', 'alta', '2025-10-10 02:43:23', None, 'activo')),
    ("INSERT IGNORE INTO tareas (id, titulo, descripcion, id_proyecto, id_asignado, estado, prioridad, fecha_creacion, fecha_vencimiento, estado_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
     (2, 'Configurar base de datos', 'Implementar modelos y conexión DB', 1, 2, 'en_progreso', 'baja', '2025-10-10 02:43:23', '2025-11-13', 'inactivo')),
    ("INSERT IGNORE INTO tareas (id, titulo, descripcion, id_proyecto, id_asignado, estado, prioridad, fecha_creacion, fecha_vencimiento, estado_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
     (3, 'Documentación del sistema', 'Redactar manual de usuario', 1, 3, 'pendiente', 'media', '2025-10-10 02:43:23', None, 'activo')),
    ("INSERT IGNORE INTO tareas (id, titulo, descripcion, id_proyecto, id_asignado, estado, prioridad, fecha_creacion, fecha_vencimiento, estado_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
     (4, 's', 's', 2, 2, 'pendiente', 'alta', '2025-11-12 01:34:37', '2025-11-10', 'activo')),
    ("INSERT IGNORE INTO tareas (id, titulo, descripcion, id_proyecto, id_asignado, estado, prioridad, fecha_creacion, fecha_vencimiento, estado_registro) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
     (5, 'A', 'A', 1, 1, 'pendiente', 'alta', '2025-11-12 01:55:25', '2025-11-19', 'activo')),

    # mensajes_chat (several)
    ("INSERT IGNORE INTO mensajes_chat (id, id_usuario, mensaje, fecha_creacion, estado) VALUES (%s, %s, %s, %s, %s);",
     (1, 2, 'ssss', '2025-11-05 13:46:57', 'activo')),
    ("INSERT IGNORE INTO mensajes_chat (id, id_usuario, mensaje, fecha_creacion, estado) VALUES (%s, %s, %s, %s, %s);",
     (2, 2, 'f', '2025-11-12 01:34:03', 'activo')),
    ("INSERT IGNORE INTO mensajes_chat (id, id_usuario, mensaje, fecha_creacion, estado) VALUES (%s, %s, %s, %s, %s);",
     (3, 2, 'ssss', '2025-11-12 01:35:03', 'activo')),
    ("INSERT IGNORE INTO mensajes_chat (id, id_usuario, mensaje, fecha_creacion, estado) VALUES (%s, %s, %s, %s, %s);",
     (4, 2, 'xxxx', '2025-11-12 03:43:38', 'activo')),
    ("INSERT IGNORE INTO mensajes_chat (id, id_usuario, mensaje, fecha_creacion, estado) VALUES (%s, %s, %s, %s, %s);",
     (5, 2, 'f', '2025-11-12 03:43:46', 'activo')),
    ("INSERT IGNORE INTO mensajes_chat (id, id_usuario, mensaje, fecha_creacion, estado) VALUES (%s, %s, %s, %s, %s);",
     (6, 2, 'aaaa', '2025-11-12 03:43:57', 'activo')),
    ("INSERT IGNORE INTO mensajes_chat (id, id_usuario, mensaje, fecha_creacion, estado) VALUES (%s, %s, %s, %s, %s);",
     (7, 2, 'ssssssssssssssssss', '2025-11-12 03:44:04', 'activo')),

    # historial_actividades (a couple of sample rows)
    ("INSERT IGNORE INTO historial_actividades (id, id_usuario, accion, tabla_afectada, id_registro_afectado, fecha) VALUES (%s, %s, %s, %s, %s, %s);",
     (1, 2, 'Inicio de sesión exitoso', None, None, '2025-11-01 12:30:55')),
    ("INSERT IGNORE INTO historial_actividades (id, id_usuario, accion, tabla_afectada, id_registro_afectado, fecha) VALUES (%s, %s, %s, %s, %s, %s);",
     (2, None, 'Usuario registrado: gerald@gmail.com', 'usuarios', None, '2025-11-02 21:44:22')),
    ("INSERT IGNORE INTO historial_actividades (id, id_usuario, accion, tabla_afectada, id_registro_afectado, fecha) VALUES (%s, %s, %s, %s, %s, %s);",
     (59, 2, 'Envió un mensaje en el chat: ssssssssssssssssss...', 'chat', None, '2025-11-12 03:44:04')),
]

# -----------------------
# Runner
# -----------------------
def run():
    con = None
    cur = None
    try:
        # 1) connect without DB, create DB
        conn0 = connect_no_db()
        cur0 = conn0.cursor()
        cur0.execute(CREATE_DB_SQL)
        conn0.commit()
        cur0.close()
        conn0.close()
        print(f"✅ Base `{DB_NAME}` creada o ya existente.")

        # 2) connect with DB and create tables
        con = connect_with_db()
        cur = con.cursor()
        # Ensure using correct DB
        cur.execute(f"USE `{DB_NAME}`;")

        for stmt in TABLES:
            cur.execute(stmt)
        con.commit()
        print("✅ Tablas creadas o ya existentes.")

        # 3) Inserts iniciales (idempotentes)
        for sql, params in INITS:
            try:
                cur.execute(sql, params)
            except Error as e:
                # show but continue (a missing FK or ordering issue will show here)
                print("⚠️ Error insert (continuando):", e, " — Query:", sql, " Params:", params)

        con.commit()
        print("✅ Datos iniciales insertados (si no existían).")

    except Error as e:
        print("❌ Error crítico durante la inicialización:", e)
        sys.exit(1)

    finally:
        if cur:
            cur.close()
        if con and con.is_connected():
            con.close()
        print("🔒 Conexión cerrada.")

if __name__ == "__main__":
    run()
