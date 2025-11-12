from functools import wraps
from flask import redirect, url_for, flash, render_template
from flask_login import current_user

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor inicia sesión para acceder a esta página', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.rol not in roles:
                return render_template('403.html'), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def registrar_actividad(id_usuario, accion, tabla_afectada=None, id_registro_afectado=None):
    """Registra actividad en el historial"""
    from app.utils.database import Database
    db = Database()
    conn = db.conectar()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO historial_actividades (id_usuario, accion, tabla_afectada, id_registro_afectado) VALUES (%s, %s, %s, %s)",
                (id_usuario, accion, tabla_afectada, id_registro_afectado)
            )
            conn.commit()
        except Exception as e:
            print(f"Error registrando actividad: {e}")
        finally:
            cursor.close()
            conn.close()