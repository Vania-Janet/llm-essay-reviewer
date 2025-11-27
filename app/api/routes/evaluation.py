"""
Rutas para evaluación de ensayos con procesamiento asíncrono.
Incluye ThreadPoolExecutor para evaluaciones en background.
"""
import os
import uuid
import hashlib
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import db
from app.database.models import Ensayo
from app.api.middleware import require_auth
from app.core.evaluator import EvaluadorEnsayos
from app.utils.pdf_processor import PDFProcessor
from app.utils.attachment_matcher import obtener_anexo_ia, tiene_anexo_ia
from app.utils.logger import get_evaluation_logger

bp = Blueprint('evaluation', __name__)
logger = get_evaluation_logger()

# Inicializar componentes
evaluador = EvaluadorEnsayos()
pdf_processor = PDFProcessor()

# ThreadPoolExecutor para procesamiento asíncrono (3 workers)
executor = ThreadPoolExecutor(max_workers=3)

# Dict para tracking de jobs en proceso
processing_jobs = {}


def limpiar_jobs_antiguos():
    """
    Elimina jobs completados hace más de 5 minutos para prevenir memory leak.
    TTL (Time To Live) = 5 minutos después de completado.
    """
    ahora = datetime.now()
    jobs_a_eliminar = []
    
    for job_id, job in processing_jobs.items():
        if 'completed_at' in job:
            tiempo_transcurrido = ahora - job['completed_at']
            if tiempo_transcurrido > timedelta(minutes=5):
                jobs_a_eliminar.append(job_id)
    
    for job_id in jobs_a_eliminar:
        del processing_jobs[job_id]
        logger.debug(f"Job {job_id} removed from cache (TTL 5 minutes)")
    
    return len(jobs_a_eliminar)


def procesar_ensayo_fondo(job_id, filepath, permanent_pdf_path, texto, texto_hash,
                           original_filename, tiene_anexo_verificado, texto_anexo,
                           nombre_autor_anexo, usuario_id):
    """
    Función para procesar ensayo en background.
    Actualiza processing_jobs con el progreso y resultado.
    
    Estados del job:
    - queued: En cola, esperando worker disponible
    - processing: Evaluando con OpenAI
    - completed: Evaluación exitosa
    - error: Error durante el procesamiento
    """
    try:
        # Actualizar estado: procesando
        processing_jobs[job_id]['status'] = 'processing'
        processing_jobs[job_id]['progress'] = 10
        
        # Evaluar el ensayo con OpenAI
        evaluacion = evaluador.evaluar(texto, anexo_ia=texto_anexo)
        processing_jobs[job_id]['progress'] = 60
        
        if not evaluacion:
            processing_jobs[job_id]['status'] = 'error'
            processing_jobs[job_id]['error'] = 'No se pudo evaluar el ensayo'
            processing_jobs[job_id]['completed_at'] = datetime.now()
            return
        
        # Guardar en la base de datos
        nuevo_ensayo = Ensayo(
            texto_completo=texto,
            texto_hash=texto_hash,
            nombre_archivo_original=original_filename,
            puntuacion_total=evaluacion['puntuacion_total'],
            calidad_tecnica=evaluacion['calidad_tecnica'],
            creatividad=evaluacion['creatividad'],
            vinculacion_tematica=evaluacion['vinculacion_tematica'],
            bienestar_colectivo=evaluacion['bienestar_colectivo'],
            uso_responsable_ia=evaluacion['uso_responsable_ia'],
            potencial_impacto=evaluacion['potencial_impacto'],
            comentario_general=evaluacion['comentario_general'],
            tiene_anexo=tiene_anexo_verificado,
            pdf_path=str(permanent_pdf_path),
            nombre_autor_anexo=nombre_autor_anexo,
            usuario_id=usuario_id
        )
        
        db.session.add(nuevo_ensayo)
        db.session.commit()
        processing_jobs[job_id]['progress'] = 90
        
        # Preparar resultado para el frontend
        resultado = {
            'id': nuevo_ensayo.id,
            'texto_ensayo': texto[:500] + '...' if len(texto) > 500 else texto,
            'texto_completo': texto,
            'puntuacion_total': evaluacion['puntuacion_total'],
            'calidad_tecnica': evaluacion['calidad_tecnica'],
            'creatividad': evaluacion['creatividad'],
            'vinculacion_tematica': evaluacion['vinculacion_tematica'],
            'bienestar_colectivo': evaluacion['bienestar_colectivo'],
            'uso_responsable_ia': evaluacion['uso_responsable_ia'],
            'potencial_impacto': evaluacion['potencial_impacto'],
            'comentario_general': evaluacion['comentario_general'],
            'tiene_anexo': tiene_anexo_verificado,
            'cache_hit': False
        }
        
        # Actualizar con resultado exitoso
        processing_jobs[job_id]['status'] = 'completed'
        processing_jobs[job_id]['progress'] = 100
        processing_jobs[job_id]['result'] = resultado
        processing_jobs[job_id]['completed_at'] = datetime.now()
        
        logger.info(f"Job {job_id} completed successfully")
        
        # Limpiar archivo temporal
        try:
            filepath = Path(filepath)
            if filepath.exists():
                os.remove(filepath)
        except Exception as e:
            logger.warning(f"Error deleting temporary file: {e}")
            
    except Exception as e:
        processing_jobs[job_id]['status'] = 'error'
        processing_jobs[job_id]['error'] = str(e)
        processing_jobs[job_id]['completed_at'] = datetime.now()
        logger.error(f"Error processing essay (job {job_id}): {e}", exc_info=True)
        
        # Rollback si hay error de BD
        try:
            db.session.rollback()
        except:
            pass


