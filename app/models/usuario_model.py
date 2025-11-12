# [file name]: usuario_model.py
# [CORRECCIÓN COMPLETA]
from app.utils.database import Database
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, nombre, email, password, rol, estado='activo', fecha_creacion=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password = password
        self.rol = rol
        self.estado = estado
        self.fecha_creacion = fecha_creacion

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.estado == 'activo'

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

class UsuarioModel:
    def __init__(self):
        self.db = Database()
    
    def obtener_por_email(self, email):
        """Obtiene un usuario por su email - CORREGIDO"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s AND estado = 'activo'", (email,))
            usuario_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if usuario_data:
                return User(
                    usuario_data['id'], 
                    usuario_data['nombre'], 
                    usuario_data['email'], 
                    usuario_data['password'],
                    usuario_data['rol'], 
                    usuario_data['estado'],
                    usuario_data['fecha_creacion']
                )
            return None
        return None
    
    def obtener_por_id(self, id_usuario):
        """Obtiene usuario por ID - CORREGIDO"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s AND estado = 'activo'", (id_usuario,))
            usuario_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if usuario_data:
                return User(
                    usuario_data['id'], 
                    usuario_data['nombre'], 
                    usuario_data['email'], 
                    usuario_data['password'],
                    usuario_data['rol'], 
                    usuario_data['estado'],
                    usuario_data['fecha_creacion']
                )
            return None
        return None
    
    def verificar_login(self, email, password):
        """Verifica credenciales de login - CORREGIDO"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s AND estado = 'activo'", (email,))
            usuario_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if usuario_data and usuario_data['password'] == password:
                return User(
                    usuario_data['id'], 
                    usuario_data['nombre'], 
                    usuario_data['email'], 
                    usuario_data['password'],
                    usuario_data['rol'], 
                    usuario_data['estado'],
                    usuario_data['fecha_creacion']
                )
        return None
    
    def obtener_usuarios_activos(self):
        """Obtiene todos los usuarios activos"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, email, rol, password, fecha_creacion FROM usuarios WHERE estado = 'activo'")
            usuarios_data = cursor.fetchall()
            cursor.close()
            conn.close()
            
            usuarios = []
            for usuario_data in usuarios_data:
                usuarios.append(User(
                    usuario_data['id'], 
                    usuario_data['nombre'], 
                    usuario_data['email'], 
                    usuario_data['password'],
                    usuario_data['rol'],
                    'activo',
                    usuario_data['fecha_creacion']
                ))
            return usuarios
        return []
    
    def crear(self, nombre, email, password, rol='Colaborador'):
        """Crea un nuevo usuario - MEJORADO"""
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
                if cursor.fetchone():
                    return False, "El email ya está registrado"
                
                cursor.execute("""
                    INSERT INTO usuarios (nombre, email, password, rol)
                    VALUES (%s, %s, %s, %s)
                """, (nombre, email, password, rol))
                
                conn.commit()
                cursor.close()
                conn.close()
                return True, "Usuario creado exitosamente"
                
            except Exception as e:
                conn.rollback()
                cursor.close()
                conn.close()
                return False, f"Error al crear usuario: {str(e)}"
        return False, "Error de conexión a la base de datos"