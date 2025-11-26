"""
Servidor web Flask para el evaluador de ensayos.
"""
import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

# Agregar el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent))

from agent import EvaluadorEnsayos
from pdf_processor import PDFProcessor
from database import db, Ensayo, init_db
from matches_ia import obtener_anexo_ia, tiene_anexo_ia, MATCHES_SEGUROS_IA

# Importar para el chat
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

app = Flask(__name__, static_folder='.')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'

# Crear directorio de uploads si no existe
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Inicializar la base de datos
init_db(app)

# Inicializar el evaluador y el procesador de PDFs
evaluador = EvaluadorEnsayos()
pdf_processor = PDFProcessor()

# Inicializar LLM para el chat
chat_llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)


@app.route('/')
def index():
    """Servir la página principal."""
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Servir archivos estáticos."""
    return send_from_directory('.', path)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    """Endpoint para evaluar un ensayo."""
    try:
        # Verificar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'El archivo debe ser un PDF'}), 400
        
        # Guardar el archivo temporalmente
        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)
        
        try:
            # Extraer texto del PDF
            texto = pdf_processor.procesar_pdf(str(filepath), limpiar=True)
            
            if not texto or len(texto.strip()) < 100:
                return jsonify({
                    'error': 'No se pudo extraer suficiente texto del PDF'
                }), 400
            
            # Verificar si tiene anexo de IA en el diccionario de matches seguros
            nombre_base = filename.replace('.pdf', '').replace('.txt', '')
            nombre_anexo = obtener_anexo_ia(nombre_base)
            tiene_anexo_verificado = tiene_anexo_ia(nombre_base)
            
            # Cargar el texto del anexo si está disponible
            texto_anexo = None
            ruta_anexo = None
            nombre_autor_anexo = None
            
            if nombre_anexo:
                # Construir ruta al anexo
                ruta_anexo = Path(__file__).parent.parent / 'Anexo_procesado' / nombre_anexo
                
                # Intentar cargar el anexo
                if ruta_anexo.exists():
                    try:
                        with open(ruta_anexo, 'r', encoding='utf-8') as f:
                            texto_anexo = f.read()
                        print(f"✅ Anexo de IA cargado: {nombre_anexo}")
                        
                        # Extraer autor del anexo
                        nombre_autor_anexo = nombre_anexo.replace('AnexoIA_', '').replace('.txt', '').replace('_', ' ')
                    except Exception as e:
                        print(f"⚠️ Error al cargar anexo: {str(e)}")
                        texto_anexo = None
                else:
                    print(f"⚠️ Anexo no encontrado en ruta: {ruta_anexo}")
            
            # Evaluar el ensayo (con o sin anexo)
            evaluacion = evaluador.evaluar(texto, anexo_ia=texto_anexo)
            
            # Preparar datos de evaluación
            calidad_tecnica = {
                'calificacion': evaluacion.calidad_tecnica.calificacion,
                'comentario': evaluacion.calidad_tecnica.comentario,
                'fragmentos_destacados': [
                    {
                        'texto': f.texto,
                        'impacto': f.impacto,
                        'razon': f.razon
                    } for f in (evaluacion.calidad_tecnica.fragmentos_destacados or [])
                ]
            }
            creatividad = {
                'calificacion': evaluacion.creatividad.calificacion,
                'comentario': evaluacion.creatividad.comentario,
                'fragmentos_destacados': [
                    {
                        'texto': f.texto,
                        'impacto': f.impacto,
                        'razon': f.razon
                    } for f in (evaluacion.creatividad.fragmentos_destacados or [])
                ]
            }
            vinculacion_tematica = {
                'calificacion': evaluacion.vinculacion_tematica.calificacion,
                'comentario': evaluacion.vinculacion_tematica.comentario,
                'fragmentos_destacados': [
                    {
                        'texto': f.texto,
                        'impacto': f.impacto,
                        'razon': f.razon
                    } for f in (evaluacion.vinculacion_tematica.fragmentos_destacados or [])
                ]
            }
            bienestar_colectivo = {
                'calificacion': evaluacion.bienestar_colectivo.calificacion,
                'comentario': evaluacion.bienestar_colectivo.comentario,
                'fragmentos_destacados': [
                    {
                        'texto': f.texto,
                        'impacto': f.impacto,
                        'razon': f.razon
                    } for f in (evaluacion.bienestar_colectivo.fragmentos_destacados or [])
                ]
            }
            uso_responsable_ia = {
                'calificacion': evaluacion.uso_responsable_ia.calificacion,
                'comentario': evaluacion.uso_responsable_ia.comentario,
                'fragmentos_destacados': [
                    {
                        'texto': f.texto,
                        'impacto': f.impacto,
                        'razon': f.razon
                    } for f in (evaluacion.uso_responsable_ia.fragmentos_destacados or [])
                ]
            }
            potencial_impacto = {
                'calificacion': evaluacion.potencial_impacto.calificacion,
                'comentario': evaluacion.potencial_impacto.comentario,
                'fragmentos_destacados': [
                    {
                        'texto': f.texto,
                        'impacto': f.impacto,
                        'razon': f.razon
                    } for f in (evaluacion.potencial_impacto.fragmentos_destacados or [])
                ]
            }
            
            # Guardar en la base de datos
            ensayo = Ensayo(
                nombre_archivo=filename,
                texto_completo=texto,
                puntuacion_total=evaluacion.puntuacion_total,
                calidad_tecnica=calidad_tecnica,
                creatividad=creatividad,
                vinculacion_tematica=vinculacion_tematica,
                bienestar_colectivo=bienestar_colectivo,
                uso_responsable_ia=uso_responsable_ia,
                potencial_impacto=potencial_impacto,
                comentario_general=evaluacion.comentario_general,
                tiene_anexo=tiene_anexo_verificado,
                ruta_anexo=str(ruta_anexo) if ruta_anexo else None
            )
            db.session.add(ensayo)
            db.session.commit()
            
            # Convertir a diccionario para JSON
            resultado = {
                'id': ensayo.id,
                'texto_ensayo': texto[:500] + '...' if len(texto) > 500 else texto,
                'texto_completo': texto,
                'puntuacion_total': evaluacion.puntuacion_total,
                'calidad_tecnica': calidad_tecnica,
                'creatividad': creatividad,
                'vinculacion_tematica': vinculacion_tematica,
                'bienestar_colectivo': bienestar_colectivo,
                'uso_responsable_ia': uso_responsable_ia,
                'potencial_impacto': potencial_impacto,
                'comentario_general': evaluacion.comentario_general,
                'tiene_anexo': tiene_anexo_verificado,
                'nombre_anexo': nombre_anexo,
                'autor_anexo': nombre_autor_anexo
            }
            
            return jsonify(resultado)
            
        finally:
            # Eliminar el archivo temporal
            if filepath.exists():
                filepath.unlink()
    
    except Exception as e:
        print(f"Error al procesar el ensayo: {str(e)}")
        return jsonify({
            'error': f'Error al procesar el ensayo: {str(e)}'
        }), 500


@app.route('/chat', methods=['POST'])
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
        
        # Obtener los ensayos de la base de datos
        ensayos = Ensayo.query.filter(Ensayo.id.in_(essay_ids)).all()
        
        if not ensayos:
            return jsonify({'error': 'No se encontraron los ensayos'}), 400
        
        # Construir contexto para uno o múltiples ensayos
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
            # Contexto para múltiples ensayos
            contexto_evaluacion = f"SE ESTÁN ANALIZANDO {len(ensayos)} ENSAYOS:\n\n"
            for i, ensayo in enumerate(ensayos, 1):
                contexto_evaluacion += f"""
{'='*80}
ENSAYO {i}: {ensayo.nombre_archivo}
{'='*80}

