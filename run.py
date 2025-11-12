from app import create_app
from app.utils.database import Database
import os

app = create_app()

def initialize_app():
    """Función para inicializar la aplicación en producción"""
    try:
        db = Database()
        db.inicializar()
        
        print("🚀 StarTask iniciando...")
        print("✅ Base de datos inicializada correctamente")
        print("📧 Usuarios de prueba:")
        print("   gerald@startask.com / gerald123 (Admin)")
        print("   david@startask.com / david123 (Líder)")
        print("   sebastian@startask.com / sebastian123 (Colaborador)")
        
        return True
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        print("⚠️  Verifica que la base de datos esté configurada correctamente")
        return False

# Solo ejecutar en desarrollo local
if __name__ == '__main__':
    if initialize_app():
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        app.run(debug=debug_mode, host='0.0.0.0', port=5000)
    else:
        print("❌ No se pudo iniciar la aplicación")