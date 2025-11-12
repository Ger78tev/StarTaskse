from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response, jsonify
from flask_login import login_required, current_user
from app.utils.helpers import roles_required, registrar_actividad
from app.models.proyecto_model import ProyectoModel
from app.models.notification_model import NotificationModel
from app.models.usuario_model import UsuarioModel
from app.models.tarea_model import TareaModel
from datetime import datetime, timedelta
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

proyecto_bp = Blueprint('proyecto', __name__)

def notificar_asignacion_proyecto(id_usuario, proyecto):
    """Notifica cuando un usuario es asignado a un proyecto"""
    notification_model = NotificationModel()
    notification_model.crear_notificacion(
        id_usuario=id_usuario,
        tipo='proyecto_asignado',
        titulo='Nuevo proyecto asignado',
        mensaje=f'Has sido asignado al proyecto: {proyecto["nombre"]}',
        enlace=f'/proyectos',
        prioridad='media'
    )

def notificar_fecha_limite_proyecto(id_usuario, proyecto, dias_restantes):
    """Notifica sobre fechas límite de proyectos"""
    notification_model = NotificationModel()
    
    if dias_restantes <= 0:
        titulo = '¡Fecha límite hoy!'
        mensaje = f'El proyecto "{proyecto["nombre"]}" vence hoy'
        prioridad = 'alta'
    elif dias_restantes <= 1:
        titulo = 'Fecha límite próxima'
        mensaje = f'El proyecto "{proyecto["nombre"]}" vence mañana'
        prioridad = 'alta'
    elif dias_restantes <= 3:
        titulo = 'Fecha límite cercana'
        mensaje = f'El proyecto "{proyecto["nombre"]}" vence en {dias_restantes} días'
        prioridad = 'media'
    else:
        titulo = 'Recordatorio de proyecto'
        mensaje = f'El proyecto "{proyecto["nombre"]}" vence en {dias_restantes} días'
        prioridad = 'baja'
    
    notification_model.crear_notificacion(
        id_usuario=id_usuario,
        tipo='fecha_limite',
        titulo=titulo,
        mensaje=mensaje,
        enlace=f'/proyectos',
        fecha_limite=proyecto['fecha_vencimiento'] if 'fecha_vencimiento' in proyecto else None,
        prioridad=prioridad
    )

def verificar_fechas_limite_proyectos():
    """Verifica y notifica sobre fechas límite de proyectos"""
    proyecto_model = ProyectoModel()
    usuario_model = UsuarioModel()
    notification_model = NotificationModel()
    
    proyectos = proyecto_model.obtener_todos()
    hoy = datetime.now().date()
    
    for proyecto in proyectos:
        if proyecto.get('fecha_vencimiento'):
            fecha_vencimiento = proyecto['fecha_vencimiento']
            if isinstance(fecha_vencimiento, str):
                fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d').date()
            
            dias_restantes = (fecha_vencimiento - hoy).days
            
            # Notificar al líder del proyecto
            if dias_restantes <= 7:  # Notificar solo si faltan 7 días o menos
                notificar_fecha_limite_proyecto(proyecto['id_lider'], proyecto, dias_restantes)
                
                # Notificar también a usuarios con tareas en este proyecto
                tarea_model = TareaModel()
                tareas_proyecto = [t for t in tarea_model.obtener_todas() if t.get('id_proyecto') == proyecto['id']]
                usuarios_notificados = set()
                
                for tarea in tareas_proyecto:
                    if tarea.get('id_asignado') and tarea['id_asignado'] not in usuarios_notificados:
                        notificar_fecha_limite_proyecto(tarea['id_asignado'], proyecto, dias_restantes)
                        usuarios_notificados.add(tarea['id_asignado'])

@proyecto_bp.route('/proyectos')
@login_required
def listar_proyectos():
    proyecto_model = ProyectoModel()
    
    if current_user.rol == 'Colaborador':
        proyectos = proyecto_model.obtener_por_usuario(current_user.id)
    else:
        proyectos = proyecto_model.obtener_todos()
    
    # Verificar fechas límite al cargar proyectos
    verificar_fechas_limite_proyectos()
    
    return render_template('proyectos.html', proyectos=proyectos)