TEXTO COMPLETO:
{ensayo.texto_completo}

---

EVALUACIÓN:

Puntuación Total: {ensayo.puntuacion_total}/5.00

Criterios Evaluados:

1. Calidad Técnica: {ensayo.calidad_tecnica.get('calificacion', 'N/A')}/5
   {ensayo.calidad_tecnica.get('comentario', 'N/A')}

2. Creatividad: {ensayo.creatividad.get('calificacion', 'N/A')}/5
   {ensayo.creatividad.get('comentario', 'N/A')}

3. Vinculación Temática: {ensayo.vinculacion_tematica.get('calificacion', 'N/A')}/5
   {ensayo.vinculacion_tematica.get('comentario', 'N/A')}

4. Bienestar Colectivo: {ensayo.bienestar_colectivo.get('calificacion', 'N/A')}/5
   {ensayo.bienestar_colectivo.get('comentario', 'N/A')}

5. Uso Responsable de IA: {ensayo.uso_responsable_ia.get('calificacion', 'N/A')}/5
   {ensayo.uso_responsable_ia.get('comentario', 'N/A')}
   Tiene Anexo: {'Sí' if ensayo.tiene_anexo else 'No'}

6. Potencial de Impacto: {ensayo.potencial_impacto.get('calificacion', 'N/A')}/5
   {ensayo.potencial_impacto.get('comentario', 'N/A')}

