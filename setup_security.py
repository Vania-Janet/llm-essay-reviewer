#!/usr/bin/env python3
"""
Script de configuración para generar claves de seguridad.
Ejecutar antes de usar el sistema por primera vez.
"""
import secrets
import os
from pathlib import Path


def generate_secret_key():
    """Generar una clave secreta segura."""
    return secrets.token_hex(32)


def setup_env_file():
    """Configurar archivo .env con claves de seguridad."""
    env_path = Path(__file__).parent / '.env'
    env_example_path = Path(__file__).parent / '.env.example'
    
    if env_path.exists():
        print("⚠️  El archivo .env ya existe.")
        response = input("¿Deseas regenerar las claves de seguridad? (s/N): ")
        if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada.")
            return
    
    print("\n🔐 Configuración de seguridad")
    print("=" * 50)
    
    # Solicitar API key de OpenAI
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if not openai_key:
        print("\n📝 Necesitas una API key de OpenAI")
        print("   Obtén una en: https://platform.openai.com/api-keys")
        openai_key = input("   Ingresa tu OPENAI_API_KEY: ").strip()
    
    # Generar claves secretas
    print("\n🔑 Generando claves de seguridad...")
    flask_secret = generate_secret_key()
    jwt_secret = generate_secret_key()
    
    # Crear contenido del archivo .env
    env_content = f"""# OpenAI API Key
OPENAI_API_KEY={openai_key}

# Flask Secret Key (generada automáticamente)
FLASK_SECRET_KEY={flask_secret}

# JWT Secret Key (generada automáticamente)
JWT_SECRET_KEY={jwt_secret}

# Base de datos
DATABASE_URL=sqlite:///ensayos.db

# Para producción, descomenta y configura:
# SSL_CERT_PATH=/path/to/cert.pem
# SSL_KEY_PATH=/path/to/key.pem
# REDIS_URL=redis://localhost:6379/0
"""
    
    # Guardar archivo
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("\n✅ Archivo .env creado exitosamente")
    print(f"   📁 Ubicación: {env_path}")
    print("\n⚠️  IMPORTANTE:")
    print("   - NUNCA compartas tu archivo .env")
    print("   - NUNCA subas .env a Git (ya está en .gitignore)")
    print("   - Guarda una copia segura de tus claves")
    print("\n🔐 Claves generadas:")
    print(f"   Flask Secret: {flask_secret[:16]}...")
    print(f"   JWT Secret:   {jwt_secret[:16]}...")


def create_admin_user():
    """Crear usuario administrador inicial."""
    try:
        from web.auth import AuthManager
        from database import db, Usuario, init_db
        from flask import Flask
        
        app = Flask(__name__)
        init_db(app)
        
        with app.app_context():
            # Verificar si ya existe un admin
            existing_admin = Usuario.query.filter_by(rol='admin').first()
            if existing_admin:
                print("\n✅ Ya existe un usuario administrador.")
                return
            
            print("\n👤 Crear usuario administrador")
            print("=" * 50)
            
            username = input("   Nombre de usuario: ").strip()
            email = input("   Email: ").strip()
            nombre = input("   Nombre completo: ").strip()
            
            while True:
                password = input("   Contraseña (min 8 caracteres): ").strip()
                if len(password) >= 8:
                    break
                print("   ❌ La contraseña debe tener al menos 8 caracteres")
            
            auth_manager = AuthManager()
            password_hash = auth_manager.hash_password(password)
            
            admin = Usuario(
                username=username,
                email=email,
                nombre_completo=nombre,
                password_hash=password_hash,
                rol='admin',
                activo=True
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("\n✅ Usuario administrador creado exitosamente")
            print(f"   Usuario: {username}")
            print(f"   Email: {email}")
            
    except ImportError:
        print("\n⚠️  No se pudo crear el usuario administrador.")
        print("   Ejecuta: pip install -r requirements.txt")
        print("   Luego vuelve a ejecutar este script.")
    except Exception as e:
        print(f"\n❌ Error al crear usuario: {str(e)}")


def main():
    """Función principal."""
    print("\n" + "=" * 50)
    print("🚀 CONFIGURACIÓN DEL SISTEMA DE EVALUACIÓN")
    print("=" * 50)
    
    # Paso 1: Configurar .env
    setup_env_file()
    
    # Paso 2: Crear usuario admin
    response = input("\n¿Deseas crear un usuario administrador? (S/n): ")
    if response.lower() not in ['n', 'no']:
        create_admin_user()
    
    print("\n" + "=" * 50)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 50)
    print("\n📚 Próximos pasos:")
    print("   1. Instalar dependencias: pip install -r requirements.txt")
    print("   2. Iniciar servidor: cd web && python app.py")
    print("   3. Abrir navegador: https://localhost:5001")
    print("\n⚠️  IMPORTANTE: Usa HTTPS en producción")
    print("   Configura certificados SSL en .env")
    print()


if __name__ == '__main__':
    main()
