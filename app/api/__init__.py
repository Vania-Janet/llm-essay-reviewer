"""
API Package - Contiene los endpoints REST y middleware.
"""

from . import routes
from .middleware import init_middleware, require_auth

__all__ = ['routes', 'init_middleware', 'require_auth']
