"""
Production configuration for Essay Evaluator.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class ProductionConfig:
    """Production configuration."""
    
    # Flask
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')  # REQUIRED in production
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # REQUIRED
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # REQUIRED
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # REQUIRED
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
    
    # Upload settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/var/app/data/raw')
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Processing
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))
    MAX_CONCURRENT_EVALUATIONS = int(os.getenv('MAX_CONCURRENT_EVALUATIONS', '5'))
    
    # Cache (Redis recommended for production)
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')  # REQUIRED if using Redis
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '300'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')
    LOG_FILE = '/var/log/essay-evaluator/app.log'
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


config = ProductionConfig()
