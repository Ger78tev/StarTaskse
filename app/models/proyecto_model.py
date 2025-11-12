from app.utils.database import Database

class ProyectoModel:
    def __init__(self):
        self.db = Database()
    
    def obtener_todos(self):
        """Obtiene todos los proyectos activos"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, u.nombre as lider_nombre 
                FROM proyectos p 
                LEFT JOIN usuarios u ON p.id_lider = u.id 
                WHERE p.estado = 'activo'
                ORDER BY p.fecha_creacion DESC
            """)
            proyectos = cursor.fetchall()
            cursor.close()
            conn.close()
            return proyectos
        return []
    
    def obtener_por_usuario(self, id_usuario):
        """Obtiene proyectos visibles para un usuario específico"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT DISTINCT p.*, u.nombre as lider_nombre 
                FROM proyectos p 
                LEFT JOIN usuarios u ON p.id_lider = u.id 
                LEFT JOIN tareas t ON p.id = t.id_proyecto 
                WHERE p.estado = 'activo' AND t.id_asignado = %s
                ORDER BY p.fecha_creacion DESC
            """, (id_usuario,))
            proyectos = cursor.fetchall()
            cursor.close()
            conn.close()
            return proyectos
        return []
    
    def obtener_por_id(self, id_proyecto):
        """Obtiene un proyecto por ID"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM proyectos WHERE id = %s", (id_proyecto,))
            proyecto = cursor.fetchone()
            cursor.close()
            conn.close()
            return proyecto
        return None
    
    def crear(self, nombre, descripcion, id_lider):
        """Crea un nuevo proyecto"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO proyectos (nombre, descripcion, id_lider)
                VALUES (%s, %s, %s)
            """, (nombre, descripcion, id_lider))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def actualizar(self, id_proyecto, nombre, descripcion):
        """Actualiza un proyecto existente"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE proyectos 
                SET nombre = %s, descripcion = %s
                WHERE id = %s
            """, (nombre, descripcion, id_proyecto))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def eliminar(self, id_proyecto):
        """Elimina un proyecto (cambia estado a inactivo)"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE proyectos SET estado = 'inactivo' WHERE id = %s", (id_proyecto,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        return False
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas de proyectos"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as total FROM proyectos WHERE estado = 'activo'")
            total_proyectos = cursor.fetchone()
            
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM proyectos 
                WHERE estado = 'activo' 
                AND fecha_creacion >= DATE_SUB(NOW(), INTERVAL 1 WEEK)
            """)
            proyectos_esta_semana = cursor.fetchone()
            
            cursor.execute("""
                SELECT p.*, u.nombre as lider_nombre 
                FROM proyectos p 
                LEFT JOIN usuarios u ON p.id_lider = u.id 
                WHERE p.estado = 'activo' 
                ORDER BY p.fecha_creacion DESC 
                LIMIT 5
            """)
            proyectos_recientes = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'total_proyectos': total_proyectos['total'],
                'proyectos_esta_semana': proyectos_esta_semana['total'],
                'proyectos_recientes': proyectos_recientes
            }
        return {'total_proyectos': 0, 'proyectos_esta_semana': 0, 'proyectos_recientes': []}
    
    def obtener_recientes(self, limite=5):
        """Obtiene proyectos recientes"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.*, u.nombre as lider_nombre 
                FROM proyectos p 
                LEFT JOIN usuarios u ON p.id_lider = u.id 
                WHERE p.estado = 'activo' 
                ORDER BY p.fecha_creacion DESC 
                LIMIT %s
            """, (limite,))
            proyectos = cursor.fetchall()
            cursor.close()
            conn.close()
            return proyectos
        return []