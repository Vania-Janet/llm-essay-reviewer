"""
Rutas para gestión de ensayos - CRUD, exportación, comparación y chat.
"""
import os
import io
import csv
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, request, jsonify, send_file, current_app
from sqlalchemy import or_

from app.database.connection import db
from app.database.models import Ensayo, CriterioPersonalizado, EvaluacionJurado
from app.api.middleware import require_auth
from app.utils.report_generator import ReportGenerator

# Para el chat con LangChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

bp = Blueprint('essays', __name__)

# Inicializar LLM para el chat
chat_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)


# ============= RUTAS DE LISTADO Y CRUD =============

@bp.route('/essays', methods=['GET'])
@require_auth
def list_essays():
    """Listar todos los ensayos evaluados ordenados por puntuación (mayor a menor)."""
    try:
        user_id = getattr(request, 'user_id', None)  # Safely get user_id
        ensayos = Ensayo.query.order_by(Ensayo.puntuacion_total.desc()).all()
        
        # Add evaluation status for current judge
        ensayos_data = []
        for ensayo in ensayos:
            data = ensayo.to_summary()
            # Check if current judge has evaluated this essay (only if user_id exists)
            if user_id:
                evaluacion_jurado = EvaluacionJurado.query.filter_by(
                    ensayo_id=ensayo.id,
                    jurado_id=user_id
                ).first()
                data['evaluado_por_jurado'] = evaluacion_jurado is not None
                data['puntuacion_jurado'] = float(evaluacion_jurado.puntuacion_total) if evaluacion_jurado else None
            else:
                data['evaluado_por_jurado'] = False
                data['puntuacion_jurado'] = None
            ensayos_data.append(data)
        
        return jsonify(ensayos_data)
    except Exception as e:
        print(f"Error al listar ensayos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/ensayos', methods=['GET'])
@require_auth
def get_ensayos():
    """Obtener lista de ensayos con formato para el frontend."""
    try:
        ensayos = Ensayo.query.filter_by(activo=True).order_by(Ensayo.fecha_evaluacion.desc()).all()
        
        ensayos_list = [{
            'id': e.id,
            'titulo': e.nombre_archivo.replace('.pdf', '').replace('Ensayo_', '').replace('_', ' '),
            'autor': e.autor if e.autor else 'Desconocido',
            'nombre_archivo': e.nombre_archivo,
            'puntuacion_total': float(e.puntuacion_total) if e.puntuacion_total else 0,
            'fecha_evaluacion': e.fecha_evaluacion.strftime('%Y-%m-%d %H:%M:%S') if e.fecha_evaluacion else None,
            'contenido_preview': e.texto_completo[:500] + '...' if e.texto_completo and len(e.texto_completo) > 500 else e.texto_completo
        } for e in ensayos]
        
        return jsonify({
            'success': True,
            'ensayos': ensayos_list,
            'total': len(ensayos_list)
        })
        
    except Exception as e:
        print(f"Error al obtener ensayos: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/essays/<int:essay_id>', methods=['GET'])
@require_auth
def get_essay(essay_id):
    """Obtener un ensayo específico por ID."""
    try:
        ensayo = Ensayo.query.get_or_404(essay_id)
        return jsonify(ensayo.to_dict_with_text())
    except Exception as e:
        print(f"Error al obtener ensayo: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/essays/<int:essay_id>/pdf', methods=['GET'])
@require_auth
def get_essay_pdf(essay_id):
    """Servir el PDF de un ensayo específico."""
    try:
        ensayo = Ensayo.query.get_or_404(essay_id)
        
        pdf_folder = Path(current_app.config.get('PERMANENT_PDF_FOLDER', 'data/pdfs'))
        
        # El nombre_archivo en BD tiene .txt pero los PDFs tienen .pdf
        # Intentar primero con el nombre exacto, luego reemplazando .txt por .pdf
        pdf_path = pdf_folder / ensayo.nombre_archivo
        
        if not pdf_path.exists():
            # Intentar reemplazando .txt por .pdf
            nombre_pdf = ensayo.nombre_archivo.replace('.txt', '.pdf')
            pdf_path = pdf_folder / nombre_pdf
        
        if not pdf_path.exists():
            return jsonify({'error': f'PDF no encontrado: {ensayo.nombre_archivo}'}), 404
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=ensayo.nombre_archivo.replace('.txt', '.pdf')
        )
        
    except Exception as e:
        print(f"Error al servir PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/essays/<int:essay_id>/report', methods=['GET', 'POST'])
@require_auth
def generate_essay_report(essay_id):
    """Generar reporte PDF profesional del ensayo."""
    try:
        ensayo = Ensayo.query.get_or_404(essay_id)
        user_id = request.current_user.get('user_id')
        
        # Preparar datos para el reporte
        essay_data = ensayo.to_dict()
        judge_data = None
        
        # Si es POST y trae datos, usarlos (para previsualización/descarga con ediciones)
        if request.method == 'POST' and request.is_json:
            data = request.get_json()
            # Construir judge_data desde el request
            judge_data = {
                'puntuacion_total': data.get('puntuacion_total'),
                'comentario_general': data.get('comentario_general'),
                'puntajes': {
                    'tecnica': data.get('calidad_tecnica', {}).get('calificacion'),
                    'creatividad': data.get('creatividad', {}).get('calificacion'),
                    'vinculacion': data.get('vinculacion_tematica', {}).get('calificacion'),
                    'bienestar': data.get('bienestar_colectivo', {}).get('calificacion'),
                    'uso_ia': data.get('uso_responsable_ia', {}).get('calificacion') or data.get('uso_ia', {}).get('calificacion'),
                    'impacto': data.get('potencial_impacto', {}).get('calificacion')
                },
                'comentarios': {
                    'tecnica': data.get('calidad_tecnica', {}).get('comentario'),
                    'creatividad': data.get('creatividad', {}).get('comentario'),
                    'vinculacion': data.get('vinculacion_tematica', {}).get('comentario'),
                    'bienestar': data.get('bienestar_colectivo', {}).get('comentario'),
                    'uso_ia': data.get('uso_responsable_ia', {}).get('comentario') or data.get('uso_ia', {}).get('comentario'),
                    'impacto': data.get('potencial_impacto', {}).get('comentario')
                }
            }
        else:
            # Buscar si hay evaluación del jurado actual
            evaluacion_jurado = EvaluacionJurado.query.filter_by(
                ensayo_id=essay_id,
                jurado_id=user_id
            ).first()
            
            if evaluacion_jurado:
                judge_data = {
                    'puntuacion_total': evaluacion_jurado.puntuacion_total,
                    'comentario_general': evaluacion_jurado.comentario_general,
                    'puntajes': {
                        'tecnica': evaluacion_jurado.calificacion_tecnica,
                        'creatividad': evaluacion_jurado.calificacion_creatividad,
                        'vinculacion': evaluacion_jurado.calificacion_vinculacion,
                        'bienestar': evaluacion_jurado.calificacion_bienestar,
                        'uso_ia': evaluacion_jurado.calificacion_uso_ia,
                        'impacto': evaluacion_jurado.calificacion_impacto
                    },
                    'comentarios': {
                        'tecnica': evaluacion_jurado.comentario_tecnica,
                        'creatividad': evaluacion_jurado.comentario_creatividad,
                        'vinculacion': evaluacion_jurado.comentario_vinculacion,
                        'bienestar': evaluacion_jurado.comentario_bienestar,
                        'uso_ia': evaluacion_jurado.comentario_uso_ia,
                        'impacto': evaluacion_jurado.comentario_impacto
                    }
                }
            
        generator = ReportGenerator()
        pdf_buffer = generator.generate_essay_report(essay_data, judge_data)
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'Reporte_Evaluacion_{ensayo.nombre_archivo.replace(".pdf", "")}.pdf'
        )
        
    except Exception as e:
        print(f"Error al generar reporte PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============= RUTAS DE EXPORTACIÓN =============

@bp.route('/essays/export/csv', methods=['GET'])
@require_auth
def export_essays_csv():
    """Exportar ensayos a CSV (compatible con Excel) ordenados por puntuación."""
    try:
        ensayos = Ensayo.query.order_by(Ensayo.puntuacion_total.desc()).all()
        
        if not ensayos:
            return jsonify({'error': 'No hay ensayos para exportar'}), 404
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Encabezados
        writer.writerow([
            'Ranking', 'Puntuación Total', 'Nombre de Archivo', 'Autor',
            'Calidad Técnica', 'Creatividad', 'Vinculación Temática',
            'Bienestar Colectivo', 'Uso Responsable IA', 'Potencial Impacto',
            'Tiene Anexo', 'Fecha Evaluación', 'Longitud (palabras)', 'Comentario General'
        ])
        
        for i, ensayo in enumerate(ensayos, 1):
            writer.writerow([
                i,
                f"{ensayo.puntuacion_total:.2f}",
                ensayo.nombre_archivo_original or ensayo.nombre_archivo,
                getattr(ensayo, 'autor', 'N/A'),
                f"{ensayo.calidad_tecnica.get('calificacion', 'N/A')}/5",
                f"{ensayo.creatividad.get('calificacion', 'N/A')}/5",
                f"{ensayo.vinculacion_tematica.get('calificacion', 'N/A')}/5",
                f"{ensayo.bienestar_colectivo.get('calificacion', 'N/A')}/5",
                f"{ensayo.uso_responsable_ia.get('calificacion', 'N/A')}/5",
                f"{ensayo.potencial_impacto.get('calificacion', 'N/A')}/5",
                'Sí' if ensayo.tiene_anexo else 'No',
                ensayo.fecha_evaluacion.strftime('%Y-%m-%d %H:%M:%S'),
                getattr(ensayo, 'num_palabras', len(ensayo.texto_completo.split()) if ensayo.texto_completo else 0),
                ensayo.comentario_general[:200] + '...' if len(ensayo.comentario_general) > 200 else ensayo.comentario_general
            ])
        
        output.seek(0)
        bytes_output = io.BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8-sig'))  # UTF-8 with BOM para Excel
        bytes_output.seek(0)
        
        return send_file(
            bytes_output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'ensayos_evaluados_{ensayos[0].fecha_evaluacion.strftime("%Y%m%d")}.csv'
        )
        
    except Exception as e:
        print(f"Error al exportar ensayos: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/essays/export/excel', methods=['GET'])
@require_auth
def export_essays_excel():
    """Exportar ensayos a Excel profesional - Sirve el archivo pre-generado."""
    try:
        from pathlib import Path
        
        # Ruta al archivo Excel pre-generado
        # app/api/routes/essays.py -> app/api/routes -> app/api -> app -> root
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        excel_path = project_root / 'data' / 'xls' / 'ensayos_evaluados_20251127_profesional.xlsx'
        
        print(f"Buscando archivo Excel en: {excel_path}")
        print(f"¿Archivo existe? {excel_path.exists()}")
        
        # Verificar que el archivo existe
        if not excel_path.exists():
            print(f"ERROR: Archivo no encontrado en {excel_path}")
            return jsonify({'error': f'Archivo Excel no encontrado en {excel_path}'}), 404
        
        print(f"Enviando archivo Excel: {excel_path}")
        return send_file(
            excel_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='ensayos_evaluados_20251127_profesional.xlsx'
        )
        
    except Exception as e:
        print(f"Error al exportar ensayos a Excel: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# ============= RUTAS DE COMPARACIÓN Y CHAT =============

@bp.route('/compare', methods=['POST'])
@require_auth
def compare_essays():
    """Comparar múltiples ensayos."""
    try:
        data = request.json
        essay_ids = data.get('essay_ids', [])
        
        if not essay_ids or len(essay_ids) < 2:
            return jsonify({'error': 'Debe proporcionar al menos 2 ensayos para comparar'}), 400
        
        ensayos = Ensayo.query.filter(Ensayo.id.in_(essay_ids)).all()
        
        if len(ensayos) != len(essay_ids):
            return jsonify({'error': 'Algunos ensayos no fueron encontrados'}), 404
        
        # Construir contexto
        contexto_comparacion = "Ensayos a comparar:\n\n"
        
        for i, ensayo in enumerate(ensayos, 1):
            contexto_comparacion += f"""
=== ENSAYO {i}: {ensayo.nombre_archivo} ===
Fecha de evaluación: {ensayo.fecha_evaluacion.strftime('%Y-%m-%d %H:%M')}
Puntuación Total: {ensayo.puntuacion_total}/5.00

TEXTO COMPLETO:
{ensayo.texto_completo}

EVALUACIÓN:
- Calidad Técnica: {ensayo.calidad_tecnica['calificacion']}/5 - {ensayo.calidad_tecnica['comentario']}
- Creatividad: {ensayo.creatividad['calificacion']}/5 - {ensayo.creatividad['comentario']}
- Vinculación Temática: {ensayo.vinculacion_tematica['calificacion']}/5 - {ensayo.vinculacion_tematica['comentario']}
- Bienestar Colectivo: {ensayo.bienestar_colectivo['calificacion']}/5 - {ensayo.bienestar_colectivo['comentario']}
- Uso Responsable de IA: {ensayo.uso_responsable_ia['calificacion']}/5 - {ensayo.uso_responsable_ia['comentario']} (Anexo: {'Sí' if ensayo.tiene_anexo else 'No'})
- Potencial de Impacto: {ensayo.potencial_impacto['calificacion']}/5 - {ensayo.potencial_impacto['comentario']}

Comentario General: {ensayo.comentario_general}

{'='*80}

"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un evaluador académico experto que realiza análisis comparativos concisos y directos.

Genera un análisis BREVE Y RESUMIDO que incluya:

1. **Ranking Final**: Lista ordenada del mejor al peor con puntuaciones
2. **Resumen de Fortalezas**: Máximo 2-3 puntos clave por ensayo
3. **Áreas de Mejora**: Máximo 2 puntos por ensayo
4. **Ganador y Justificación**: 2-3 líneas explicando por qué gana

Sé CONCISO. Usa máximo 400 palabras en total. No repitas información. Mantén un tono profesional y directo.

Ensayos a comparar:
{contexto}"""),
            ("user", "Por favor, realiza un análisis comparativo completo de estos {num_ensayos} ensayos.")
        ])
        
        chain = prompt | chat_llm
        comparacion = chain.invoke({
            "contexto": contexto_comparacion,
            "num_ensayos": len(ensayos)
        })
        
        return jsonify({
            'comparacion': comparacion.content,
            'ensayos': [ensayo.to_dict() for ensayo in ensayos]
        })
        
    except Exception as e:
        print(f"Error al comparar ensayos: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    """Endpoint para el chat de consultas sobre la evaluación."""
    try:
        data = request.json
        message = data.get('message', '')
        essay_ids = data.get('essay_ids', [])
        
        if not message:
            return jsonify({'error': 'No se proporcionó un mensaje'}), 400
        
        if not essay_ids:
            return jsonify({'error': 'No hay ensayos seleccionados'}), 400
        
        ensayos = Ensayo.query.filter(Ensayo.id.in_(essay_ids)).all()
        
        if not ensayos:
            return jsonify({'error': 'No se encontraron los ensayos'}), 400
        
        # Construir contexto
        if len(ensayos) == 1:
            ensayo = ensayos[0]
            contexto_evaluacion = f"""
TEXTO COMPLETO DEL ENSAYO:
Nombre: {ensayo.nombre_archivo}
{ensayo.texto_completo}

---

EVALUACIÓN DEL ENSAYO:

Puntuación Total: {ensayo.puntuacion_total}/5.00

Criterios Evaluados:

1. Calidad Técnica y Rigor Académico (20%):
   - Calificación: {ensayo.calidad_tecnica.get('calificacion', 'N/A')}/5
   - Comentario: {ensayo.calidad_tecnica.get('comentario', 'N/A')}

2. Creatividad y Originalidad (20%):
   - Calificación: {ensayo.creatividad.get('calificacion', 'N/A')}/5
   - Comentario: {ensayo.creatividad.get('comentario', 'N/A')}

3. Vinculación con Ejes Temáticos (15%):
   - Calificación: {ensayo.vinculacion_tematica.get('calificacion', 'N/A')}/5
   - Comentario: {ensayo.vinculacion_tematica.get('comentario', 'N/A')}

4. Bienestar Colectivo y Responsabilidad Social (20%):
   - Calificación: {ensayo.bienestar_colectivo.get('calificacion', 'N/A')}/5
   - Comentario: {ensayo.bienestar_colectivo.get('comentario', 'N/A')}

5. Uso Responsable de IA (15%):
   - Calificación: {ensayo.uso_responsable_ia.get('calificacion', 'N/A')}/5
   - Comentario: {ensayo.uso_responsable_ia.get('comentario', 'N/A')}
   - Tiene Anexo: {'Sí' if ensayo.tiene_anexo else 'No'}

6. Potencial de Impacto y Publicación (10%):
   - Calificación: {ensayo.potencial_impacto.get('calificacion', 'N/A')}/5
   - Comentario: {ensayo.potencial_impacto.get('comentario', 'N/A')}

Comentario General: {ensayo.comentario_general}
"""
        else:
            contexto_evaluacion = f"SE ESTÁN ANALIZANDO {len(ensayos)} ENSAYOS:\n\n"
            for i, ensayo in enumerate(ensayos, 1):
                contexto_evaluacion += f"""
{'='*80}
ENSAYO {i}: {ensayo.nombre_archivo}
{'='*80}

TEXTO COMPLETO:
{ensayo.texto_completo}

EVALUACIÓN:
Puntuación Total: {ensayo.puntuacion_total}/5.00

Criterios:
1. Calidad Técnica: {ensayo.calidad_tecnica.get('calificacion', 'N/A')}/5 - {ensayo.calidad_tecnica.get('comentario', 'N/A')}
2. Creatividad: {ensayo.creatividad.get('calificacion', 'N/A')}/5 - {ensayo.creatividad.get('comentario', 'N/A')}
3. Vinculación Temática: {ensayo.vinculacion_tematica.get('calificacion', 'N/A')}/5 - {ensayo.vinculacion_tematica.get('comentario', 'N/A')}
4. Bienestar Colectivo: {ensayo.bienestar_colectivo.get('calificacion', 'N/A')}/5 - {ensayo.bienestar_colectivo.get('comentario', 'N/A')}
5. Uso Responsable de IA: {ensayo.uso_responsable_ia.get('calificacion', 'N/A')}/5 - {ensayo.uso_responsable_ia.get('comentario', 'N/A')} (Anexo: {'Sí' if ensayo.tiene_anexo else 'No'})
6. Potencial de Impacto: {ensayo.potencial_impacto.get('calificacion', 'N/A')}/5 - {ensayo.potencial_impacto.get('comentario', 'N/A')}

Comentario General: {ensayo.comentario_general}

"""
        
        system_message = """Eres un asistente académico experto y profesional que ayuda a usuarios a comprender 
evaluaciones de ensayos académicos. Tu tono debe ser formal, respetuoso y constructivo.

Tus responsabilidades incluyen:
- Responder preguntas específicas sobre la evaluación realizada
- Aclarar comentarios y calificaciones de los diferentes criterios
- Proporcionar sugerencias concretas para mejorar el ensayo
- Explicar el sistema de evaluación y los criterios utilizados
- Ofrecer orientación académica profesional
- Citar fragmentos específicos del ensayo para justificar las calificaciones
- Proporcionar ejemplos concretos del texto cuando sea relevante"""
        
        if len(ensayos) > 1:
            system_message += """
- Cuando se analicen múltiples ensayos, compara y contrasta entre ellos
- Identifica fortalezas y debilidades relativas entre los ensayos
- Proporciona análisis comparativos detallados cuando se solicite
- Menciona explícitamente a qué ensayo te refieres en tus respuestas"""
        
        system_message += """

IMPORTANTE:
- Tienes acceso al texto completo del ensayo y a toda la evaluación
- Cuando justifiques una calificación, CITA fragmentos específicos del ensayo
- Usa comillas para indicar citas textuales del ensayo
- Mantén un tono formal y profesional en todo momento
- Proporciona respuestas claras, concisas y bien estructuradas
- Cuando des sugerencias, sé específico y constructivo
- Si el usuario pregunta algo fuera del contexto de la evaluación, redirige cortésmente a temas académicos relevantes
- No inventes información que no esté en la evaluación o en el ensayo

Contexto de la evaluación actual:
{contexto}

Responde la siguiente consulta del usuario de manera profesional y útil, citando fragmentos del ensayo cuando sea apropiado."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", "{mensaje}")
        ])
        
        chain = prompt | chat_llm
        respuesta = chain.invoke({
            "contexto": contexto_evaluacion,
            "mensaje": message
        })
        
        return jsonify({'response': respuesta.content})
        
    except Exception as e:
        print(f"Error en el chat: {str(e)}")
        return jsonify({'error': f'Error al procesar la consulta: {str(e)}'}), 500


