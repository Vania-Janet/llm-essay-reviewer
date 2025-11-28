"""
Script para cargar ensayos y anexos ya procesados en la base de datos.
Este script procesa los archivos .txt de las carpetas pdfs_procesado y Anexo_procesado
y los evalúa con el agente de IA para guardar toda la información en la base de datos.
"""
import os
import sys
from pathlib import Path
from tqdm import tqdm
import re

# Agregar el directorio actual al path
sys.path.append(str(Path(__file__).parent))

from app.core.evaluator import EvaluadorEnsayos
from app.database.connection import db
from app.database.models import Ensayo
from flask import Flask
from matches_ia import MATCHES_SEGUROS_IA, obtener_anexo_ia, cargar_texto_anexo

def setup_app():
    """Configura la aplicación Flask y la base de datos."""
    app = Flask(__name__)
    
    # Configurar base de datos
    db_path = Path(__file__).parent / 'data' / 'essays.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print(f"Base de datos configurada en: {db_path}")
    
    return app

def extract_author_from_filename(filename: str) -> str:
    """
    Extrae el nombre del autor del nombre del archivo.
    Formato: Ensayo_[Autor]_[Titulo].txt o AnexoIA_[Autor]_[Titulo].txt
    """
    # Remover extensión
    name_without_ext = filename.replace('.txt', '').replace('.pdf', '')
    
    # Separar por guiones bajos
    parts = name_without_ext.split('_')
    
    if name_without_ext.startswith('Ensayo_'):
        # Formato: Ensayo_Nombre_Apellido_Titulo...
        # El autor puede tener múltiples partes (nombre y apellidos)
        # Buscar hasta encontrar palabras que parezcan título (mayúsculas)
        author_parts = []
        for i, part in enumerate(parts[1:], 1):  # Saltar 'Ensayo'
            # Si la parte tiene todas las palabras en mayúsculas o es muy larga, probablemente es título
            if part.isupper() and len(part) > 3:
                break
            # Si encontramos palabras comunes de títulos, detenemos
            if part.lower() in ['el', 'la', 'los', 'las', 'un', 'una', 'de', 'del']:
                break
            author_parts.append(part)
            if len(author_parts) >= 4:  # Máximo 4 partes para el nombre
                break
        
        return ' '.join(author_parts) if author_parts else 'Desconocido'
    
    elif name_without_ext.startswith('AnexoIA_'):
        # Similar para anexos
        author_parts = []
        for i, part in enumerate(parts[1:], 1):
            if part.isupper() and len(part) > 3:
                break
            if part.lower() in ['el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'uso', 'proceso']:
                break
            author_parts.append(part)
            if len(author_parts) >= 4:
                break
        
        return ' '.join(author_parts) if author_parts else 'Desconocido'
    
    return 'Desconocido'

def find_matching_anexo(essay_filename: str, anexos_folder: Path) -> tuple:
    """
    Busca el anexo correspondiente al ensayo usando el diccionario MATCHES_SEGUROS_IA.
    Retorna (ruta_anexo, texto_anexo) o (None, None) si no se encuentra.
    """
    # Buscar en el diccionario de matches seguros
    anexo_filename = obtener_anexo_ia(essay_filename)
    
    if anexo_filename:
        # Cargar el texto del anexo
        texto_anexo = cargar_texto_anexo(anexo_filename, str(anexos_folder))
        if texto_anexo:
            ruta_anexo = str(anexos_folder / anexo_filename)
            return (ruta_anexo, texto_anexo)
        else:
            print(f"   WARN: Anexo definido pero archivo no encontrado: {anexo_filename}")
    
    return (None, None)

def load_all_anexos(anexos_folder: Path) -> dict:
    """
    Carga todos los anexos en memoria.
    Retorna diccionario {ruta_completa: texto}
    """
    anexos_dict = {}
    
    if not anexos_folder.exists():
        print(f"WARN: Carpeta de anexos no encontrada: {anexos_folder}")
        return anexos_dict
    
    txt_files = list(anexos_folder.glob('*.txt'))
    
    print(f"Cargando {len(txt_files)} anexos...")
    
    for txt_file in txt_files:
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                texto = f.read().strip()
                if texto:
                    anexos_dict[txt_file] = texto
        except Exception as e:
            print(f"ERROR: Leyendo anexo {txt_file.name}: {e}")
    
    print(f"Cargados {len(anexos_dict)} anexos")
    return anexos_dict

def process_all_essays():
    """
    Procesa todos los ensayos de pdfs_procesado y los evalúa con el agente de IA.
    """
    # Configurar app y base de datos
    app = setup_app()
    
    # Inicializar evaluador
    evaluador = EvaluadorEnsayos()
    
    # Carpetas de trabajo
    pdfs_folder = Path(__file__).parent.parent / 'data' / 'processed'
    anexos_folder = Path(__file__).parent.parent / 'data' / 'anexos'
    
    if not pdfs_folder.exists():
        print(f"ERROR: Carpeta no encontrada: {pdfs_folder}")
        return
    
    # Mostrar estadísticas de matches
    print(f"\nMatches definidos en MATCHES_SEGUROS_IA: {len(MATCHES_SEGUROS_IA)}")
    
    # Obtener todos los archivos .txt de ensayos
    txt_files = list(pdfs_folder.glob('Ensayo_*.txt'))
    
    if not txt_files:
        print(f"ERROR: No se encontraron archivos .txt en {pdfs_folder}")
        return
    
    print(f"\nEncontrados {len(txt_files)} ensayos para procesar")
    print("=" * 80)
    
    processed = 0
    errors = 0
    skipped = 0
    con_anexo = 0
    sin_anexo = 0
    
    with app.app_context():
        for txt_file in tqdm(txt_files, desc="Procesando ensayos"):
            try:
                # Leer el texto del ensayo
                with open(txt_file, 'r', encoding='utf-8') as f:
                    texto_ensayo = f.read().strip()
                
                if not texto_ensayo:
                    print(f"\nWARN: Ensayo vacio: {txt_file.name}")
                    skipped += 1
                    continue
                
                # Extraer nombre del autor
                author = extract_author_from_filename(txt_file.name)
                
                # Buscar anexo correspondiente usando el diccionario de matches
                ruta_anexo, texto_anexo = find_matching_anexo(txt_file.name, anexos_folder)
                
                # Verificar si ya existe en la base de datos
                import hashlib
                texto_hash = hashlib.sha256(texto_ensayo.encode('utf-8')).hexdigest()
                
                existing = Ensayo.query.filter_by(texto_hash=texto_hash).first()
                if existing:
                    print(f"\nSKIP: Ensayo ya existe en BD: {txt_file.name}")
                    skipped += 1
                    continue
                
                # Evaluar el ensayo con el agente de IA
                print(f"\nEvaluando: {author}")
                try:
                    evaluacion = evaluador.evaluar(
                        ensayo=texto_ensayo,
                        anexo_ia=texto_anexo
                    )
                    
                    # Calcular puntuación total
                    puntuacion = evaluacion.calcular_puntuacion_total()
                    
                    # Crear registro en la base de datos
                    nuevo_ensayo = Ensayo(
                        nombre_archivo=txt_file.name,
                        autor=author,
                        texto_completo=texto_ensayo,
                        texto_hash=texto_hash,
                        puntuacion_total=puntuacion,
                        calidad_tecnica=evaluacion.calidad_tecnica.model_dump(),
                        creatividad=evaluacion.creatividad.model_dump(),
                        vinculacion_tematica=evaluacion.vinculacion_tematica.model_dump(),
                        bienestar_colectivo=evaluacion.bienestar_colectivo.model_dump(),
                        uso_responsable_ia=evaluacion.uso_responsable_ia.model_dump(),
                        potencial_impacto=evaluacion.potencial_impacto.model_dump(),
                        comentario_general=evaluacion.comentario_general,
                        tiene_anexo=texto_anexo is not None,
                        ruta_anexo=ruta_anexo,
                        texto_anexo=texto_anexo,
                        longitud_texto=len(texto_ensayo),
                        num_palabras=len(texto_ensayo.split())
                    )
                    
                    db.session.add(nuevo_ensayo)
                    db.session.commit()
                    
                    print(f"{author} - Puntuacion: {puntuacion:.2f}/5.00")
                    if ruta_anexo:
                        print(f"   Anexo encontrado: {Path(ruta_anexo).name}")
                        con_anexo += 1
                    else:
                        print(f"   WARN: Sin anexo")
                        sin_anexo += 1
                    
                    processed += 1
                    
                except KeyboardInterrupt:
                    print(f"\n\nWARN: Proceso interrumpido por el usuario")
                    print(f"Procesados hasta ahora: {processed}")
                    db.session.rollback()
                    raise
                except Exception as eval_error:
                    print(f"ERROR: Evaluando: {eval_error}")
                    errors += 1
                    db.session.rollback()
                    continue
                
            except Exception as e:
                print(f"\nERROR: Procesando {txt_file.name}: {e}")
                import traceback
                traceback.print_exc()
                errors += 1
                db.session.rollback()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DEL PROCESAMIENTO")
    print("=" * 80)
    print(f"Procesados exitosamente: {processed}")
    print(f"   Con anexo: {con_anexo}")
    print(f"   Sin anexo: {sin_anexo}")
    print(f"Omitidos (duplicados/vacios): {skipped}")
    print(f"Errores: {errors}")
    print(f"Total de archivos: {len(txt_files)}")
    print("=" * 80)
    
    if processed > 0:
        print("\nEnsayos cargados en la base de datos!")
        print(f"Base de datos: {Path(__file__).parent / 'essays.db'}")
        print("\nPuedes iniciar el servidor web con: python main.py")

if __name__ == "__main__":
    print("=" * 80)
    print("CARGA DE ENSAYOS PROCESADOS A BASE DE DATOS")
    print("=" * 80)
    print("\nEste script procesara todos los ensayos en pdfs_procesado/")
    print("y los evaluara con el agente de IA para guardarlos en la BD.\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        process_all_essays()
    else:
        print("Operacion cancelada")
