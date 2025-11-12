# [file name]: chat_model.py
from app.utils.database import Database
from datetime import datetime

class ChatModel:
    def __init__(self):
        self.db = Database()
    
    def enviar_mensaje(self, id_usuario, mensaje):
        """Envía un mensaje al chat - CORREGIDO"""
        try:
            conn = self.db.conectar()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mensajes_chat (id_usuario, mensaje, fecha_creacion)
                    VALUES (%s, %s, %s)
                """, (id_usuario, mensaje, datetime.now()))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"✅ Mensaje guardado: {mensaje}")  # Debug
                return True
            return False
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return False
    
    def obtener_mensajes(self, limite=50):
        """Obtiene los últimos mensajes del chat - CORREGIDO"""
        try:
            conn = self.db.conectar()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT 
                        mc.*, 
                        u.nombre as usuario_nombre, 
                        u.rol as usuario_rol,
                        DATE_FORMAT(mc.fecha_creacion, '%%H:%%i') as hora
                    FROM mensajes_chat mc
                    LEFT JOIN usuarios u ON mc.id_usuario = u.id
                    WHERE mc.estado = 'activo'
                    ORDER BY mc.fecha_creacion ASC
                    LIMIT %s
                """, (limite,))
                mensajes = cursor.fetchall()
                cursor.close()
                conn.close()
                print(f"✅ Mensajes obtenidos: {len(mensajes)}")  # Debug
                return mensajes
            return []
        except Exception as e:
            print(f"❌ Error obteniendo mensajes: {e}")
            return []
    
    def eliminar_mensaje(self, id_mensaje, id_usuario):
        """Elimina un mensaje"""
        try:
            conn = self.db.conectar()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE mensajes_chat 
                    SET estado = 'eliminado' 
                    WHERE id = %s AND id_usuario = %s
                """, (id_mensaje, id_usuario))
                conn.commit()
                affected = cursor.rowcount
                cursor.close()
                conn.close()
                return affected > 0
            return False
        except Exception as e:
            print(f"❌ Error eliminando mensaje: {e}")
            return False