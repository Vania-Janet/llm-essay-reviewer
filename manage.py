#!/usr/bin/env python3
"""
Script de gestión de base de datos con Flask-Migrate.

Comandos disponibles:
  python manage.py init        - Inicializar sistema de migraciones
  python manage.py migrate     - Crear nueva migración automática
  python manage.py upgrade     - Aplicar migraciones pendientes
  python manage.py downgrade   - Revertir última migración
  python manage.py history     - Ver historial de migraciones
  python manage.py current     - Ver versión actual de BD
"""
import sys
import os
from pathlib import Path

# Agregar directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from app.database.connection import db
from flask_migrate import Migrate, init, migrate as create_migration, upgrade, downgrade, current, history

migrate_tool = Migrate()

def create_app():
    """Crear aplicación Flask para migraciones."""
    app = Flask(__name__)
    
    # Configuración de base de datos
    project_root = Path(__file__).parent
    db_path = project_root / 'data' / 'essays.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path.absolute()}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar extensiones
    db.init_app(app)
    migrate_tool.init_app(app, db)
    
    return app

def print_help():
    """Mostrar ayuda de comandos."""
    print("""
======================================================================
           GESTION DE BASE DE DATOS - Flask-Migrate           
======================================================================

Comandos disponibles:

  init              Inicializar sistema de migraciones (solo primera vez)
  migrate [mensaje] Crear nueva migracion automatica
  upgrade           Aplicar todas las migraciones pendientes
  downgrade         Revertir la ultima migracion
  history           Ver historial de migraciones
  current           Ver version actual de la base de datos
  help              Mostrar esta ayuda

Ejemplos:

  # Primera vez - Inicializar sistema
  python manage.py init

  # Despues de modificar models en database.py
  python manage.py migrate "Agregar campo fecha_modificacion"

  # Aplicar cambios a la base de datos
  python manage.py upgrade

  # Ver que version tienes
  python manage.py current

  # Revertir ultimo cambio
  python manage.py downgrade

Flujo de trabajo tipico:

  1. Modificar modelos en database.py
  2. python manage.py migrate "Descripcion del cambio"
  3. python manage.py upgrade
  4. Listo!

NOTA: Las migraciones se guardan en /migrations/versions/
      Incluirlas en Git para compartir con el equipo.
    """)

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] == 'help':
        print_help()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    app = create_app()
    
    with app.app_context():
        try:
            if command == 'init':
                print("Inicializando sistema de migraciones...")
                from flask_migrate import init as flask_init
                flask_init()
                print("Sistema de migraciones inicializado en /migrations/")
                print("Ahora ejecuta: python manage.py migrate 'Initial migration'")
                
            elif command == 'migrate':
                mensaje = sys.argv[2] if len(sys.argv) > 2 else 'Auto migration'
                print(f"Creando migracion: {mensaje}")
                from flask_migrate import migrate as flask_migrate
                flask_migrate(message=mensaje)
                print("Migracion creada exitosamente")
                print("Ahora ejecuta: python manage.py upgrade")
                
            elif command == 'upgrade':
                print("Aplicando migraciones...")
                from flask_migrate import upgrade as flask_upgrade
                flask_upgrade()
                print("Base de datos actualizada")
                
            elif command == 'downgrade':
                print("Revirtiendo ultima migracion...")
                from flask_migrate import downgrade as flask_downgrade
                flask_downgrade()
                print("Migracion revertida")
                
            elif command == 'current':
                print("Version actual de la base de datos:")
                from flask_migrate import current as flask_current
                flask_current()
                
            elif command == 'history':
                print("Historial de migraciones:")
                from flask_migrate import history as flask_history
                flask_history()
                
            else:
                print(f"ERROR: Comando desconocido: {command}")
                print("Usa 'python manage.py help' para ver comandos disponibles")
                sys.exit(1)
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
