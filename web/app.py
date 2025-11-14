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

# Importar para el chat
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

app = Flask(__name__, static_folder='.')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'

# Crear directorio de uploads si no existe
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

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
            
            # Evaluar el ensayo
            evaluacion = evaluador.evaluar(texto)
            
            # Convertir a diccionario para JSON
            resultado = {
                'puntuacion_total': evaluacion.puntuacion_total,
                'calidad_tecnica': {
                    'calificacion': evaluacion.calidad_tecnica.calificacion,
                    'comentario': evaluacion.calidad_tecnica.comentario
                },
                'creatividad': {
                    'calificacion': evaluacion.creatividad.calificacion,
                    'comentario': evaluacion.creatividad.comentario
                },
                'vinculacion_tematica': {
                    'calificacion': evaluacion.vinculacion_tematica.calificacion,
                    'comentario': evaluacion.vinculacion_tematica.comentario
                },
                'bienestar_colectivo': {
                    'calificacion': evaluacion.bienestar_colectivo.calificacion,
                    'comentario': evaluacion.bienestar_colectivo.comentario
                },
                'potencial_impacto': {
                    'calificacion': evaluacion.potencial_impacto.calificacion,
                    'comentario': evaluacion.potencial_impacto.comentario
                },
                'comentario_general': evaluacion.comentario_general
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
        evaluation = data.get('evaluation', {})
        
        if not message:
            return jsonify({'error': 'No se proporcionó un mensaje'}), 400
        
        if not evaluation:
            return jsonify({'error': 'No hay evaluación disponible'}), 400
        
        # Construir contexto de la evaluación
        contexto_evaluacion = f"""
EVALUACIÓN DEL ENSAYO:

Puntuación Total: {evaluation.get('puntuacion_total', 'N/A')}/5.00

Criterios Evaluados:

1. Calidad Técnica y Rigor Académico (20%):
   - Calificación: {evaluation.get('calidad_tecnica', {}).get('calificacion', 'N/A')}/5
   - Comentario: {evaluation.get('calidad_tecnica', {}).get('comentario', 'N/A')}

2. Creatividad y Originalidad (20%):
   - Calificación: {evaluation.get('creatividad', {}).get('calificacion', 'N/A')}/5
   - Comentario: {evaluation.get('creatividad', {}).get('comentario', 'N/A')}

3. Vinculación con Ejes Temáticos (15%):
   - Calificación: {evaluation.get('vinculacion_tematica', {}).get('calificacion', 'N/A')}/5
   - Comentario: {evaluation.get('vinculacion_tematica', {}).get('comentario', 'N/A')}

4. Bienestar Colectivo y Responsabilidad Social (20%):
   - Calificación: {evaluation.get('bienestar_colectivo', {}).get('calificacion', 'N/A')}/5
   - Comentario: {evaluation.get('bienestar_colectivo', {}).get('comentario', 'N/A')}

5. Potencial de Impacto y Publicación (20%):
   - Calificación: {evaluation.get('potencial_impacto', {}).get('calificacion', 'N/A')}/5
   - Comentario: {evaluation.get('potencial_impacto', {}).get('comentario', 'N/A')}

Comentario General: {evaluation.get('comentario_general', 'N/A')}
"""
        
        # Crear el prompt para el chat
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Eres un asistente académico experto y profesional que ayuda a usuarios a comprender 
evaluaciones de ensayos académicos. Tu tono debe ser formal, respetuoso y constructivo.

Tus responsabilidades incluyen:
- Responder preguntas específicas sobre la evaluación realizada
- Aclarar comentarios y calificaciones de los diferentes criterios
- Proporcionar sugerencias concretas para mejorar el ensayo
- Explicar el sistema de evaluación y los criterios utilizados
- Ofrecer orientación académica profesional

IMPORTANTE:
- Mantén un tono formal y profesional en todo momento
- Proporciona respuestas claras, concisas y bien estructuradas
- Cuando des sugerencias, sé específico y constructivo
- Si el usuario pregunta algo fuera del contexto de la evaluación, redirige cortésmente a temas académicos relevantes
- No inventes información que no esté en la evaluación

Contexto de la evaluación actual:
{contexto}

Responde la siguiente consulta del usuario de manera profesional y útil."""),
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