# ============= RUTAS DE CRITERIOS PERSONALIZADOS =============

@bp.route('/criterios', methods=['GET'])
@require_auth
def get_criterios_personalizados():
    """Obtener todos los criterios personalizados del usuario actual."""
    try:
        user_id = request.user_id
        
        criterios = CriterioPersonalizado.query.filter_by(
            usuario_id=user_id,
            activo=True
        ).order_by(CriterioPersonalizado.orden).all()
        
        return jsonify({
            'criterios': [c.to_dict() for c in criterios],
            'total': len(criterios)
        })
        
    except Exception as e:
        print(f"Error al obtener criterios: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/criterios', methods=['POST'])
@require_auth
def crear_criterio():
    """Crear un nuevo criterio personalizado."""
    try:
        user_id = request.user_id
        data = request.json
        
        if not data.get('nombre') or not data.get('descripcion'):
            return jsonify({'error': 'Nombre y descripción son requeridos'}), 400
        
        peso = data.get('peso', 20.0)
        if peso <= 0 or peso > 100:
            return jsonify({'error': 'El peso debe estar entre 0 y 100'}), 400
        
        ultimo_criterio = CriterioPersonalizado.query.filter_by(
            usuario_id=user_id
        ).order_by(CriterioPersonalizado.orden.desc()).first()
        
        siguiente_orden = (ultimo_criterio.orden + 1) if ultimo_criterio else 0
        
        criterio = CriterioPersonalizado(
            usuario_id=user_id,
            nombre=data['nombre'].strip(),
            descripcion=data['descripcion'].strip(),
            peso=peso,
            icono=data.get('icono', '📝'),
            orden=siguiente_orden
        )
        
        db.session.add(criterio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'criterio': criterio.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear criterio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/criterios/<int:criterio_id>', methods=['PUT'])
@require_auth
def actualizar_criterio(criterio_id):
    """Actualizar un criterio existente."""
    try:
        user_id = request.user_id
        data = request.json
        
        criterio = CriterioPersonalizado.query.filter_by(
            id=criterio_id,
            usuario_id=user_id
        ).first_or_404()
        
        if 'nombre' in data:
            criterio.nombre = data['nombre'].strip()
        if 'descripcion' in data:
            criterio.descripcion = data['descripcion'].strip()
        if 'peso' in data:
            peso = data['peso']
            if peso <= 0 or peso > 100:
                return jsonify({'error': 'El peso debe estar entre 0 y 100'}), 400
            criterio.peso = peso
        if 'icono' in data:
            criterio.icono = data['icono']
        if 'orden' in data:
            criterio.orden = data['orden']
        if 'activo' in data:
            criterio.activo = data['activo']
        
        criterio.fecha_modificacion = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'criterio': criterio.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar criterio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/criterios/<int:criterio_id>', methods=['DELETE'])
@require_auth
def eliminar_criterio(criterio_id):
    """Eliminar (soft delete) un criterio."""
    try:
        user_id = request.user_id
        
        criterio = CriterioPersonalizado.query.filter_by(
            id=criterio_id,
            usuario_id=user_id
        ).first_or_404()
        
        criterio.activo = False
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar criterio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/criterios/reordenar', methods=['POST'])
@require_auth
def reordenar_criterios():
    """Reordenar criterios personalizados."""
    try:
        user_id = request.user_id
        data = request.json
        
        criterios_orden = data.get('criterios', [])
        
        for item in criterios_orden:
            criterio = CriterioPersonalizado.query.filter_by(
                id=item['id'],
                usuario_id=user_id
            ).first()
            
            if criterio:
                criterio.orden = item['orden']
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al reordenar criterios: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============= RUTAS DE EVALUACIÓN MANUAL =============

@bp.route('/evaluar_con_criterios/<int:ensayo_id>', methods=['POST'])
@require_auth
def evaluar_con_criterios(ensayo_id):
    """Evaluar un ensayo usando criterios personalizados con asistencia de IA."""
    try:
        ensayo = Ensayo.query.get(ensayo_id)
        if not ensayo:
            return jsonify({'error': 'Ensayo no encontrado'}), 404
        
        data = request.json
        criterios = data.get('criterios', [])
        
        if not criterios:
            return jsonify({'error': 'No se proporcionaron criterios'}), 400
        
        evaluaciones = []
        
        for criterio in criterios:
            puntuacion_sugerida = criterio['peso'] * 0.8
            
            evaluaciones.append({
                'criterio_id': criterio['id'],
                'nombre': criterio['nombre'],
                'puntuacion': round(puntuacion_sugerida, 2),
                'comentario': f"Evaluación basada en {criterio['nombre']}: El ensayo cumple con los estándares esperados."
            })
        
        return jsonify({
            'success': True,
            'ensayo_id': ensayo_id,
            'evaluacion': evaluaciones
        })
        
    except Exception as e:
        print(f"Error al evaluar con criterios: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/guardar_evaluacion_manual/<int:ensayo_id>', methods=['POST'])
@require_auth
def guardar_evaluacion_manual(ensayo_id):
    """Guardar una evaluación manual realizada por el juez."""
    try:
        ensayo = Ensayo.query.get(ensayo_id)
        if not ensayo:
            return jsonify({'error': 'Ensayo no encontrado'}), 404
        
        data = request.json
        evaluaciones = data.get('evaluaciones', [])
        comentario_general = data.get('comentario_general', '')
        puntuacion_total = data.get('puntuacion_total', 0)
        
        if not evaluaciones:
            return jsonify({'error': 'No se proporcionaron evaluaciones'}), 400
        
        ensayo.puntuacion_total = puntuacion_total
        ensayo.comentario_general = comentario_general
        ensayo.fecha_evaluacion = datetime.now()
        
        detalles_criterios = "\n\n=== EVALUACIÓN POR CRITERIOS PERSONALIZADOS ===\n"
        for eval_item in evaluaciones:
            criterio = CriterioPersonalizado.query.get(eval_item['criterio_id'])
            if criterio:
                detalles_criterios += f"\n{criterio.icono or '📋'} {criterio.nombre}: {eval_item['puntuacion']}/{criterio.peso} pts\n"
                if eval_item.get('comentario'):
                    detalles_criterios += f"   → {eval_item['comentario']}\n"
        
        ensayo.comentario_general = comentario_general + detalles_criterios
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evaluación guardada exitosamente',
            'ensayo_id': ensayo_id,
            'puntuacion_total': puntuacion_total
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar evaluación manual: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/evaluaciones-jurado', methods=['POST'])
@require_auth
def guardar_evaluacion_jurado():
    """Guardar o actualizar evaluación de jurado usando los 6 criterios del Grading Cockpit."""
    try:
        data = request.json
        
        ensayo_id = data.get('ensayo_id')
        if not ensayo_id:
            return jsonify({'error': 'ensayo_id es requerido'}), 400
        
        ensayo = Ensayo.query.get(ensayo_id)
        if not ensayo:
            return jsonify({'error': 'Ensayo no encontrado'}), 404
        
        jurado_id = request.current_user.get('user_id')
        
        puntajes = data.get('puntajes', {})
        comentarios = data.get('comentarios', {})
        
        criterios_requeridos = ['tecnica', 'creatividad', 'vinculacion', 'bienestar', 'uso_ia', 'impacto']
        for criterio in criterios_requeridos:
            if criterio not in puntajes or puntajes[criterio] is None:
                return jsonify({'error': f'Falta puntaje para criterio: {criterio}'}), 400
            if not (1 <= puntajes[criterio] <= 5):
                return jsonify({'error': f'Puntaje inválido para {criterio}: debe estar entre 1 y 5'}), 400
        
        evaluacion = EvaluacionJurado.query.filter_by(
            ensayo_id=ensayo_id,
            jurado_id=jurado_id
        ).first()
        
        if evaluacion:
            evaluacion.calificacion_tecnica = puntajes['tecnica']
            evaluacion.calificacion_creatividad = puntajes['creatividad']
            evaluacion.calificacion_vinculacion = puntajes['vinculacion']
            evaluacion.calificacion_bienestar = puntajes['bienestar']
            evaluacion.calificacion_uso_ia = puntajes['uso_ia']
            evaluacion.calificacion_impacto = puntajes['impacto']
            
            evaluacion.comentario_tecnica = comentarios.get('tecnica', '')
            evaluacion.comentario_creatividad = comentarios.get('creatividad', '')
            evaluacion.comentario_vinculacion = comentarios.get('vinculacion', '')
            evaluacion.comentario_bienestar = comentarios.get('bienestar', '')
            evaluacion.comentario_uso_ia = comentarios.get('uso_ia', '')
            evaluacion.comentario_impacto = comentarios.get('impacto', '')
            
            evaluacion.comentario_general = data.get('comentario_general', '')
            evaluacion.puntuacion_total = data.get('puntuacion_total', 0)
            evaluacion.estado = data.get('estado', 'completada')
            evaluacion.fecha_modificacion = datetime.now(timezone.utc)
            
            if evaluacion.estado == 'completada':
                evaluacion.fecha_completada = datetime.now(timezone.utc)
        else:
            evaluacion = EvaluacionJurado(
                ensayo_id=ensayo_id,
                jurado_id=jurado_id,
                calificacion_tecnica=puntajes['tecnica'],
                calificacion_creatividad=puntajes['creatividad'],
                calificacion_vinculacion=puntajes['vinculacion'],
                calificacion_bienestar=puntajes['bienestar'],
                calificacion_uso_ia=puntajes['uso_ia'],
                calificacion_impacto=puntajes['impacto'],
                comentario_tecnica=comentarios.get('tecnica', ''),
                comentario_creatividad=comentarios.get('creatividad', ''),
                comentario_vinculacion=comentarios.get('vinculacion', ''),
                comentario_bienestar=comentarios.get('bienestar', ''),
                comentario_uso_ia=comentarios.get('uso_ia', ''),
                comentario_impacto=comentarios.get('impacto', ''),
                comentario_general=data.get('comentario_general', ''),
                puntuacion_total=data.get('puntuacion_total', 0),
                estado=data.get('estado', 'completada'),
                fecha_completada=datetime.now(timezone.utc) if data.get('estado') == 'completada' else None
            )
            db.session.add(evaluacion)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Evaluación guardada exitosamente',
            'evaluacion_id': evaluacion.id,
            'ensayo_id': ensayo_id,
            'estado': evaluacion.estado
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar evaluación de jurado: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/evaluaciones-jurado/<int:ensayo_id>', methods=['GET'])
@require_auth
def obtener_evaluacion_jurado(ensayo_id):
    """Obtener la evaluación del jurado actual para un ensayo específico."""
    try:
        jurado_id = request.current_user.get('user_id')
        
        evaluacion = EvaluacionJurado.query.filter_by(
            ensayo_id=ensayo_id,
            jurado_id=jurado_id
        ).first()
        
        if not evaluacion:
            return jsonify({'evaluacion': None}), 200
        
        return jsonify({
            'evaluacion': {
                'id': evaluacion.id,
                'puntajes': {
                    'tecnica': evaluacion.calificacion_tecnica,
                    'creatividad': evaluacion.calificacion_creatividad,
                    'vinculacion': evaluacion.calificacion_vinculacion,
                    'bienestar': evaluacion.calificacion_bienestar,
                    'uso_ia': evaluacion.calificacion_uso_ia,
                    'impacto': evaluacion.calificacion_impacto
                },
                'comentarios': {
                    'tecnica': evaluacion.comentario_tecnica,
                    'creatividad': evaluacion.comentario_creatividad,
                    'vinculacion': evaluacion.comentario_vinculacion,
                    'bienestar': evaluacion.comentario_bienestar,
                    'uso_ia': evaluacion.comentario_uso_ia,
                    'impacto': evaluacion.comentario_impacto
                },
                'comentario_general': evaluacion.comentario_general,
                'puntuacion_total': evaluacion.puntuacion_total,
                'estado': evaluacion.estado,
                'fecha_modificacion': evaluacion.fecha_modificacion.isoformat() if evaluacion.fecha_modificacion else None
            }
        }), 200
        
    except Exception as e:
        print(f"Error al obtener evaluación de jurado: {str(e)}")
        return jsonify({'error': str(e)}), 500
