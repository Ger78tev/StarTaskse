from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.utils.helpers import roles_required, registrar_actividad
from app.models.tarea_model import TareaModel
from app.models.proyecto_model import ProyectoModel
from app.models.usuario_model import UsuarioModel

tarea_bp = Blueprint('tarea', __name__)

@tarea_bp.route('/tareas')
@login_required
def listar_tareas():
    tarea_model = TareaModel()
    proyecto_model = ProyectoModel()
    usuario_model = UsuarioModel()
    
    if current_user.rol == 'Colaborador':
        tareas = tarea_model.obtener_por_usuario(current_user.id)
    else:
        tareas = tarea_model.obtener_todas()
    
    proyectos = proyecto_model.obtener_todos()
    usuarios = usuario_model.obtener_usuarios_activos()
    
    return render_template('tareas.html', tareas=tareas, proyectos=proyectos, usuarios=usuarios)

@tarea_bp.route('/tareas/crear', methods=['POST'])
@login_required
@roles_required('Administrador', 'Líder de Proyecto')
def crear_tarea():
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    id_proyecto = request.form['id_proyecto']
    id_asignado = request.form['id_asignado']
    prioridad = request.form.get('prioridad', 'media')
    fecha_vencimiento = request.form.get('fecha_vencimiento') or None
    
    tarea_model = TareaModel()
    resultado = tarea_model.crear(titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento)
    
    if resultado:
        registrar_actividad(current_user.id, f"Creó la tarea '{titulo}'", 'tareas')
        flash('Tarea creada exitosamente', 'success')
    else:
        flash('Error al crear tarea', 'danger')
    
    return redirect(url_for('tarea.listar_tareas'))

@tarea_bp.route('/tareas/editar/<int:id>', methods=['POST'])
@login_required
def editar_tarea(id):
    estado = request.form['estado']
    
    tarea_model = TareaModel()
    resultado = tarea_model.actualizar_estado(id, estado)
    
    if resultado:
        registrar_actividad(current_user.id, f"Actualizó estado de tarea ID {id} a {estado}", 'tareas', id)
        flash('Estado de tarea actualizado', 'success')
    else:
        flash('Error al actualizar tarea', 'danger')
    
    return redirect(url_for('tarea.listar_tareas'))

@tarea_bp.route('/tareas/actualizar/<int:id>', methods=['POST'])
@login_required
@roles_required('Administrador', 'Líder de Proyecto')
def actualizar_tarea(id):
    try:
        # Obtener todos los campos del formulario
        titulo = request.form.get('titulo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        id_proyecto = request.form.get('id_proyecto')
        id_asignado = request.form.get('id_asignado')
        prioridad = request.form.get('prioridad', 'media')
        fecha_vencimiento = request.form.get('fecha_vencimiento') or None
        estado = request.form.get('estado', 'pendiente')
        
        print(f"Actualizando tarea {id}:")
        print(f"Título: {titulo}")
        print(f"Descripción: {descripcion}")
        print(f"Proyecto: {id_proyecto}")
        print(f"Asignado: {id_asignado}")
        print(f"Prioridad: {prioridad}")
        print(f"Fecha: {fecha_vencimiento}")
        print(f"Estado: {estado}")
        
        # Validaciones básicas
        if not titulo:
            error_msg = 'El título es requerido'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': error_msg}), 400
            else:
                flash(error_msg, 'danger')
                return redirect(url_for('tarea.listar_tareas'))
        
        tarea_model = TareaModel()
        
        # Actualizar la tarea completa
        resultado = tarea_model.actualizar_tarea(
            id, titulo, descripcion, id_proyecto, id_asignado, prioridad, fecha_vencimiento
        )
        
        # Si hay resultado, también actualizar el estado
        if resultado:
            estado_resultado = tarea_model.actualizar_estado(id, estado)
            print(f"Estado actualizado: {estado_resultado}")
        
        if resultado:
            registrar_actividad(current_user.id, f"Editó la tarea '{titulo}'", 'tareas', id)
            
            # Si es una petición AJAX, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': 'Tarea actualizada exitosamente'
                })
            else:
                flash('Tarea actualizada exitosamente', 'success')
        else:
            error_msg = 'Error al actualizar tarea'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': error_msg}), 400
            else:
                flash(error_msg, 'danger')
        
    except Exception as e:
        print(f"Error en actualizar_tarea: {str(e)}")
        error_msg = f'Error del servidor: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': error_msg}), 500
        else:
            flash(error_msg, 'danger')
    
    return redirect(url_for('tarea.listar_tareas'))

@tarea_bp.route('/tareas/eliminar/<int:id>')
@login_required
@roles_required('Administrador', 'Líder de Proyecto')
def eliminar_tarea(id):
    tarea_model = TareaModel()
    resultado = tarea_model.eliminar(id)
    
    if resultado:
        registrar_actividad(current_user.id, f"Eliminó la tarea ID {id}", 'tareas', id)
        flash('Tarea eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar tarea', 'danger')
    
    return redirect(url_for('tarea.listar_tareas'))