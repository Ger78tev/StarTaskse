# [file name]: database.py
# [CORRECCIÓN PARA RAILWAY]
import mysql.connector
from mysql.connector import Error
import os

class Database:
    def __init__(self):
        # ⚠️ CORRECCIÓN: Usar variables de entorno específicas de Railway
        self.config = {
            'host': os.environ.get('MYSQLHOST', 'localhost'),
            'user': os.environ.get('MYSQLUSER', 'root'),
            'password': os.environ.get('MYSQLPASSWORD', ''),
            'database': os.environ.get('MYSQLDATABASE', 'startask'),
            'port': int(os.environ.get('MYSQLPORT', '3306')),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'connect_timeout': 30,
            'autocommit': True
        }
        print(f"🔧 Configuración DB: host={self.config['host']}, db={self.config['database']}")
    
    def conectar(self):
        """Establece conexión con la base de datos MySQL"""
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                print(f"✅ Conectado a MySQL en {self.config['host']}")
                return connection
        except Error as e:
            print(f"❌ Error conectando a MySQL: {e}")
            print(f"🔧 Config usada: {self.config['host']}:{self.config['port']}, user: {self.config['user']}, db: {self.config['database']}")
            return None

    # ... resto del código se mantiene igual ...
    
    # ... (el resto del código se mantiene igual)
    
    def crear_base_datos(self):
        """Crea la base de datos si no existe"""
        try:
            # Conectar sin especificar base de datos
            temp_config = self.config.copy()
            temp_config.pop('database', None)
            
            conn = mysql.connector.connect(**temp_config)
            cursor = conn.cursor()
            
            # Crear base de datos
            cursor.execute("CREATE DATABASE IF NOT EXISTS startask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute("USE startask")
            
            # Crear todas las tablas
            self.crear_tablas_completas(conn)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Base de datos y tablas creadas correctamente")
            
        except Error as e:
            print(f"❌ Error creando base de datos: {e}")
    
    def crear_tablas_completas(self, conn=None):
        """Crea todas las tablas necesarias para StarTask"""
        try:
            if conn is None:
                conn = self.conectar()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Tabla de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    rol ENUM('Administrador', 'Líder de Proyecto', 'Colaborador') NOT NULL,
                    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de proyectos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyectos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    fecha_inicio DATE,
                    fecha_fin DATE,
                    estado ENUM('activo', 'inactivo', 'completado') DEFAULT 'activo',
                    id_lider INT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_lider) REFERENCES usuarios(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de tareas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tareas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    descripcion TEXT,
                    id_proyecto INT,
                    id_asignado INT,
                    estado ENUM('pendiente', 'en_progreso', 'completada') DEFAULT 'pendiente',
                    prioridad ENUM('baja', 'media', 'alta') DEFAULT 'media',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_vencimiento DATE,
                    estado_registro ENUM('activo', 'inactivo') DEFAULT 'activo',
                    FOREIGN KEY (id_proyecto) REFERENCES proyectos(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_asignado) REFERENCES usuarios(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de mensajes de chat
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes_chat (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT,
                    mensaje TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado ENUM('activo', 'eliminado') DEFAULT 'activo',
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de configuración de usuario
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_usuario (
                    id_usuario INT PRIMARY KEY,
                    tema VARCHAR(20) DEFAULT 'light',
                    notificaciones_email BOOLEAN DEFAULT TRUE,
                    notificaciones_tareas BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de configuración del sistema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_sistema (
                    id INT PRIMARY KEY DEFAULT 1,
                    nombre VARCHAR(100) DEFAULT 'StarTask',
                    logo_url VARCHAR(255),
                    version VARCHAR(20) DEFAULT '1.0.0'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de notificaciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notificaciones (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT NOT NULL,
                    tipo ENUM('proyecto_asignado', 'fecha_limite', 'nuevo_mensaje', 'tarea_urgente') NOT NULL,
                    titulo VARCHAR(255) NOT NULL,
                    mensaje TEXT NOT NULL,
                    enlace VARCHAR(500),
                    leida TINYINT(1) DEFAULT 0,
                    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                    fecha_limite DATE,
                    prioridad ENUM('baja', 'media', 'alta') DEFAULT 'media',
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
                    INDEX idx_notificaciones_usuario (id_usuario, leida, fecha_creacion)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de historial de actividades
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_actividades (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_usuario INT,
                    accion VARCHAR(200) NOT NULL,
                    tabla_afectada VARCHAR(50),
                    id_registro_afectado INT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de comentarios de tareas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comentarios_tareas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_tarea INT,
                    id_usuario INT,
                    comentario TEXT NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
                    FOREIGN KEY (id_tarea) REFERENCES tareas(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla de miembros de proyecto
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyecto_miembros (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_proyecto INT,
                    id_usuario INT,
                    rol ENUM('Líder', 'Miembro') DEFAULT 'Miembro',
                    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_proyecto_usuario (id_proyecto, id_usuario),
                    FOREIGN KEY (id_proyecto) REFERENCES proyectos(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            if conn:
                conn.commit()
                cursor.close()
                if not conn.in_transaction:
                    conn.close()
            
            print("✅ Todas las tablas creadas/verificadas correctamente")
            return True
            
        except Error as e:
            print(f"❌ Error creando tablas: {e}")
            return False
    
    def verificar_usuarios_existen(self):
        """Verifica si existen usuarios en la base de datos"""
        conn = self.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as count FROM usuarios WHERE estado = 'activo'")
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            return resultado['count'] > 0 if resultado else False
        return False

    def insertar_datos_iniciales(self):
        """Inserta datos iniciales esenciales"""
        try:
            conn = self.conectar()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            # Insertar configuración del sistema
            cursor.execute("""
                INSERT IGNORE INTO config_sistema (id, nombre, version) 
                VALUES (1, 'StarTask', '1.0.0')
            """)
            
            # Insertar usuarios de ejemplo si no existen
            usuarios = [
                (1, 'Gerald Baños', 'gerald@startask.com', 'gerald123', 'Administrador'),
                (2, 'David Salazar', 'david@startask.com', 'david123', 'Líder de Proyecto'),
                (3, 'Sebastian Suarez', 'sebastian@startask.com', 'sebastian123', 'Colaborador')
            ]
            
            for usuario in usuarios:
                cursor.execute("""
                    INSERT IGNORE INTO usuarios (id, nombre, email, password, rol) 
                    VALUES (%s, %s, %s, %s, %s)
                """, usuario)
                
                # Crear configuración para cada usuario
                cursor.execute("INSERT IGNORE INTO config_usuario (id_usuario) VALUES (%s)", (usuario[0],))
            
            # Insertar proyecto de ejemplo
            cursor.execute("""
                INSERT IGNORE INTO proyectos (id, nombre, descripcion, id_lider) 
                VALUES (1, 'Proyecto Demo StarTask', 'Proyecto de demostración del sistema', 2)
            """)
            
            # Insertar tareas de ejemplo
            tareas = [
                (1, 'Diseñar interfaz login', 'Crear diseño moderno para página de login', 1, 3, 'pendiente', 'alta'),
                (2, 'Configurar base de datos', 'Implementar modelos y conexión DB', 1, 2, 'en_progreso', 'alta'),
                (3, 'Documentación del sistema', 'Redactar manual de usuario', 1, 3, 'pendiente', 'media')
            ]
            
            for tarea in tareas:
                cursor.execute("""
                    INSERT IGNORE INTO tareas (id, titulo, descripcion, id_proyecto, id_asignado, estado, prioridad)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, tarea)
            
            # Actividad inicial
            cursor.execute("""
                INSERT IGNORE INTO historial_actividades (id_usuario, accion) 
                VALUES (1, 'Sistema inicializado correctamente')
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ Datos iniciales insertados correctamente")
            return True
            
        except Error as e:
            print(f"❌ Error insertando datos iniciales: {e}")
            return False
    
    def inicializar(self):
        """Inicializa toda la base de datos de forma automática"""
        print("🔄 INICIALIZANDO BASE DE DATOS STARTASK...")
        
        try:
            # Verificar/Crear base de datos y tablas
            self.crear_base_datos()
            
            # Insertar datos iniciales si no existen usuarios
            if not self.verificar_usuarios_existen():
                self.insertar_datos_iniciales()
                print("✅ Datos iniciales insertados")
            else:
                print("ℹ️  La base de datos ya contiene datos")
                
            print("🎉 ¡Base de datos StarTask lista para usar!")
            return True
            
        except Exception as e:
            print(f"❌ Error crítico en inicialización: {e}")
            return False

# Función para inicializar la base de datos automáticamente al importar
def inicializar_base_datos():
    """Función para inicializar la base de datos automáticamente"""
    db = Database()
    return db.inicializar()

# Si se ejecuta este archivo directamente, inicializar la base de datos
if __name__ == "__main__":

    inicializar_base_datos()
