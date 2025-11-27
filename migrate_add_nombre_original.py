#!/usr/bin/env python3
"""
Script de migración para agregar el campo nombre_archivo_original a ensayos existentes.
Este script debe ejecutarse UNA VEZ después de actualizar el modelo de la base de datos.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from database import db, Ensayo
from web.app import app

def migrate_add_nombre_original():
    """Agrega la columna nombre_archivo_original a la tabla ensayos."""
    
    with app.app_context():
        # Verificar si la columna ya existe
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('ensayos')]
        
        if 'nombre_archivo_original' in columns:
            print("✅ La columna 'nombre_archivo_original' ya existe.")
            
            # Poblar valores NULL con el nombre actual (para registros antiguos)
            ensayos_sin_original = Ensayo.query.filter(
                Ensayo.nombre_archivo_original.is_(None)
            ).all()
            
            if ensayos_sin_original:
                print(f"📝 Actualizando {len(ensayos_sin_original)} ensayos sin nombre original...")
                for ensayo in ensayos_sin_original:
                    # Para registros antiguos, usar el nombre actual como original
                    # (aunque no sea perfecto, es mejor que NULL)
                    ensayo.nombre_archivo_original = ensayo.nombre_archivo
                
                db.session.commit()
                print(f"✅ {len(ensayos_sin_original)} ensayos actualizados correctamente.")
            else:
                print("✅ Todos los ensayos ya tienen nombre original.")
            
            return
        
        # La columna no existe, necesitamos crearla
        print("⚠️  La columna 'nombre_archivo_original' NO existe.")
        print("🔧 Agregando columna a la tabla ensayos...")
        
        try:
            # Agregar la columna usando SQL directo
            with db.engine.connect() as conn:
                conn.execute(db.text(
                    "ALTER TABLE ensayos ADD COLUMN nombre_archivo_original VARCHAR(255)"
                ))
                conn.commit()
            
            print("✅ Columna agregada correctamente.")
            
            # Poblar con valores del nombre actual para registros existentes
            ensayos = Ensayo.query.all()
            print(f"📝 Poblando {len(ensayos)} ensayos con nombre original...")
            
            for ensayo in ensayos:
                ensayo.nombre_archivo_original = ensayo.nombre_archivo
            
            db.session.commit()
            print("✅ Migración completada exitosamente.")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    print("🚀 Iniciando migración de base de datos...")
    print("="*60)
    
    try:
        migrate_add_nombre_original()
        print("="*60)
        print("✅ Migración completada. La base de datos está actualizada.")
        print("ℹ️  Los nuevos ensayos usarán UUID para nombres únicos.")
        
    except Exception as e:
        print("="*60)
        print(f"❌ ERROR: {e}")
        print("⚠️  La migración falló. Revisa los errores y vuelve a intentar.")
        sys.exit(1)
