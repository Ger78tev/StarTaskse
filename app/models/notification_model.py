# [file name]: notification_model.py
from app.utils.database import Database
from datetime import datetime, timedelta

class NotificationModel:
    def __init__(self):
        self.db = Database()
    
    def crear_notificacion(self, id_usuario, tipo, titulo, mensaje, enlace=None, fecha_limite=None, prioridad='media'):
        """Crea una nueva notificación"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notificaciones (id_usuario, tipo, titulo, mensaje, enlace, fecha_limite, prioridad)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_usuario, tipo, titulo, mensaje, enlace, fecha_limite, prioridad))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def obtener_notificaciones_usuario(self, id_usuario, limite=10):
        """Obtiene las notificaciones de un usuario"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM notificaciones 
                WHERE id_usuario = %s 
                ORDER BY leida ASC, fecha_creacion DESC 
                LIMIT %s
            """, (id_usuario, limite))
            notificaciones = cursor.fetchall()
            cursor.close()
            conn.close()
            return notificaciones
        return []
    
    def contar_no_leidas(self, id_usuario):
        """Cuenta las notificaciones no leídas de un usuario"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM notificaciones 
                WHERE id_usuario = %s AND leida = FALSE
            """, (id_usuario,))
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count
        return 0
    
    def marcar_como_leida(self, id_notificacion, id_usuario):
        """Marca una notificación como leída"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notificaciones 
                SET leida = TRUE 
                WHERE id = %s AND id_usuario = %s
            """, (id_notificacion, id_usuario))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def marcar_todas_leidas(self, id_usuario):
        """Marca todas las notificaciones como leídas"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notificaciones 
                SET leida = TRUE 
                WHERE id_usuario = %s AND leida = FALSE
            """, (id_usuario,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def eliminar_notificacion(self, id_notificacion, id_usuario):
        """Elimina una notificación"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM notificaciones 
                WHERE id = %s AND id_usuario = %s
            """, (id_notificacion, id_usuario))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False