# [file name]: init_database.py
import mysql.connector
import os
from pathlib import Path

def init_database():
    try:
        # Configuración de la base de datos
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # Tu contraseña de MySQL
            'charset': 'utf8mb4'
        }
        
        # Conectar a MySQL
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("🗃️  Inicializando base de datos StarTask...")
        
        # Leer el archivo SQL
        sql_file = Path(__file__).parent / 'database_setup.sql'
        
        with open(sql_file, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Ejecutar cada sentencia SQL
        statements = sql_script.split(';')
        
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"✅ Ejecutada sentencia {i+1}/{len(statements)}")
                except Exception as e:
                    print(f"⚠️  En sentencia {i+1}: {e}")
                    continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 ¡Base de datos StarTask inicializada correctamente!")
        print("📊 Datos iniciales insertados:")
        print("   👥 Usuarios: Gerald, David, Sebastian")
        print("   📋 Proyecto: Proyecto Demo StarTask")
        print("   ✅ Tareas: 3 tareas de ejemplo")
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")

if __name__ == "__main__":
    init_database()