# [file name]: config_model.py
# [corrección completa]
from app.utils.database import Database
from datetime import datetime, timedelta

class ConfigModel:
    def __init__(self):
        self.db = Database()
    
    def crear_tablas_config(self):
        """Crea las tablas de configuración si no existen"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            
            # Configuración de usuario
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_usuario (
                    id_usuario INT PRIMARY KEY,
                    tema VARCHAR(20) DEFAULT 'auto',
                    notificaciones_email BOOLEAN DEFAULT TRUE,
                    notificaciones_tareas BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
                )
            """)
            
            # Configuración del sistema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config_sistema (
                    id INT PRIMARY KEY DEFAULT 1,
                    nombre VARCHAR(100) DEFAULT 'StarTask',
                    logo_url VARCHAR(255),
                    version VARCHAR(20) DEFAULT '1.0.0'
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
    
    def obtener_config_usuario(self, id_usuario):
        """Obtiene la configuración del usuario"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM config_usuario WHERE id_usuario = %s", (id_usuario,))
            config = cursor.fetchone()
            if not config:
                # Crear configuración por defecto
                cursor.execute("INSERT INTO config_usuario (id_usuario) VALUES (%s)", (id_usuario,))
                conn.commit()
                cursor.execute("SELECT * FROM config_usuario WHERE id_usuario = %s", (id_usuario,))
                config = cursor.fetchone()
            cursor.close()
            conn.close()
            return config
        return None
    
    def obtener_config_sistema(self):
        """Obtiene la configuración del sistema"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM config_sistema WHERE id = 1")
            config = cursor.fetchone()
            if not config:
                # Crear configuración por defecto
                cursor.execute("INSERT INTO config_sistema (id, nombre) VALUES (1, 'StarTask')")
                conn.commit()
                cursor.execute("SELECT * FROM config_sistema WHERE id = 1")
                config = cursor.fetchone()
            cursor.close()
            conn.close()
            return config
        return {'id': 1, 'nombre': 'StarTask', 'logo_url': None}
    
    def actualizar_tema(self, id_usuario, tema):
        """Actualiza el tema del usuario"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE config_usuario SET tema = %s WHERE id_usuario = %s", (tema, id_usuario))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def actualizar_notificaciones(self, id_usuario, notificaciones_email, notificaciones_tareas):
        """Actualiza las preferencias de notificaciones"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE config_usuario 
                SET notificaciones_email = %s, notificaciones_tareas = %s 
                WHERE id_usuario = %s
            """, (notificaciones_email, notificaciones_tareas, id_usuario))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def actualizar_cuenta(self, id_usuario, nombre, email):
        """Actualiza la información de la cuenta del usuario"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            # Verificar si el email ya existe en otro usuario
            cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", (email, id_usuario))
            if cursor.fetchone():
                return False, "El email ya está en uso por otro usuario"
            
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = %s, email = %s 
                WHERE id = %s
            """, (nombre, email, id_usuario))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Cuenta actualizada correctamente"
        return False, "Error de conexión a la base de datos"
    
    def actualizar_config_sistema(self, nombre, logo_url):
        """Actualiza la configuración del sistema"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE config_sistema 
                SET nombre = %s, logo_url = %s 
                WHERE id = 1
            """, (nombre, logo_url))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def obtener_estadisticas_usuario(self, id_usuario):
        """Obtiene estadísticas del usuario"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as tareas_asignadas FROM tareas WHERE id_asignado = %s AND estado_registro = 'activo'", (id_usuario,))
            tareas_asignadas = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as tareas_completadas FROM tareas WHERE id_asignado = %s AND estado = 'completada' AND estado_registro = 'activo'", (id_usuario,))
            tareas_completadas = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(DISTINCT id_proyecto) as proyectos_participando FROM tareas WHERE id_asignado = %s AND estado_registro = 'activo'", (id_usuario,))
            proyectos_participando = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'tareas_asignadas': tareas_asignadas['tareas_asignadas'] if tareas_asignadas else 0,
                'tareas_completadas': tareas_completadas['tareas_completadas'] if tareas_completadas else 0,
                'proyectos_participando': proyectos_participando['proyectos_participando'] if proyectos_participando else 0
            }
        return {'tareas_asignadas': 0, 'tareas_completadas': 0, 'proyectos_participando': 0}
    
    def obtener_actividad_reciente(self, id_usuario, limite=5):
        """Obtiene la actividad reciente del usuario desde la base de datos"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT accion, fecha, tabla_afectada, id_registro_afectado
                FROM historial_actividades 
                WHERE id_usuario = %s 
                ORDER BY fecha DESC 
                LIMIT %s
            """, (id_usuario, limite))
            actividades = cursor.fetchall()
            cursor.close()
            conn.close()
            
            actividades_formateadas = []
            for actividad in actividades:
                icono = self._obtener_icono_actividad(actividad['accion'])
                fecha_formateada = self._formatear_fecha(actividad['fecha'])
                actividades_formateadas.append({
                    'icono': icono,
                    'descripcion': actividad['accion'],
                    'fecha': fecha_formateada
                })
            
            return actividades_formateadas
        
        # Datos de ejemplo si no hay conexión
        return [
            {'icono': 'plus', 'descripcion': 'Nueva tarea creada: "Diseñar interfaz"', 'fecha': 'Hace 2 horas'},
            {'icono': 'check', 'descripcion': 'Tarea completada: "Configurar BD"', 'fecha': 'Hace 1 día'},
            {'icono': 'comment', 'descripcion': 'Mensaje enviado en el chat', 'fecha': 'Hace 2 días'}
        ]
    
    def _obtener_icono_actividad(self, accion):
        """Determina el icono basado en el tipo de actividad"""
        accion_lower = accion.lower()
        if 'inicio de sesión' in accion_lower:
            return 'sign-in-alt'
        elif 'creó' in accion_lower or 'nueva' in accion_lower:
            return 'plus'
        elif 'editó' in accion_lower or 'actualizó' in accion_lower:
            return 'edit'
        elif 'eliminó' in accion_lower:
            return 'trash'
        elif 'completada' in accion_lower or 'completó' in accion_lower:
            return 'check-circle'
        elif 'mensaje' in accion_lower or 'chat' in accion_lower:
            return 'comment'
        else:
            return 'stream'
    
    def _formatear_fecha(self, fecha):
        """Formatea la fecha para mostrarla de manera relativa"""
        ahora = datetime.now()
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        
        diferencia = ahora - fecha
        
        if diferencia < timedelta(minutes=1):
            return 'Hace unos segundos'
        elif diferencia < timedelta(hours=1):
            minutos = int(diferencia.seconds / 60)
            return f'Hace {minutos} minutos'
        elif diferencia < timedelta(days=1):
            horas = int(diferencia.seconds / 3600)
            return f'Hace {horas} horas'
        elif diferencia < timedelta(days=7):
            dias = diferencia.days
            return f'Hace {dias} días'
        else:
            return fecha.strftime('%d/%m/%Y')
    
    def obtener_ultimo_acceso(self, id_usuario):
        """Obtiene el último acceso del usuario desde el historial"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT fecha 
                FROM historial_actividades 
                WHERE id_usuario = %s AND accion LIKE '%Inicio de sesión%'
                ORDER BY fecha DESC 
                LIMIT 1
            """, (id_usuario,))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            if resultado:
                return resultado['fecha']
        return datetime.now()