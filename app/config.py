"""
Configuración centralizada de la aplicación.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorios base
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

class Config:
    """Configuración base de la aplicación."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Database
    DATABASE_PATH = DATA_DIR / 'essays.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', SECRET_KEY)
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'uploads'
    PERMANENT_PDF_FOLDER = BASE_DIR / 'data' / 'pdfs'
    PERMANENT_ANEXO_FOLDER = BASE_DIR / 'data' / 'anexos'
    PERMANENT_PROCESSED_FOLDER = BASE_DIR / 'data' / 'processed'
    
    # Security
    BCRYPT_LOG_ROUNDS = 12
    RATE_LIMIT_LOGIN = "5 per minute"
    RATE_LIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # CORS (si es necesario)
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    @classmethod
    def init_app(cls, app):
        """Inicializar configuración en la app Flask."""
        # Crear directorios si no existen
        cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.PERMANENT_PDF_FOLDER.mkdir(parents=True, exist_ok=True)
        cls.PERMANENT_ANEXO_FOLDER.mkdir(parents=True, exist_ok=True)
        
        # Configurar Flask
        app.config.from_object(cls)


class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False
    TESTING = False
    
    # En producción, SECRET_KEY debe venir de variable de entorno
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Validar que exista API key
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY debe estar configurada en producción")
        
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY debe cambiarse en producción")


class TestingConfig(Config):
    """Configuración para testing."""
    TESTING = True
    DATABASE_PATH = BASE_DIR / 'test.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'


# Mapeo de configuraciones
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Obtener configuración por nombre."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)
