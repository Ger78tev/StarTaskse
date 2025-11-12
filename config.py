import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'startask_railway_production_secret_key_2024')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'startask')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig  # Cambiado a producción por defecto
}