# [file name]: reportes_controller.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from app.models.proyecto_model import ProyectoModel
from app.models.tarea_model import TareaModel
from app.models.usuario_model import UsuarioModel
from app.models.config_model import ConfigModel
from app.utils.helpers import roles_required, registrar_actividad
from datetime import datetime, timedelta
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch

reportes_bp = Blueprint('reportes', __name__)

@reportes_bp.route('/reportes')
@login_required
def dashboard_reportes():
    """Dashboard principal de reportes y métricas"""
    proyecto_model = ProyectoModel()
    tarea_model = TareaModel()
    usuario_model = UsuarioModel()
    config_model = ConfigModel()
    
    # Obtener estadísticas generales
    stats_proyectos = proyecto_model.obtener_estadisticas()
    stats_tareas = tarea_model.obtener_estadisticas()
    usuarios = usuario_model.obtener_usuarios_activos()
    
    # Métricas detalladas
    tareas_pendientes = tarea_model.contar_tareas_por_estado('pendiente')
    tareas_en_progreso = tarea_model.contar_tareas_por_estado('en_progreso')
    tareas_completadas = stats_tareas['tareas_completadas']
    total_tareas = stats_tareas['total_tareas']
    
    # Calcular porcentajes
    porcentaje_completadas = (tareas_completadas / total_tareas * 100) if total_tareas > 0 else 0
    porcentaje_en_progreso = (tareas_en_progreso / total_tareas * 100) if total_tareas > 0 else 0
    porcentaje_pendientes = (tareas_pendientes / total_tareas * 100) if total_tareas > 0 else 0
    
    # Proyectos recientes
    proyectos_recientes = proyecto_model.obtener_recientes(5)
    
    # Tareas recientes
    if current_user.rol == 'Colaborador':
        tareas_recientes = tarea_model.obtener_por_usuario(current_user.id, 10)
    else:
        tareas_recientes = tarea_model.obtener_todas()[:10]
    
    # Reportes predefinidos
    reportes_disponibles = [
        {
            'id': 'proyectos',
            'icono': 'project-diagram',
            'titulo': 'Reporte de Proyectos',
            'estado': 'listo',
            'descripcion': 'Resumen general de todos los proyectos activos',
            'tipo': 'Completo',
            'fecha': datetime.now().strftime('%d/%m/%Y')
        },
        {
            'id': 'tareas',
            'icono': 'tasks',
            'titulo': 'Reporte de Tareas',
            'estado': 'listo',
            'descripcion': 'Análisis de productividad y tareas completadas',
            'tipo': 'Detallado',
            'fecha': datetime.now().strftime('%d/%m/%Y')
        },
        {
            'id': 'equipo',
            'icono': 'users',
            'titulo': 'Reporte de Equipo',
            'estado': 'listo',
            'descripcion': 'Rendimiento y asignación de miembros del equipo',
            'tipo': 'Resumen',
            'fecha': datetime.now().strftime('%d/%m/%Y')
        },
        {
            'id': 'productividad',
            'icono': 'chart-line',
            'titulo': 'Métricas de Productividad',
            'estado': 'generando',
            'descripcion': 'Estadísticas de avance y eficiencia del equipo',
            'tipo': 'Analítico',
            'fecha': datetime.now().strftime('%d/%m/%Y')
        }
    ]
    
    return render_template('reportes.html',
                         total_proyectos=stats_proyectos['total_proyectos'],
                         proyectos_activos=stats_proyectos['total_proyectos'],  # Todos están activos
                         total_tareas=total_tareas,
                         tareas_completadas=tareas_completadas,
                         tareas_pendientes=tareas_pendientes,
                         tareas_en_progreso=tareas_en_progreso,
                         team_members=len(usuarios),
                         porcentaje_completadas=porcentaje_completadas,
                         porcentaje_en_progreso=porcentaje_en_progreso,
                         porcentaje_pendientes=porcentaje_pendientes,
                         proyectos_recientes=proyectos_recientes,
                         tareas_recientes=tareas_recientes,
                         reportes_disponibles=reportes_disponibles)

