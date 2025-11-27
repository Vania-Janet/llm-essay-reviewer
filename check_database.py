#!/usr/bin/env python3
"""
Script para verificar el contenido de la base de datos de ensayos.
"""
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from database import db, Ensayo, Usuario, init_db

def main():
    """Verificar el contenido de la base de datos."""
    # Crear una app Flask temporal para acceder a la base de datos
    app = Flask(__name__)
    init_db(app)
    
    with app.app_context():
        print("\n" + "="*60)
        print("📊 ESTADO DE LA BASE DE DATOS")
        print("="*60 + "\n")
        
        # Contar usuarios
        usuario_count = Usuario.query.count()
        print(f"👥 Usuarios registrados: {usuario_count}")
        
        if usuario_count > 0:
            usuarios = Usuario.query.all()
            for u in usuarios:
                print(f"   - {u.username} ({u.email}) - Rol: {u.rol}")
        
        print()
        
        # Contar ensayos
        ensayo_count = Ensayo.query.count()
        print(f"📝 Ensayos evaluados: {ensayo_count}")
        
        if ensayo_count > 0:
            print(f"\n{'='*60}")
            print("LISTA DE ENSAYOS:")
            print(f"{'='*60}\n")
            
            ensayos = Ensayo.query.order_by(Ensayo.fecha_evaluacion.desc()).all()
            
            for i, ensayo in enumerate(ensayos, 1):
                print(f"{i}. ID: {ensayo.id}")
                print(f"   📄 Archivo: {ensayo.nombre_archivo}")
                print(f"   ⭐ Puntuación: {ensayo.puntuacion_total:.2f}/5.00")
                print(f"   📅 Fecha: {ensayo.fecha_evaluacion.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   🤖 Tiene anexo IA: {'Sí' if ensayo.tiene_anexo else 'No'}")
                
                # Mostrar calificaciones por criterio
                print(f"   📊 Calificaciones:")
                print(f"      - Calidad Técnica: {ensayo.calidad_tecnica.get('calificacion', 'N/A')}/5")
                print(f"      - Creatividad: {ensayo.creatividad.get('calificacion', 'N/A')}/5")
                print(f"      - Vinculación Temática: {ensayo.vinculacion_tematica.get('calificacion', 'N/A')}/5")
                print(f"      - Bienestar Colectivo: {ensayo.bienestar_colectivo.get('calificacion', 'N/A')}/5")
                print(f"      - Uso Responsable IA: {ensayo.uso_responsable_ia.get('calificacion', 'N/A')}/5")
                print(f"      - Potencial Impacto: {ensayo.potencial_impacto.get('calificacion', 'N/A')}/5")
                
                # Vista previa del texto
                texto_preview = ensayo.texto_completo[:150] if ensayo.texto_completo else "N/A"
                print(f"   📖 Texto (preview): {texto_preview}...")
                print()
        
        else:
            print("\n⚠️  No hay ensayos en la base de datos.")
            print("💡 Sugerencia: Usa la interfaz web para evaluar ensayos.")
        
        print("="*60)
        
        # Información de la base de datos
        db_path = Path(__file__).parent / 'essays.db'
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            print(f"\n💾 Archivo de base de datos: {db_path}")
            print(f"📦 Tamaño: {size_kb:.2f} KB")
        
        print()

if __name__ == '__main__':
    main()
