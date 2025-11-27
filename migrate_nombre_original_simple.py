#!/usr/bin/env python3
"""
Script de migración simple para agregar la columna nombre_archivo_original
sin depender de las importaciones pesadas de la app.
"""
import sqlite3
from pathlib import Path

def run_migration():
    """Ejecutar la migración de la base de datos."""
    
    # Ruta a la base de datos
    db_path = Path(__file__).parent / 'essays.db'
    
    if not db_path.exists():
        print(f"❌ Base de datos no encontrada en: {db_path}")
        return False
    
    print(f"📊 Conectando a la base de datos: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(ensayos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'nombre_archivo_original' in columns:
            print("✅ La columna 'nombre_archivo_original' ya existe en la tabla ensayos")
            return True
        
        print("➕ Agregando columna 'nombre_archivo_original' a la tabla ensayos...")
        
        # Agregar la columna
        cursor.execute("""
            ALTER TABLE ensayos 
            ADD COLUMN nombre_archivo_original VARCHAR(255)
        """)
        
        print("✅ Columna agregada exitosamente")
        
        # Copiar valores existentes de nombre_archivo a nombre_archivo_original
        print("📝 Copiando valores existentes...")
        cursor.execute("""
            UPDATE ensayos 
            SET nombre_archivo_original = nombre_archivo 
            WHERE nombre_archivo_original IS NULL
        """)
        
        rows_updated = cursor.rowcount
        print(f"✅ Se actualizaron {rows_updated} registros")
        
        # Confirmar cambios
        conn.commit()
        print("✅ Migración completada exitosamente")
        
        # Verificar el resultado
        cursor.execute("SELECT COUNT(*) FROM ensayos WHERE nombre_archivo_original IS NOT NULL")
        count = cursor.fetchone()[0]
        print(f"📊 Total de ensayos con nombre_archivo_original: {count}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()
            print("🔌 Conexión a la base de datos cerrada")

if __name__ == '__main__':
    print("=" * 60)
    print("🔄 Iniciando migración de base de datos")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migración completada con éxito")
    else:
        print("❌ Migración falló - revisa los errores anteriores")
    print("=" * 60)
