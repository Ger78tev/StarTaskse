# [file name]: auth_controller.py
# [CORRECCIÓN COMPLETA]
from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models.usuario_model import UsuarioModel
from app.utils.helpers import registrar_actividad

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Página principal - redirige a login"""
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login - CORREGIDO"""
    # ⚠️ CORRECCIÓN: Verificar si ya está autenticado
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.tablero'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Por favor, completa todos los campos', 'danger')
            return render_template('login.html')
        
        usuario_model = UsuarioModel()
        usuario = usuario_model.verificar_login(email, password)
        
        if usuario:
            # ⚠️ CORRECCIÓN: Usar login_user correctamente
            login_user(usuario, remember=True)
            registrar_actividad(usuario.id, 'Inicio de sesión exitoso')
            flash(f'¡Bienvenido {usuario.nombre}!', 'success')
            
            # Redirigir a la página que intentaba acceder o al dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.tablero'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro - CORREGIDO"""
    # ⚠️ CORRECCIÓN: Verificar si ya está autenticado
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.tablero'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirmar_password = request.form.get('confirmar_password', '').strip()
        
        # Validaciones
        if not all([nombre, email, password, confirmar_password]):
            flash('Por favor, completa todos los campos', 'danger')
            return render_template('registro.html')
        
        if password != confirmar_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('registro.html')
        
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'danger')
            return render_template('registro.html')
        
        usuario_model = UsuarioModel()
        resultado, mensaje = usuario_model.crear(nombre, email, password, 'Colaborador')
        
        if resultado:
            registrar_actividad(None, f'Usuario registrado: {email}', 'usuarios')
            flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(mensaje, 'danger')
        
    return render_template('registro.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout - CORREGIDO"""
    user_id = current_user.id
    user_name = current_user.nombre
    logout_user()
    registrar_actividad(user_id, 'Cierre de sesión')
    flash(f'Has cerrado sesión correctamente. ¡Hasta pronto {user_name}!', 'info')
    return redirect(url_for('auth.login'))