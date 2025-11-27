"""
Middleware de autenticación y rate limiting.
"""
from functools import wraps
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.utils.security import AuthManager

# Instancia global del limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Instancia global del auth manager
auth_manager = AuthManager()


def require_auth(f):
    """
    Decorador para proteger rutas con autenticación JWT.
    
    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_route():
            user_id = request.user_id
            return jsonify({"message": "Access granted"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Obtener token desde cookie o header
        token = auth_manager.get_token_from_request()  # Sin pasar request
        
        if not token:
            return jsonify({'error': 'Token no proporcionado'}), 401
        
        # Verificar token
        payload = auth_manager.verify_token(token)
        
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Agregar user_id al request
        request.user_id = payload.get('user_id')
        request.username = payload.get('username')
        request.current_user = payload  # Para compatibilidad con código existente
        
        return f(*args, **kwargs)
    
    return decorated_function


def init_middleware(app):
    """Inicializar middleware en la aplicación."""
    limiter.init_app(app)
    return limiter, auth_manager
