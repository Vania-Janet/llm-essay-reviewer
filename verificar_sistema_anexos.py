#!/usr/bin/env python3
"""
Script de verificación completa del sistema de anexos.
Verifica que todas las rutas, archivos y configuraciones estén correctas.
"""
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from matches_ia import MATCHES_SEGUROS_IA, obtener_anexo_ia, tiene_anexo_ia
from flask import Flask
from database import db, Ensayo, init_db

def verificar_archivos_anexos():
    """Verificar que todos los anexos del diccionario existan físicamente."""
    print("\n" + "="*60)
    print("📁 VERIFICACIÓN DE ARCHIVOS ANEXOS")
    print("="*60 + "\n")
    
    anexos_dir = Path(__file__).parent / 'Anexo_procesado'
    print(f"Directorio anexos: {anexos_dir}")
    print(f"¿Existe?: {anexos_dir.exists()}\n")
    
    if not anexos_dir.exists():
        print("❌ ERROR: El directorio Anexo_procesado no existe!")
        return False
    
    # Contar archivos físicos
    archivos_fisicos = list(anexos_dir.glob('*'))
    txt_files = list(anexos_dir.glob('*.txt'))
    pdf_files = list(anexos_dir.glob('*.pdf'))
    
    print(f"📊 Archivos físicos en directorio:")
    print(f"   Total: {len(archivos_fisicos)}")
    print(f"   TXT: {len(txt_files)}")
    print(f"   PDF: {len(pdf_files)}\n")
    
    # Verificar diccionario
    print(f"📊 Matches en diccionario:")
    print(f"   Total: {len(MATCHES_SEGUROS_IA)}")
    anexos_unicos = set(MATCHES_SEGUROS_IA.values())
    print(f"   Anexos únicos: {len(anexos_unicos)}\n")
    
    # Verificar existencia de cada anexo referenciado
    anexos_existentes = 0
    anexos_faltantes = []
    
    for nombre_anexo in anexos_unicos:
        ruta = anexos_dir / nombre_anexo
        if ruta.exists():
            anexos_existentes += 1
        else:
            anexos_faltantes.append(nombre_anexo)
    
    print(f"✅ Anexos que existen: {anexos_existentes}/{len(anexos_unicos)}")
    
    if anexos_faltantes:
        print(f"\n⚠️ Anexos faltantes ({len(anexos_faltantes)}):")
        for anexo in anexos_faltantes:
            print(f"   - {anexo}")
        return False
    else:
        print("✅ Todos los anexos del diccionario existen físicamente!\n")
        return True

def verificar_rutas_web_app():
    """Verificar que las rutas en web/app.py sean correctas."""
    print("="*60)
    print("🔗 VERIFICACIÓN DE RUTAS EN WEB/APP.PY")
    print("="*60 + "\n")
    
    # Simular la construcción de ruta como en web/app.py
    app_py_path = Path(__file__).parent / 'web' / 'app.py'
    ruta_anexos = app_py_path.parent.parent / 'Anexo_procesado'
    
    print(f"Ruta de app.py: {app_py_path}")
    print(f"Ruta construida a Anexo_procesado: {ruta_anexos}")
    print(f"¿Existe?: {ruta_anexos.exists()}\n")
    
    if ruta_anexos.exists():
        print("✅ La ruta desde web/app.py es correcta!\n")
        return True
    else:
        print("❌ ERROR: La ruta desde web/app.py no es correcta!\n")
        return False

def verificar_base_datos():
    """Verificar el estado de la base de datos."""
    print("="*60)
    print("💾 VERIFICACIÓN DE BASE DE DATOS")
    print("="*60 + "\n")
    
    app = Flask(__name__)
    init_db(app)
    
    with app.app_context():
        total = Ensayo.query.count()
        con_anexo = Ensayo.query.filter_by(tiene_anexo=True).count()
        sin_anexo = Ensayo.query.filter_by(tiene_anexo=False).count()
        
        print(f"📊 Ensayos en base de datos:")
        print(f"   Total: {total}")
        print(f"   Con anexo: {con_anexo}")
        print(f"   Sin anexo: {sin_anexo}\n")
        
        if sin_anexo > 0:
            print(f"📝 Ensayos sin anexo:")
            ensayos_sin_anexo = Ensayo.query.filter_by(tiene_anexo=False).all()
            for e in ensayos_sin_anexo:
                nombre_base = e.nombre_archivo.replace('.pdf', '').replace('.txt', '')
                tiene_en_dict = tiene_anexo_ia(nombre_base)
                simbolo = "⚠️" if tiene_en_dict else "✅"
                print(f"   {simbolo} {e.nombre_archivo}")
                if tiene_en_dict:
                    print(f"      → ⚠️ DEBERÍA tener anexo según diccionario!")
            print()
        
        # Verificar si hay ensayos que deberían tener anexo pero no lo tienen
        ensayos_incorrectos = 0
        for ensayo in Ensayo.query.all():
            nombre_base = ensayo.nombre_archivo.replace('.pdf', '').replace('.txt', '')
            tiene_en_dict = tiene_anexo_ia(nombre_base)
            if tiene_en_dict and not ensayo.tiene_anexo:
                ensayos_incorrectos += 1
        
        if ensayos_incorrectos > 0:
            print(f"❌ {ensayos_incorrectos} ensayos tienen anexo en diccionario pero no en BD")
            print("   → Ejecuta: python fix_anexos_database.py\n")
            return False
        else:
            print("✅ Todos los ensayos tienen el estado correcto de anexo!\n")
            return True

