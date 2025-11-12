# [file name]: __init__.py
# [CORRECCIÓN COMPLETA]
from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from config import config

login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # ⚠️ CORRECCIÓN: Configuración más robusta de Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    login_manager.session_protection = "strong"
    
    # Registrar blueprints
    from app.controllers.auth_controller import auth_bp
    from app.controllers.dashboard_controller import dashboard_bp
    from app.controllers.proyecto_controller import proyecto_bp
    from app.controllers.tarea_controller import tarea_bp
    from app.controllers.chat_controller import chat_bp
    from app.controllers.reportes_controller import reportes_bp
    from app.controllers.config_controller import config_bp
    from app.controllers.notification_controller import notification_bp
    
    app.register_blueprint(notification_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(proyecto_bp)
    app.register_blueprint(tarea_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(config_bp)
    
    # User loader para Flask-Login - CORREGIDO
    from app.models.usuario_model import UsuarioModel
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            usuario_model = UsuarioModel()
            return usuario_model.obtener_por_id(int(user_id))
        except:
            return None
    
    # Context processor para hacer config_usuario disponible en todos los templates
    @app.context_processor
    def inject_config():
        from app.models.config_model import ConfigModel
        config_model = ConfigModel()
        config_usuario = None
        config_sistema = config_model.obtener_config_sistema()
        
        if current_user.is_authenticated:
            config_usuario = config_model.obtener_config_usuario(current_user.id)
        
        return dict(
            config_usuario=config_usuario,
            config_sistema=config_sistema
        )
    
    # ⚠️ CORRECCIÓN: Manejo de errores mejorado
    @app.errorhandler(401)
    def unauthorized(error):
        if request.path.startswith('/api/'):
            return {'error': 'No autorizado'}, 401
        flash('Por favor inicia sesión para acceder a esta página', 'warning')
        return redirect(url_for('auth.login'))
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app