"""
Database Package - Modelos y conexión de base de datos.

Contiene:
- connection: Configuración y inicialización de SQLAlchemy
- models: Modelos ORM de la aplicación
"""

from .connection import db, init_db
from .models import Ensayo, Usuario, CriterioPersonalizado, EvaluacionJurado

__all__ = ['db', 'init_db', 'Ensayo', 'Usuario', 'CriterioPersonalizado', 'EvaluacionJurado']
