"""
Entry point de la aplicación Flask.
"""
import os
from pathlib import Path
from flask import Flask, render_template, send_file, jsonify
from flask_cors import CORS

from app.config import get_config
from app.database.connection import init_db
from app.api.middleware import init_middleware

# Importar rutas
from app.api.routes import auth, evaluation, essays, admin

# Directorios base
BASE_DIR = Path(__file__).parent
TEMPLATE_DIR = BASE_DIR / 'app' / 'templates'
STATIC_DIR = BASE_DIR / 'app' / 'static'


def create_app(config_name=None):
    """
    Factory para crear la aplicación Flask.
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'testing')
    
    Returns:
        app: Instancia configurada de Flask
    """
    # Configurar static y template folders con rutas absolutas
    app = Flask(__name__, 
                static_folder=str(STATIC_DIR),
                static_url_path='/static',
                template_folder=str(TEMPLATE_DIR))
    
    # Cargar configuración
    config = get_config(config_name)
    config.init_app(app)
    
    # Inicializar extensiones
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)
    init_db(app)
    limiter, auth_manager = init_middleware(app)
    
    # Registrar blueprints
    app.register_blueprint(auth.bp, url_prefix='/api')
    app.register_blueprint(evaluation.bp, url_prefix='/api')
    app.register_blueprint(essays.bp, url_prefix='/api')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    
    # Rutas para servir templates
    @app.route('/')
    def index():
        """Servir página principal."""
        return render_template('index.html')
    
    @app.route('/login')
    def login():
        """Servir página de login."""
        return render_template('login.html')
    
    @app.route('/api/pdfs/<filename>')
    def serve_pdf(filename):
        """Servir PDFs con autenticación."""
        try:
            pdf_path = app.config['PERMANENT_PDF_FOLDER'] / filename
            
            if not pdf_path.exists():
                return jsonify({'error': 'PDF no encontrado'}), 404
            
            if not filename.endswith('.pdf'):
                return jsonify({'error': 'Archivo inválido'}), 400
            
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=False,
                download_name=filename
            )
        except Exception as e:
            print(f"Error al servir PDF: {e}")
            return jsonify({'error': 'Error al cargar PDF'}), 500
    
    # Health check
    @app.route('/health')
    def health():
        """Endpoint de health check."""
        return jsonify({
            'status': 'healthy',
            'environment': config_name or 'development'
        })
    
    return app


if __name__ == '__main__':
    # Obtener configuración desde variable de entorno
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    # Ejecutar servidor (puerto 5001 por defecto para evitar conflicto con AirPlay en macOS)
    debug = env == 'development'
    port = int(os.getenv('PORT', 5001))
    
    print(f"\nServidor iniciado en modo: {env}")
    print(f"URL: http://localhost:{port}")
    print(f"Debug: {debug}\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
