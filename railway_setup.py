#!/usr/bin/env python3
"""
Script de inicialización para Railway
Ejecuta este script manualmente después del despliegue
"""

import mysql.connector
from mysql.connector import Error
import os
import time

def railway_database_setup():
    print("🚀 INICIALIZANDO STARTASK EN RAILWAY...")
    
    # Configuración desde variables de entorno
    db_config = {
        'host': os.environ.get('DB_HOST'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
        'port': int(os.environ.get('DB_PORT', 3306))
    }
    
    try:
        # Conectar sin base de datos específica
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        print("✅ Conectado a MySQL en Railway")
        
        # Crear base de datos si no existe
        cursor.execute("CREATE DATABASE IF NOT EXISTS startask CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("USE startask")
        
        print("✅ Base de datos 'startask' creada/verificada")
        
        # Ejecutar script SQL
        with open('database_setup.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Ejecutar cada sentencia
        statements = sql_script.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"⚠️  En sentencia: {e}")
                    continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 ¡Base de datos inicializada correctamente en Railway!")
        print("📊 Datos disponibles:")
        print("   👤 Admin: gerald@startask.com / gerald123")
        print("   👤 Líder: david@startask.com / david123")
        print("   👤 Colaborador: sebastian@startask.com / sebastian123")
        
        return True
        
    except Error as e:
        print(f"❌ Error en inicialización: {e}")
        return False

if __name__ == "__main__":
    railway_database_setup()