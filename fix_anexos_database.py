#!/usr/bin/env python3
"""
Script para actualizar el campo tiene_anexo en la base de datos.
Re-verifica todos los ensayos contra el diccionario MATCHES_SEGUROS_IA
y actualiza la base de datos con la información correcta.
"""
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from database import db, Ensayo, init_db
from matches_ia import tiene_anexo_ia, obtener_anexo_ia

def main():
    """Actualizar el campo tiene_anexo para todos los ensayos."""
    # Crear una app Flask temporal para acceder a la base de datos
    app = Flask(__name__)
    init_db(app)
    
    with app.app_context():
        print("\n" + "="*60)
        print("🔧 ACTUALIZACIÓN DE ANEXOS EN BASE DE DATOS")
        print("="*60 + "\n")
        
        # Obtener todos los ensayos
        ensayos = Ensayo.query.all()
        total = len(ensayos)
        print(f"📊 Total de ensayos en base de datos: {total}\n")
        
        actualizados = 0
        con_anexo_antes = 0
        con_anexo_despues = 0
        
        for ensayo in ensayos:
            # Guardar estado anterior
            tenia_anexo_antes = ensayo.tiene_anexo
            if tenia_anexo_antes:
                con_anexo_antes += 1
            
            # Extraer nombre base (sin extensión)
            nombre_base = ensayo.nombre_archivo.replace('.pdf', '').replace('.txt', '')
            
            # Verificar si tiene anexo según el diccionario
            tiene_anexo_nuevo = tiene_anexo_ia(nombre_base)
            nombre_anexo = obtener_anexo_ia(nombre_base)
            
            # Actualizar si cambió
            if ensayo.tiene_anexo != tiene_anexo_nuevo:
                print(f"🔄 Actualizando: {ensayo.nombre_archivo}")
                print(f"   Antes: tiene_anexo={tenia_anexo_antes}")
                print(f"   Después: tiene_anexo={tiene_anexo_nuevo}")
                if nombre_anexo:
                    print(f"   Anexo: {nombre_anexo}")
                print()
                
                ensayo.tiene_anexo = tiene_anexo_nuevo
                
                # Actualizar ruta del anexo si existe
                if tiene_anexo_nuevo and nombre_anexo:
                    ruta_anexo = Path(__file__).parent / 'Anexo_procesado' / nombre_anexo
                    ensayo.ruta_anexo = str(ruta_anexo)
                    
                    # Intentar cargar el texto del anexo
                    if ruta_anexo.exists():
                        try:
                            if nombre_anexo.lower().endswith('.pdf'):
                                from pdf_processor import extraer_texto_pdf
                                ensayo.texto_anexo = extraer_texto_pdf(str(ruta_anexo))
                            else:
                                with open(ruta_anexo, 'r', encoding='utf-8') as f:
                                    ensayo.texto_anexo = f.read()
                        except Exception as e:
                            print(f"   ⚠️ Error al cargar texto del anexo: {e}")
                
                actualizados += 1
            
            if ensayo.tiene_anexo:
                con_anexo_despues += 1
        
        # Guardar cambios
        db.session.commit()
        
        print("="*60)
        print("✅ ACTUALIZACIÓN COMPLETADA")
        print("="*60)
        print(f"📊 Ensayos procesados: {total}")
        print(f"🔄 Ensayos actualizados: {actualizados}")
        print(f"📝 Con anexo (antes): {con_anexo_antes}")
        print(f"📝 Con anexo (después): {con_anexo_despues}")
        print(f"➕ Diferencia: +{con_anexo_despues - con_anexo_antes}")
        print()

if __name__ == '__main__':
    main()
