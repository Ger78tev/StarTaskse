# [file name]: chat_controller.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.chat_model import ChatModel
from app.models.usuario_model import UsuarioModel
from app.utils.helpers import registrar_actividad

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chat_team():
    """Página del chat - CORREGIDA"""
    try:
        chat_model = ChatModel()
        usuario_model = UsuarioModel()
        
        # Obtener mensajes
        mensajes = chat_model.obtener_mensajes(100)  # Más mensajes
        print(f"🔍 Debug: {len(mensajes)} mensajes cargados")  # Debug
        
        # Obtener usuarios activos
        usuarios_activos = usuario_model.obtener_usuarios_activos()
        
        return render_template('chat.html', 
                             mensajes=mensajes, 
                             usuarios_activos=usuarios_activos,
                             current_user_id=current_user.id)
    except Exception as e:
        print(f"❌ Error en chat_team: {e}")
        flash('Error al cargar el chat', 'danger')
        return render_template('chat.html', mensajes=[], usuarios_activos=[])

@chat_bp.route('/chat/enviar', methods=['POST'])
@login_required
def enviar_mensaje():
    """Envía un mensaje - CORREGIDO"""
    try:
        mensaje = request.form.get('mensaje', '').strip()
        print(f"🔍 Debug: Intentando enviar mensaje: '{mensaje}'")  # Debug
        
        if not mensaje:
            flash('El mensaje no puede estar vacío', 'danger')
            return redirect(url_for('chat.chat_team'))
        
        if len(mensaje) > 500:
            flash('El mensaje es demasiado largo', 'danger')
            return redirect(url_for('chat.chat_team'))
        
        chat_model = ChatModel()
        resultado = chat_model.enviar_mensaje(current_user.id, mensaje)
        
        if resultado:
            registrar_actividad(current_user.id, f"Envió un mensaje en el chat: {mensaje[:50]}...", 'chat')
            flash('Mensaje enviado correctamente', 'success')
            print("✅ Mensaje enviado a la base de datos")  # Debug
        else:
            flash('Error al enviar el mensaje', 'danger')
            print("❌ Error al enviar mensaje")  # Debug
        
        return redirect(url_for('chat.chat_team'))
        
    except Exception as e:
        print(f"❌ Error en enviar_mensaje: {e}")
        flash('Error al enviar el mensaje', 'danger')
        return redirect(url_for('chat.chat_team'))

@chat_bp.route('/chat/eliminar/<int:id_mensaje>')
@login_required
def eliminar_mensaje(id_mensaje):
    """Elimina un mensaje"""
    try:
        chat_model = ChatModel()
        resultado = chat_model.eliminar_mensaje(id_mensaje, current_user.id)
        
        if resultado:
            registrar_actividad(current_user.id, f"Eliminó un mensaje del chat", 'chat', id_mensaje)
            flash('Mensaje eliminado', 'success')
        else:
            flash('No se pudo eliminar el mensaje', 'danger')
        
        return redirect(url_for('chat.chat_team'))
    except Exception as e:
        print(f"❌ Error eliminando mensaje: {e}")
        flash('Error al eliminar mensaje', 'danger')
        return redirect(url_for('chat.chat_team'))

# API para obtener mensajes en tiempo real
@chat_bp.route('/api/chat/mensajes')
@login_required
def api_obtener_mensajes():
    """API para obtener mensajes (para AJAX)"""
    try:
        chat_model = ChatModel()
        mensajes = chat_model.obtener_mensajes(100)
        return jsonify({
            'success': True,
            'mensajes': mensajes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })