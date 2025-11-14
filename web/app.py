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

app = Flask(__name__, static_folder='.')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'

# Crear directorio de uploads si no existe
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Inicializar el evaluador y el procesador de PDFs
evaluador = EvaluadorEnsayos()
pdf_processor = PDFProcessor()


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