@proyecto_bp.route('/proyectos/crear', methods=['POST'])
@login_required
@roles_required('Administrador', 'Líder de Proyecto')
def crear_proyecto():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    id_lider = current_user.id
    fecha_vencimiento = request.form.get('fecha_vencimiento') or None
    
    proyecto_model = ProyectoModel()
    resultado = proyecto_model.crear(nombre, descripcion, id_lider, fecha_vencimiento)
    
    if resultado:
        registrar_actividad(current_user.id, f"Creó el proyecto '{nombre}'", 'proyectos')
        
        # Notificar al líder sobre la creación del proyecto
        notification_model = NotificationModel()
        notification_model.crear_notificacion(
            id_usuario=id_lider,
            tipo='proyecto_asignado',
            titulo='Proyecto creado',
            mensaje=f'Has creado el proyecto: {nombre}',
            enlace='/proyectos',
            fecha_limite=fecha_vencimiento,
            prioridad='media'
        )
        
        flash('Proyecto creado exitosamente', 'success')
    else:
        flash('Error al crear proyecto', 'danger')
    
    return redirect(url_for('proyecto.listar_proyectos'))

@proyecto_bp.route('/proyectos/editar/<int:id>', methods=['POST'])
@login_required
@roles_required('Administrador', 'Líder de Proyecto')
def editar_proyecto(id):
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    fecha_vencimiento = request.form.get('fecha_vencimiento') or None
    
    proyecto_model = ProyectoModel()
    proyecto = proyecto_model.obtener_por_id(id)
    
    if not proyecto:
        flash('Proyecto no encontrado', 'danger')
        return redirect(url_for('proyecto.listar_proyectos'))
    
    resultado = proyecto_model.actualizar(id, nombre, descripcion, fecha_vencimiento)
    
    if resultado:
        registrar_actividad(current_user.id, f"Editó el proyecto '{nombre}'", 'proyectos', id)
        
        # Notificar sobre la actualización del proyecto
        notification_model = NotificationModel()
        tarea_model = TareaModel()
        
        # Notificar al líder
        notification_model.crear_notificacion(
            id_usuario=proyecto['id_lider'],
            tipo='proyecto_asignado',
            titulo='Proyecto actualizado',
            mensaje=f'Se actualizó el proyecto: {nombre}',
            enlace='/proyectos',
            prioridad='baja'
        )
        
        # Notificar a usuarios con tareas en este proyecto
        tareas_proyecto = [t for t in tarea_model.obtener_todas() if t.get('id_proyecto') == id]
        usuarios_notificados = set()
        
        for tarea in tareas_proyecto:
            if tarea.get('id_asignado') and tarea['id_asignado'] not in usuarios_notificados:
                notification_model.crear_notificacion(
                    id_usuario=tarea['id_asignado'],
                    tipo='proyecto_asignado',
                    titulo='Proyecto actualizado',
                    mensaje=f'Se actualizó el proyecto: {nombre}',
                    enlace='/proyectos',
                    prioridad='baja'
                )
                usuarios_notificados.add(tarea['id_asignado'])
        
        flash('Proyecto actualizado exitosamente', 'success')
    else:
        flash('Error al actualizar proyecto', 'danger')
    
    return redirect(url_for('proyecto.listar_proyectos'))

@proyecto_bp.route('/proyectos/eliminar/<int:id>')
@login_required
@roles_required('Administrador', 'Líder de Proyecto')
def eliminar_proyecto(id):
    proyecto_model = ProyectoModel()
    proyecto = proyecto_model.obtener_por_id(id)
    
    if not proyecto:
        flash('Proyecto no encontrado', 'danger')
        return redirect(url_for('proyecto.listar_proyectos'))
    
    resultado = proyecto_model.eliminar(id)
    
    if resultado:
        registrar_actividad(current_user.id, f"Eliminó el proyecto ID {id}", 'proyectos', id)
        flash('Proyecto eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar proyecto', 'danger')
    
    return redirect(url_for('proyecto.listar_proyectos'))

@proyecto_bp.route('/reporte/proyectos')
@login_required
def reporte_proyectos():
    proyecto_model = ProyectoModel()
    proyectos = proyecto_model.obtener_todos()
    
    # Crear PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, "Reporte de Proyectos - StarTask")
    
    # Información
    p.setFont("Helvetica", 10)
    p.drawString(100, height - 130, f"Generado por: {current_user.nombre}")
    p.drawString(100, height - 150, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Tabla de proyectos
    y = height - 200
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, y, "Proyectos Activos:")
    
    y -= 30
    p.setFont("Helvetica", 10)
    
    for proyecto in proyectos:
        if y < 100:
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - 100
        
        p.drawString(120, y, f"• {proyecto['nombre']}")
        p.drawString(140, y - 15, f"Líder: {proyecto['lider_nombre']}")
        y -= 40
    
    p.save()
    buffer.seek(0)
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=reporte_proyectos.pdf'
    return response

@proyecto_bp.route('/api/proyectos/verificar-fechas')
@login_required
def api_verificar_fechas():
    """API para verificar fechas límite de proyectos"""
    try:
        verificar_fechas_limite_proyectos()
        return jsonify({'success': True, 'message': 'Fechas verificadas correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500