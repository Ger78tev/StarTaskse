from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.proyecto_model import ProyectoModel
from app.models.tarea_model import TareaModel
from app.models.usuario_model import UsuarioModel

# DEFINIR EL BLUEPRINT - ESTO DEBE ESTAR PRESENTE
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/tablero')
@login_required
def tablero():
    proyecto_model = ProyectoModel()
    tarea_model = TareaModel()
    usuario_model = UsuarioModel()
    
    # ... resto del código del dashboard ...
    
    # Obtener estadísticas reales
    stats_proyectos = proyecto_model.obtener_estadisticas()
    stats_tareas = tarea_model.obtener_estadisticas()
    usuarios = usuario_model.obtener_usuarios_activos()
    
    # Proyectos recientes
    proyectos_recientes = proyecto_model.obtener_recientes(3)
    
    # Tareas del usuario
    if current_user.rol == 'Colaborador':
        mis_tareas = tarea_model.obtener_por_usuario(current_user.id, 5)
    else:
        mis_tareas = tarea_model.obtener_todas()[:5]
    
    # Métricas para estadísticas
    metricas = {
        'tareas_pendientes': tarea_model.contar_tareas_por_estado('pendiente'),
        'tareas_en_progreso': tarea_model.contar_tareas_por_estado('en_progreso'),
        'tareas_completadas': tarea_model.contar_tareas_por_estado('completada'),
        'tareas_totales': stats_tareas['total_tareas']
    }
    
    return render_template('tablero.html',
                         total_proyectos=stats_proyectos['total_proyectos'],
                         total_tareas=stats_tareas['total_tareas'],
                         tareas_completadas=stats_tareas['tareas_completadas'],
                         total_usuarios=len(usuarios),
                         proyectos_recientes=proyectos_recientes,
                         mis_tareas=mis_tareas,
                         metricas=metricas)