@reportes_bp.route('/reportes/proyectos/pdf')
@login_required
def generar_reporte_proyectos_pdf():
    """Genera reporte PDF de proyectos"""
    proyecto_model = ProyectoModel()
    proyectos = proyecto_model.obtener_todos()
    
    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.HexColor('#7c3aed')
    )
    
    # Título
    title = Paragraph("REPORTE DE PROYECTOS - STARTASK", title_style)
    elements.append(title)
    
    # Información del reporte
    info_text = f"""
    <b>Generado por:</b> {current_user.nombre}<br/>
    <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Total de proyectos:</b> {len(proyectos)}<br/>
    """
    info = Paragraph(info_text, styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 20))
    
    # Tabla de proyectos
    if proyectos:
        data = [['Nombre', 'Líder', 'Descripción', 'Fecha Creación']]
        
        for proyecto in proyectos:
            descripcion = proyecto['descripcion'][:100] + '...' if len(proyecto['descripcion']) > 100 else proyecto['descripcion']
            fecha = proyecto['fecha_creacion'].strftime('%d/%m/%Y') if proyecto['fecha_creacion'] else 'N/A'
            data.append([
                proyecto['nombre'],
                proyecto.get('lider_nombre', 'N/A'),
                descripcion,
                fecha
            ])
        
        table = Table(data, colWidths=[120, 80, 180, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No hay proyectos activos", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    # Registrar actividad
    registrar_actividad(current_user.id, "Generó reporte PDF de proyectos", 'reportes')
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_proyectos_{datetime.now().strftime("%Y%m%d")}.pdf'
    return response

@reportes_bp.route('/reportes/tareas/pdf')
@login_required
def generar_reporte_tareas_pdf():
    """Genera reporte PDF de tareas"""
    tarea_model = TareaModel()
    proyecto_model = ProyectoModel()
    
    if current_user.rol == 'Colaborador':
        tareas = tarea_model.obtener_por_usuario(current_user.id)
    else:
        tareas = tarea_model.obtener_todas()
    
    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.HexColor('#7c3aed')
    )
    
    # Título
    title = Paragraph("REPORTE DE TAREAS - STARTASK", title_style)
    elements.append(title)
    
    # Estadísticas
    stats = tarea_model.obtener_estadisticas()
    stats_text = f"""
    <b>Generado por:</b> {current_user.nombre}<br/>
    <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Total de tareas:</b> {stats['total_tareas']}<br/>
    <b>Tareas completadas:</b> {stats['tareas_completadas']}<br/>
    <b>Tasa de finalización:</b> {(stats['tareas_completadas']/stats['total_tareas']*100) if stats['total_tareas'] > 0 else 0:.1f}%<br/>
    """
    elements.append(Paragraph(stats_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Tabla de tareas
    if tareas:
        data = [['Título', 'Proyecto', 'Asignado', 'Estado', 'Prioridad', 'Vencimiento']]
        
        for tarea in tareas:
            fecha_vencimiento = tarea['fecha_vencimiento'].strftime('%d/%m/%Y') if tarea['fecha_vencimiento'] else 'No definida'
            data.append([
                tarea['titulo'][:30],
                tarea.get('proyecto_nombre', 'N/A')[:20],
                tarea.get('asignado_nombre', 'N/A')[:20],
                tarea['estado'].replace('_', ' ').title(),
                tarea['prioridad'].title(),
                fecha_vencimiento
            ])
        
        table = Table(data, colWidths=[100, 80, 80, 60, 50, 70])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No hay tareas para mostrar", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    registrar_actividad(current_user.id, "Generó reporte PDF de tareas", 'reportes')
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_tareas_{datetime.now().strftime("%Y%m%d")}.pdf'
    return response

@reportes_bp.route('/reportes/equipo/pdf')
@login_required
@roles_required('Administrador', 'Líder de Proyecto')
def generar_reporte_equipo_pdf():
    """Genera reporte PDF del equipo"""
    usuario_model = UsuarioModel()
    tarea_model = TareaModel()
    config_model = ConfigModel()
    
    usuarios = usuario_model.obtener_usuarios_activos()
    
    # Crear PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        textColor=colors.HexColor('#7c3aed')
    )
    
    # Título
    title = Paragraph("REPORTE DE EQUIPO - STARTASK", title_style)
    elements.append(title)
    
    # Información del equipo
    info_text = f"""
    <b>Generado por:</b> {current_user.nombre}<br/>
    <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Total de miembros:</b> {len(usuarios)}<br/>
    """
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Tabla de miembros
    if usuarios:
        data = [['Nombre', 'Email', 'Rol', 'Tareas Asignadas', 'Tareas Completadas']]
        
        for usuario in usuarios:
            tareas_usuario = tarea_model.obtener_por_usuario(usuario.id)
            tareas_completadas = len([t for t in tareas_usuario if t['estado'] == 'completada'])
            
            data.append([
                usuario.nombre,
                usuario.email,
                usuario.rol,
                str(len(tareas_usuario)),
                str(tareas_completadas)
            ])
        
        table = Table(data, colWidths=[100, 120, 80, 60, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No hay miembros en el equipo", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    registrar_actividad(current_user.id, "Generó reporte PDF del equipo", 'reportes')
    
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=reporte_equipo_{datetime.now().strftime("%Y%m%d")}.pdf'
    return response

@reportes_bp.route('/reportes/productividad')
@login_required
def reporte_productividad():
    """Vista de métricas de productividad"""
    proyecto_model = ProyectoModel()
    tarea_model = TareaModel()
    usuario_model = UsuarioModel()
    
    # Obtener datos para métricas
    proyectos = proyecto_model.obtener_todos()
    tareas = tarea_model.obtener_todas()
    usuarios = usuario_model.obtener_usuarios_activos()
    
    # Calcular métricas avanzadas
    total_tareas = len(tareas)
    tareas_completadas = len([t for t in tareas if t['estado'] == 'completada'])
    tareas_vencidas = len([t for t in tareas if t['fecha_vencimiento'] and t['fecha_vencimiento'] < datetime.now().date() and t['estado'] != 'completada'])
    
    # Eficiencia por usuario
    eficiencia_usuarios = []
    for usuario in usuarios:
        tareas_usuario = tarea_model.obtener_por_usuario(usuario.id)
        completadas = len([t for t in tareas_usuario if t['estado'] == 'completada'])
        total = len(tareas_usuario)
        eficiencia = (completadas / total * 100) if total > 0 else 0
        
        eficiencia_usuarios.append({
            'usuario': usuario.nombre,
            'rol': usuario.rol,
            'tareas_asignadas': total,
            'tareas_completadas': completadas,
            'eficiencia': eficiencia
        })
    
    # Proyectos con más tareas
    proyectos_tareas = []
    for proyecto in proyectos:
        tareas_proyecto = [t for t in tareas if t['id_proyecto'] == proyecto['id']]
        completadas_proyecto = len([t for t in tareas_proyecto if t['estado'] == 'completada'])
        
        proyectos_tareas.append({
            'proyecto': proyecto['nombre'],
            'total_tareas': len(tareas_proyecto),
            'completadas': completadas_proyecto,
            'porcentaje': (completadas_proyecto / len(tareas_proyecto) * 100) if len(tareas_proyecto) > 0 else 0
        })
    
    # Ordenar por eficiencia
    eficiencia_usuarios.sort(key=lambda x: x['eficiencia'], reverse=True)
    proyectos_tareas.sort(key=lambda x: x['porcentaje'], reverse=True)
    
    return render_template('reporte_productividad.html',
                         total_tareas=total_tareas,
                         tareas_completadas=tareas_completadas,
                         tareas_vencidas=tareas_vencidas,
                         tasa_completadas=(tareas_completadas / total_tareas * 100) if total_tareas > 0 else 0,
                         eficiencia_usuarios=eficiencia_usuarios[:5],  # Top 5
                         proyectos_tareas=proyectos_tareas[:5])  # Top 5