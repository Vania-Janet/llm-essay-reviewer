"""
Conexión y configuración de base de datos con Flask-Migrate.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instancias globales
db = SQLAlchemy()
migrate = Migrate()


def init_db(app):
    """
    Inicializar base de datos con la aplicación Flask.
    Asegura persistencia completa de datos.
    
    Args:
        app: Instancia de Flask
    """
    # Configurar opciones de SQLAlchemy para persistencia
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,  # Verificar conexión antes de usar
        'pool_recycle': 3600,   # Reciclar conexiones cada hora
        'echo': False,          # No mostrar SQL en producción
    }
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Importar modelos para que SQLAlchemy los registre
        from . import models
        
        # Crear tablas si no existen
        db.create_all()
        
        print(f"Base de datos inicializada en: {app.config['DATABASE_PATH']}")
        print(f"   Archivo existe: {app.config['DATABASE_PATH'].exists()}")
        print("Usa 'python manage.py migrate' para crear migraciones")
        print("Usa 'python manage.py upgrade' para aplicar migraciones")


def get_db():
    """Obtener instancia de base de datos."""
    return db
