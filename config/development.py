"""
Development configuration for Essay Evaluator.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class DevelopmentConfig:
    """Development configuration."""
    
    # Flask
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR}/essay_evaluator/data/database/essays.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
    
    # Upload settings
    UPLOAD_FOLDER = BASE_DIR / 'essay_evaluator' / 'data' / 'raw'
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))  # 10MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Processing
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '5'))
    MAX_CONCURRENT_EVALUATIONS = int(os.getenv('MAX_CONCURRENT_EVALUATIONS', '3'))
    
    # Evaluation
    EVALUATION_CONFIG = {
        'model': OPENAI_MODEL,
        'temperature': OPENAI_TEMPERATURE,
        'max_tokens': 2000,
        'parallel_execution': True,
        'criteria_weights': {
            'calidad_tecnica': 0.167,
            'creatividad': 0.167,
            'vinculacion_tematica': 0.167,
            'bienestar_colectivo': 0.167,
            'uso_responsable_ia': 0.167,
            'potencial_impacto': 0.167
        }
    }
    
    # Cache (optional)
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = BASE_DIR / 'logs' / 'app.log'


config = DevelopmentConfig()
