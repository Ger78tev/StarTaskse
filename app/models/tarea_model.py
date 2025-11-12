from app.utils.database import Database

class TareaModel:
    def __init__(self):
        self.db = Database()
    
    def obtener_todas(self):
        """Obtiene todas las tareas activas"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.*, p.nombre as proyecto_nombre, u.nombre as asignado_nombre 
                FROM tareas t 
                LEFT JOIN proyectos p ON t.id_proyecto = p.id 
                LEFT JOIN usuarios u ON t.id_asignado = u.id 
                WHERE t.estado_registro = 'activo'
                ORDER BY t.prioridad DESC, t.fecha_vencimiento ASC
            """)
            tareas = cursor.fetchall()
            cursor.close()
            conn.close()
            return tareas
        return []
    
    def obtener_por_usuario(self, id_usuario, limite=None):
        """Obtiene tareas asignadas a un usuario específico"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT t.*, p.nombre as proyecto_nombre 
                FROM tareas t 
                LEFT JOIN proyectos p ON t.id_proyecto = p.id 
                WHERE t.estado_registro = 'activo' AND t.id_asignado = %s
                ORDER BY t.prioridad DESC, t.fecha_vencimiento ASC
            """
            if limite:
                query += " LIMIT %s"
                cursor.execute(query, (id_usuario, limite))
            else:
                cursor.execute(query, (id_usuario,))
            tareas = cursor.fetchall()
            cursor.close()
            conn.close()
            return tareas
        return []
    
    def crear(self, titulo, descripcion, id_proyecto, id_asignado, prioridad='media', fecha_vencimiento=None):
        """Crea una nueva tarea"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tareas (titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def actualizar_estado(self, id_tarea, estado):
        """Actualiza el estado de una tarea"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tareas SET estado = %s WHERE id = %s", (estado, id_tarea))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def actualizar_tarea_completa(self, id_tarea, titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento=None, estado=None):
        """Actualiza una tarea completa incluyendo estado"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            try:
                # Actualizar todos los campos incluyendo estado
                cursor.execute("""
                    UPDATE tareas 
                    SET titulo = %s, descripcion = %s, id_proyecto = %s, id_asignado = %s, 
                        prioridad = %s, fecha_vencimiento = %s, estado = %s
                    WHERE id = %s
                """, (titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento, estado, id_tarea))
                conn.commit()
                cursor.close()
                conn.close()
                return True
            except Exception as e:
                print(f"Error al actualizar tarea: {e}")
                conn.rollback()
                cursor.close()
                conn.close()
            return False
        return False

    def actualizar_tarea(self, id_tarea, titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento=None):
        """Actualiza una tarea completa"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tareas 
                SET titulo = %s, descripcion = %s, id_proyecto = %s, id_asignado = %s, 
                    prioridad = %s, fecha_vencimiento = %s
                WHERE id = %s
            """, (titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento, id_tarea))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def eliminar(self, id_tarea):
        """Elimina una tarea (cambia estado a inactivo)"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tareas SET estado_registro = 'inactivo' WHERE id = %s", (id_tarea,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de tareas"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as total FROM tareas WHERE estado_registro = 'activo'")
            total_tareas = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) as total FROM tareas WHERE estado = 'completada' AND estado_registro = 'activo'")
            tareas_completadas = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'total_tareas': total_tareas['total'],
                'tareas_completadas': tareas_completadas['total']
            }
        return {'total_tareas': 0, 'tareas_completadas': 0}
    
    def contar_tareas_por_estado(self, estado):
        """Cuenta las tareas por estado específico"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM tareas 
                WHERE estado = %s AND estado_registro = 'activo'
            """, (estado,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result['total'] if result else 0
        return 0