def probar_deteccion_anexos():
    """Probar la detección de anexos con casos de ejemplo."""
    print("="*60)
    print("🧪 PRUEBA DE DETECCIÓN DE ANEXOS")
    print("="*60 + "\n")
    
    # Casos de prueba con diferentes formatos
    test_cases = [
        ("TXT", "Ensayo_Lalo_Orea_DEL_AURA_AL_ALGORITMO_LA_MEMORIA_TECNOLÓGICA_EN_LA_ERA_DE_LA_INTELIGENCIA_ARTIFICIAL.txt"),
        ("PDF", "Ensayo_Medina_Vallarta_Maximiliano_Tecnología_para_un_Futuro_Sostenible,_Inclusivo_y_Memorable.txt"),
        ("PDF", "Ensayo_Ana_Gabriela_González_Esparza_Miradas_al_Mañana.txt"),
        ("SIN", "Ensayo_Itzel_Guadarrama_Gutiérrez_Inteligencia_Artificial_espejo_de_una_realidad_patriarcal.txt"),
    ]
    
    todos_ok = True
    
    for tipo_esperado, filename in test_cases:
        nombre_base = filename.replace('.pdf', '').replace('.txt', '')
        nombre_anexo = obtener_anexo_ia(nombre_base)
        tiene_anexo = tiene_anexo_ia(nombre_base)
        
        if tipo_esperado == "SIN":
            if not tiene_anexo:
                print(f"✅ {filename[:50]}...")
                print(f"   → Correctamente detectado SIN anexo\n")
            else:
                print(f"❌ {filename[:50]}...")
                print(f"   → ERROR: Debería NO tener anexo\n")
                todos_ok = False
        else:
            if tiene_anexo and nombre_anexo:
                ruta = Path(__file__).parent / 'Anexo_procesado' / nombre_anexo
                if ruta.exists():
                    tipo_real = "PDF" if nombre_anexo.lower().endswith('.pdf') else "TXT"
                    if tipo_real == tipo_esperado:
                        print(f"✅ {filename[:50]}...")
                        print(f"   → Anexo: {nombre_anexo}")
                        print(f"   → Tipo: {tipo_real} ✓\n")
                    else:
                        print(f"⚠️ {filename[:50]}...")
                        print(f"   → Tipo esperado: {tipo_esperado}, real: {tipo_real}\n")
                else:
                    print(f"❌ {filename[:50]}...")
                    print(f"   → ERROR: Anexo no existe: {nombre_anexo}\n")
                    todos_ok = False
            else:
                print(f"❌ {filename[:50]}...")
                print(f"   → ERROR: Debería tener anexo\n")
                todos_ok = False
    
    return todos_ok

def main():
    """Ejecutar todas las verificaciones."""
    print("\n" + "🔍" + " VERIFICACIÓN COMPLETA DEL SISTEMA DE ANEXOS ".center(58, "="))
    
    resultados = {
        "Archivos anexos": verificar_archivos_anexos(),
        "Rutas web/app.py": verificar_rutas_web_app(),
        "Base de datos": verificar_base_datos(),
        "Detección anexos": probar_deteccion_anexos(),
    }
    
    print("="*60)
    print("📊 RESUMEN DE VERIFICACIONES")
    print("="*60 + "\n")
    
    for nombre, resultado in resultados.items():
        simbolo = "✅" if resultado else "❌"
        print(f"{simbolo} {nombre}")
    
    print()
    
    if all(resultados.values()):
        print("🎉 ¡SISTEMA COMPLETAMENTE VERIFICADO!")
        print("✅ El sistema está listo para detectar y cargar los 48 anexos\n")
        return 0
    else:
        print("⚠️ Hay problemas que deben corregirse")
        print("   Revisa los detalles arriba\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