Comentario General: {ensayo.comentario_general}

"""
        
        # Crear el prompt para el chat
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
        
        # Generar respuesta
        chain = prompt | chat_llm
        respuesta = chain.invoke({
            "contexto": contexto_evaluacion,
            "mensaje": message
        })
        
        return jsonify({'response': respuesta.content})
        
    except Exception as e:
        print(f"Error en el chat: {str(e)}")
        return jsonify({
            'error': f'Error al procesar la consulta: {str(e)}'
        }), 500


@app.route('/essays', methods=['GET'])
def list_essays():
    """Listar todos los ensayos evaluados."""
    try:
        ensayos = Ensayo.query.order_by(Ensayo.fecha_evaluacion.desc()).all()
        return jsonify([ensayo.to_summary() for ensayo in ensayos])
    except Exception as e:
        print(f"Error al listar ensayos: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/essays/<int:essay_id>', methods=['GET'])
def get_essay(essay_id):
    """Obtener un ensayo específico por ID."""
    try:
        ensayo = Ensayo.query.get_or_404(essay_id)
        return jsonify(ensayo.to_dict_with_text())
    except Exception as e:
        print(f"Error al obtener ensayo: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/compare', methods=['POST'])
def compare_essays():
    """Comparar múltiples ensayos."""
    try:
        data = request.json
        essay_ids = data.get('essay_ids', [])
        
        if not essay_ids or len(essay_ids) < 2:
            return jsonify({
                'error': 'Debe proporcionar al menos 2 ensayos para comparar'
            }), 400
        
        # Obtener los ensayos
        ensayos = Ensayo.query.filter(Ensayo.id.in_(essay_ids)).all()
        
        if len(ensayos) != len(essay_ids):
            return jsonify({
                'error': 'Algunos ensayos no fueron encontrados'
            }), 404
        
        # Preparar el contexto de comparación
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
        
        # Crear el prompt para la comparación
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
        
        # Generar la comparación
        chain = prompt | chat_llm
        comparacion = chain.invoke({
            "contexto": contexto_comparacion,
            "num_ensayos": len(ensayos)
        })
        
        # Preparar respuesta
        resultado = {
            'comparacion': comparacion.content,
            'ensayos': [ensayo.to_dict() for ensayo in ensayos]
        }
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"Error al comparar ensayos: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def too_large(e):
    """Manejar archivos demasiado grandes."""
    return jsonify({
        'error': 'El archivo es demasiado grande. Tamaño máximo: 16MB'
    }), 413


if __name__ == '__main__':
    print("🚀 Iniciando servidor web en http://localhost:5001")
    print("📁 Carpeta de uploads:", app.config['UPLOAD_FOLDER'])
    app.run(debug=True, host='0.0.0.0', port=5001)
