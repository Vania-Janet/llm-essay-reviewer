"""
Rutas de autenticación: login, registro, logout.
"""
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import db
from app.database.models import Usuario
from app.api.middleware import limiter, auth_manager, require_auth
from app.utils.security import validate_password_strength
from app.utils.logger import get_auth_logger

bp = Blueprint('auth', __name__)
logger = get_auth_logger()


@bp.route('/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        nombre_completo = data.get('nombre_completo', '').strip()
        
        # Validaciones
        if len(username) < 3:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 3 caracteres'}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Verificar unicidad
        if Usuario.query.filter_by(username=username).first():
            return jsonify({'error': 'El nombre de usuario ya está en uso'}), 409
        
        if Usuario.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        # Crear usuario
        password_hash = auth_manager.hash_password(password)
        logger.info(f"Creating user: {username}")
        logger.debug(f"Email: {email}, Hash generated: {password_hash[:20]}...")
        
        nuevo_usuario = Usuario(
            username=username,
            email=email,
            password_hash=password_hash,
            nombre_completo=nombre_completo
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        logger.info(f"User created successfully: {username} (ID: {nuevo_usuario.id})")
        
        # Generar token
        token = auth_manager.generate_token(str(nuevo_usuario.id), nuevo_usuario.username)
        
        # Respuesta con cookie HttpOnly
        response = jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': nuevo_usuario.to_dict()
        })
        
        response.set_cookie(
            'token',
            token,
            httponly=True,
            secure=False,  # True en producción con HTTPS
            samesite='Lax',
            max_age=86400
        )
        
        return response, 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during registration: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error de base de datos al registrar usuario'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error during registration: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error inesperado al registrar usuario'}), 500


@bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """Autenticar usuario y generar token."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['username', 'password']):
            return jsonify({'error': 'Usuario/Email y contraseña requeridos'}), 400
        
        login_input = data['username'].strip()
        password = data['password']
        
        logger.debug(f"Login attempt: {login_input}")
        
        # Buscar por username o email
        usuario = Usuario.query.filter(
            or_(Usuario.username == login_input, Usuario.email == login_input)
        ).first()
        
        if not usuario:
            logger.warning(f"Failed login: user not found - {login_input}")
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        logger.debug(f"User found: {usuario.username} (ID: {usuario.id})")
        
        if not usuario.activo:
            logger.warning(f"Failed login: inactive user - {usuario.username}")
            return jsonify({'error': 'Usuario inactivo'}), 403
        
        # Verificar contraseña
        password_valid = auth_manager.verify_password(password, usuario.password_hash)
        logger.debug(f"Password verification: {'valid' if password_valid else 'invalid'}")
        
        if not password_valid:
            logger.warning(f"Failed login: invalid password - {usuario.username}")
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        logger.info(f"Successful login: {usuario.username} (ID: {usuario.id})")
        
        # Actualizar último acceso
        from datetime import datetime
        usuario.ultimo_acceso = datetime.now()
        db.session.commit()
        
        # Generar token
        token = auth_manager.generate_token(str(usuario.id), usuario.username)
        
        # Respuesta con cookie HttpOnly
        response = jsonify({
            'message': 'Login exitoso',
            'user': usuario.to_dict()
        })
        
        response.set_cookie(
            'token',
            token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=86400
        )
        
        return response
        
    except SQLAlchemyError as e:
        logger.error(f"Database error during login: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error de base de datos'}), 500
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}", exc_info=True)
        return jsonify({'error': 'Error al iniciar sesión'}), 500


@bp.route('/logout', methods=['POST'])
def logout():
    """Cerrar sesión del usuario - invalidar cookie completamente."""
    response = jsonify({'message': 'Sesión cerrada exitosamente'})
    # Invalidar la cookie completamente con todos los parámetros
    response.set_cookie(
        'token',
        '',
        expires=0,
        httponly=True,
        secure=False,
        samesite='Lax',
        max_age=0
    )
    # Agregar headers para prevenir caché
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response, 200


@bp.route('/verify-token', methods=['GET'])
def verify_token():
    """Verificar si el token es válido."""
    token = auth_manager.get_token_from_request()  # Sin pasar request
    
    if not token:
        return jsonify({'valid': False}), 401
    
    payload = auth_manager.verify_token(token)
    
    if not payload:
        return jsonify({'valid': False}), 401
    
    return jsonify({'valid': True, 'user_id': payload.get('user_id')}), 200


@bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Cambiar contraseña del usuario autenticado."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['current_password', 'new_password']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        usuario = Usuario.query.get(request.user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Verificar contraseña actual
        if not auth_manager.verify_password(data['current_password'], usuario.password_hash):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 401
        
        # Validar nueva contraseña
        is_valid, message = validate_password_strength(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Actualizar contraseña
        usuario.password_hash = auth_manager.hash_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cambiar contraseña: {str(e)}'}), 500


@bp.route('/db-status', methods=['GET'])
def db_status():
    """Verificar estado de la base de datos."""
    try:
        from app.database.models import Ensayo
        
        total_ensayos = Ensayo.query.count()
        con_anexo = Ensayo.query.filter_by(tiene_anexo=True).count()
        sin_anexo = Ensayo.query.filter_by(tiene_anexo=False).count()
        
        return jsonify({
            'status': 'ok',
            'total_ensayos': total_ensayos,
            'con_anexo': con_anexo,
            'sin_anexo': sin_anexo,
            'database_path': str(current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown'))
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
