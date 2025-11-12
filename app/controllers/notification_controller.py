# [file name]: notification_controller.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.notification_model import NotificationModel

notification_bp = Blueprint('notificaciones', __name__)

@notification_bp.route('/api/notificaciones')
@login_required
def obtener_notificaciones():
    notification_model = NotificationModel()
    notificaciones = notification_model.obtener_notificaciones_usuario(current_user.id)
    return jsonify(notificaciones)

@notification_bp.route('/api/notificaciones/contar')
@login_required
def contar_notificaciones():
    notification_model = NotificationModel()
    count = notification_model.contar_no_leidas(current_user.id)
    return jsonify({'count': count})

@notification_bp.route('/api/notificaciones/leer/<int:id_notificacion>', methods=['POST'])
@login_required
def marcar_como_leida(id_notificacion):
    notification_model = NotificationModel()
    success = notification_model.marcar_como_leida(id_notificacion, current_user.id)
    return jsonify({'success': success})

@notification_bp.route('/api/notificaciones/leer-todas', methods=['POST'])
@login_required
def marcar_todas_leidas():
    notification_model = NotificationModel()
    success = notification_model.marcar_todas_leidas(current_user.id)
    return jsonify({'success': success})

@notification_bp.route('/api/notificaciones/eliminar/<int:id_notificacion>', methods=['DELETE'])
@login_required
def eliminar_notificacion(id_notificacion):
    notification_model = NotificationModel()
    success = notification_model.eliminar_notificacion(id_notificacion, current_user.id)
    return jsonify({'success': success})