@bp.route('/evaluate', methods=['POST'])
@require_auth
def evaluate():
    """
    Endpoint principal para evaluar un ensayo.
    
    Flujo:
    1. Recibe PDF, extrae texto
    2. Verifica hash para caché (evita re-evaluar duplicados)
    3. Si es nuevo, crea job y envía a ThreadPoolExecutor
    4. Retorna job_id para polling desde frontend
    
    Returns:
        - 200 con resultado si hay cache hit
        - 202 Accepted con job_id si se inicia procesamiento async
        - 400/500 en caso de error
    """
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'El archivo debe ser un PDF'}), 400
        
        # Configuración de carpetas
        upload_folder = Path(current_app.config.get('UPLOAD_FOLDER', 'data/uploads'))
        pdf_folder = Path(current_app.config.get('PERMANENT_PDF_FOLDER', 'data/pdfs'))
        anexo_folder = Path(current_app.config.get('PERMANENT_ANEXO_FOLDER', 'data/anexos'))
        
        # Asegurar que existen
        upload_folder.mkdir(parents=True, exist_ok=True)
        pdf_folder.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre único con UUID para evitar colisiones
        original_filename = secure_filename(file.filename)
        extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{extension}"
        
        # Guardar el archivo temporalmente para procesar
        filepath = upload_folder / unique_filename
        file.save(filepath)
        
        # Guardar copia permanente para el visor
        permanent_pdf_path = pdf_folder / unique_filename
        
        try:
            # Copiar a ubicación permanente
            shutil.copy2(filepath, permanent_pdf_path)
            print(f"✅ PDF guardado permanentemente en: {permanent_pdf_path}")
            
            # Extraer texto del PDF
            texto = pdf_processor.procesar_pdf(str(filepath), limpiar=True)
            
            if not texto or len(texto.strip()) < 100:
                # Limpiar archivos
                if filepath.exists():
                    os.remove(filepath)
                if permanent_pdf_path.exists():
                    os.remove(permanent_pdf_path)
                return jsonify({
                    'error': 'No se pudo extraer suficiente texto del PDF'
                }), 400
            
            # 🚀 HASH CACHE: Verificar si este texto ya fue evaluado
            texto_hash = hashlib.sha256(texto.encode('utf-8')).hexdigest()
            ensayo_existente = Ensayo.query.filter_by(texto_hash=texto_hash).first()
            
            if ensayo_existente:
                print(f"⚡ CACHE HIT: Ensayo duplicado encontrado (ID: {ensayo_existente.id})")
                print(f"   Hash: {texto_hash[:16]}...")
                print(f"   Archivo original: {ensayo_existente.nombre_archivo_original}")
                
                # Limpiar archivos temporales
                if filepath.exists():
                    os.remove(filepath)
                if permanent_pdf_path.exists():
                    os.remove(permanent_pdf_path)
                
                # Retornar evaluación existente sin llamar a OpenAI
                resultado = {
                    'id': ensayo_existente.id,
                    'texto_ensayo': ensayo_existente.texto_completo[:500] + '...' if len(ensayo_existente.texto_completo) > 500 else ensayo_existente.texto_completo,
                    'texto_completo': ensayo_existente.texto_completo,
                    'puntuacion_total': ensayo_existente.puntuacion_total,
                    'calidad_tecnica': ensayo_existente.calidad_tecnica,
                    'creatividad': ensayo_existente.creatividad,
                    'vinculacion_tematica': ensayo_existente.vinculacion_tematica,
                    'bienestar_colectivo': ensayo_existente.bienestar_colectivo,
                    'uso_responsable_ia': ensayo_existente.uso_responsable_ia,
                    'potencial_impacto': ensayo_existente.potencial_impacto,
                    'comentario_general': ensayo_existente.comentario_general,
                    'tiene_anexo': ensayo_existente.tiene_anexo,
                    'cache_hit': True,
                    'mensaje_cache': f'✨ Evaluación recuperada del caché (archivo original: {ensayo_existente.nombre_archivo_original})'
                }
                return jsonify(resultado)
            
            print(f"🔄 CACHE MISS: Evaluando nuevo ensayo con OpenAI")
            print(f"   Hash: {texto_hash[:16]}...")
            
            # Verificar si tiene anexo de IA
            nombre_base = original_filename.replace('.pdf', '').replace('.txt', '')
            nombre_anexo = obtener_anexo_ia(nombre_base)
            tiene_anexo_verificado = tiene_anexo_ia(nombre_base)
            
            # Cargar el texto del anexo si está disponible
            texto_anexo = None
            nombre_autor_anexo = None
            
            if nombre_anexo:
                ruta_anexo = anexo_folder / nombre_anexo
                if ruta_anexo.exists():
                    try:
                        if nombre_anexo.lower().endswith('.pdf'):
                            from app.utils.pdf_processor import extraer_texto_pdf
                            texto_anexo = extraer_texto_pdf(str(ruta_anexo))
                            print(f"✅ Anexo de IA PDF cargado: {nombre_anexo}")
                        else:
                            with open(ruta_anexo, 'r', encoding='utf-8') as f:
                                texto_anexo = f.read()
                            print(f"✅ Anexo de IA TXT cargado: {nombre_anexo}")
                        
                        nombre_autor_anexo = nombre_anexo.replace('AnexoIA_', '').replace('.txt', '').replace('.pdf', '').replace('_', ' ')
                    except Exception as e:
                        print(f"⚠️ Error al cargar anexo: {str(e)}")
                        texto_anexo = None
                else:
                    print(f"⚠️ Anexo no encontrado en ruta: {ruta_anexo}")
            
            # 🚀 ASYNC: Generar job ID y enviar a background
            job_id = str(uuid.uuid4())
            usuario_id = getattr(request, 'user_id', None)
            
            # Inicializar tracking del job
            processing_jobs[job_id] = {
                'status': 'queued',
                'progress': 0,
                'created_at': datetime.now(),
                'result': None,
                'error': None
            }
            
            # Enviar tarea al ThreadPoolExecutor
            executor.submit(
                procesar_ensayo_fondo,
                job_id, str(filepath), str(permanent_pdf_path), texto, texto_hash,
                original_filename, tiene_anexo_verificado, texto_anexo,
                nombre_autor_anexo, usuario_id
            )
            
            print(f"✅ Job {job_id} enviado a procesamiento en background")
            
            # Retornar job_id para que el frontend pueda hacer polling
            return jsonify({
                'job_id': job_id,
                'message': 'Ensayo en proceso de evaluación',
                'status': 'queued'
            }), 202  # 202 Accepted
            
        except Exception as e:
            # Si hay error antes de enviar al executor, limpiar archivos
            if filepath.exists():
                os.remove(filepath)
            if permanent_pdf_path.exists():
                os.remove(permanent_pdf_path)
            raise e
    
    except Exception as e:
        print(f"Error al procesar el ensayo: {str(e)}")
        return jsonify({
            'error': f'Error al procesar el ensayo: {str(e)}'
        }), 500


