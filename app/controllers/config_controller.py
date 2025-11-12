from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.config_model import ConfigModel

config_bp = Blueprint('configuracion', __name__)

@config_bp.route('/configuracion')
@login_required
def settings():
    config_model = ConfigModel()
    config_usuario = config_model.obtener_config_usuario(current_user.id)
    return render_template('configuracion.html', config_usuario=config_usuario)

# ⚠️ SOLO UNA FUNCIÓN actualizar_tema - ELIMINAR LA DUPLICADA
@config_bp.route('/configuracion/tema')
@login_required
def actualizar_tema():
    tema = request.args.get('tema', 'light')
    config_model = ConfigModel()
    
    # Actualizar tema en base de datos
    success = config_model.actualizar_tema(current_user.id, tema)
    
    if success:
        flash(f'Tema cambiado a modo {"oscuro" if tema == "dark" else "claro"}', 'success')
    else:
        flash('Error al cambiar el tema', 'danger')
    
    # Redirigir a la página anterior
    return redirect(request.referrer or url_for('dashboard.tablero'))

@config_bp.route('/configuracion/cuenta', methods=['POST'])
@login_required
def actualizar_cuenta():
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip()
    
    if nombre and email:
        config_model = ConfigModel()
        if config_model.actualizar_cuenta(current_user.id, nombre, email):
            flash('Cuenta actualizada correctamente', 'success')
        else:
            flash('Error al actualizar la cuenta', 'danger')
    
    return redirect(url_for('configuracion.settings'))

@config_bp.route('/perfil')
@login_required
def perfil():
    config_model = ConfigModel()
    estadisticas = config_model.obtener_estadisticas_usuario(current_user.id)
    actividad_reciente = config_model.obtener_actividad_reciente(current_user.id)
    ultimo_acceso = config_model.obtener_ultimo_acceso(current_user.id)
    
    return render_template('perfil.html', 
                         estadisticas=estadisticas, 
                         actividad_reciente=actividad_reciente,
                         ultimo_acceso=ultimo_acceso)