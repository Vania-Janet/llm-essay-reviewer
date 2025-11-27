"""
Sistema de autenticación seguro para el evaluador de ensayos.
Utiliza bcrypt para hashing de contraseñas y JWT para sesiones.
"""
import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import bcrypt
import jwt


class AuthManager:
    """Gestor de autenticación con hashing seguro de contraseñas."""
    
    def __init__(self, secret_key=None):
        """
        Inicializar el gestor de autenticación.
        
        Args:
            secret_key: Clave secreta para JWT. Si no se proporciona, se genera una.
        """
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY') or secrets.token_hex(32)
        self.token_expiry_hours = 24
        
    def hash_password(self, password: str) -> str:
        """
        Hash de contraseña usando bcrypt.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        # bcrypt automáticamente genera y almacena el salt
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds es un buen balance seguridad/performance
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verificar si una contraseña coincide con su hash.
        
        Args:
            password: Contraseña en texto plano
            hashed: Hash almacenado
            
        Returns:
            True si la contraseña es correcta
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    def generate_token(self, user_id: str, username: str) -> str:
        """
        Generar un JWT token para el usuario.
        
        Args:
            user_id: ID del usuario
            username: Nombre de usuario
            
        Returns:
            Token JWT
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> dict:
        """
        Verificar y decodificar un JWT token.
        
        Args:
            token: Token JWT
            
        Returns:
            Payload del token si es válido, None si no
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_token_from_request(self) -> str:
        """
        Extraer token del header Authorization.
        
        Returns:
            Token o None
        """
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None


def require_auth(f):
    """
    Decorador para proteger rutas que requieren autenticación.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_manager = AuthManager()
        token = auth_manager.get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Token de autenticación requerido'}), 401
        
        payload = auth_manager.verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Agregar información del usuario al request
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validar que la contraseña cumpla con requisitos mínimos de seguridad.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Tupla (es_valida, mensaje)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"
    
    # Opcional: verificar caracteres especiales
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, "La contraseña debe contener al menos un carácter especial"
    
    return True, "Contraseña válida"