@bp.route('/job-status/<job_id>', methods=['GET'])
@require_auth
def job_status(job_id):
    """
    Endpoint para verificar el status de un job de procesamiento.
    El frontend hace polling cada 2 segundos hasta que el job completa.
    
    Returns:
        {
            status: 'queued' | 'processing' | 'completed' | 'error',
            progress: 0-100,
            result: {...} si completed,
            error: string si error
        }
    """
    job = processing_jobs.get(job_id)
    
    if not job:
        return jsonify({'error': 'Job no encontrado'}), 404
    
    response = {
        'status': job['status'],
        'progress': job['progress'],
        'created_at': job['created_at'].isoformat()
    }
    
    if job['status'] == 'completed':
        response['result'] = job['result']
        response['completed_at'] = job['completed_at'].isoformat()
    elif job['status'] == 'error':
        response['error'] = job['error']
        if 'completed_at' in job:
            response['completed_at'] = job['completed_at'].isoformat()
    
    return jsonify(response)


@bp.route('/cleanup-jobs', methods=['POST'])
def cleanup_jobs():
    """
    Endpoint para limpiar jobs antiguos manualmente.
    Puede ser llamado por un cron job o tarea programada.
    También se ejecuta automáticamente con TTL de 5 minutos.
    """
    antes = len(processing_jobs)
    eliminados = limpiar_jobs_antiguos()
    despues = len(processing_jobs)
    
    return jsonify({
        'message': f'Limpieza completada: {eliminados} jobs eliminados',
        'jobs_eliminados': eliminados,
        'jobs_activos': despues
    })


@bp.route('/jobs-stats', methods=['GET'])
@require_auth
def jobs_stats():
    """
    Obtener estadísticas de los jobs activos (para debugging/admin).
    """
    stats = {
        'total': len(processing_jobs),
        'queued': 0,
        'processing': 0,
        'completed': 0,
        'error': 0
    }
    
    for job in processing_jobs.values():
        status = job.get('status', 'unknown')
        if status in stats:
            stats[status] += 1
    
    return jsonify(stats)
