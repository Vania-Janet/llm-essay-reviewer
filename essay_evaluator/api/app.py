"""
Servidor web Flask para el evaluador de ensayos.
"""
import os
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
import io
import csv
import shutil  # Para copiar PDFs permanentemente

# Agregar el directorio padre al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

from essay_evaluator.core.agent.evaluator import EvaluadorEnsayos
from essay_evaluator.utils.pdf.processor import PDFProcessor
from essay_evaluator.utils.database.connection import db, Ensayo, Usuario, CriterioPersonalizado, init_db
from essay_evaluator.api.routes.auth import AuthManager, require_auth, validate_password_strength

# TODO: Move to separate module
# from matches_ia import obtener_anexo_ia, tiene_anexo_ia, MATCHES_SEGUROS_IA

# Importar para el chat
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Get the base directory (essay-agent root)
BASE_DIR = Path(__file__).parent.parent.parent
STATIC_DIR = Path(__file__).parent.parent / 'web' / 'static'
TEMPLATE_DIR = Path(__file__).parent.parent / 'web' / 'templates'

app = Flask(__name__, 
            static_folder=str(STATIC_DIR),
            template_folder=str(TEMPLATE_DIR))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = BASE_DIR / 'essay_evaluator' / 'data' / 'raw'

# Configuración de seguridad
is_production = os.getenv('FLASK_ENV') == 'production'
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY') or os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = is_production  # Solo HTTPS en producción
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevenir acceso JavaScript
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Crear directorio de uploads si no existe
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Inicializar la base de datos
init_db(app)

# Inicializar el evaluador y el procesador de PDFs
evaluador = EvaluadorEnsayos()
pdf_processor = PDFProcessor()

# Inicializar gestor de autenticación
auth_manager = AuthManager()

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


# ============= RUTAS DE AUTENTICACIÓN =============

@app.route('/api/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario."""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        nombre_completo = data.get('nombre_completo', '').strip()
        
        # Validar longitud de usuario
        if len(username) < 3:
            return jsonify({'error': 'El nombre de usuario debe tener al menos 3 caracteres'}), 400
        
        # Validar formato de email básico
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Email inválido'}), 400
        
        # Validar fortaleza de contraseña
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            return jsonify({'error': 'El nombre de usuario ya está en uso'}), 409
        
        if Usuario.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        # Crear nuevo usuario con contraseña hasheada
        password_hash = auth_manager.hash_password(password)
        
        nuevo_usuario = Usuario(
            username=username,
            email=email,
            password_hash=password_hash,
            nombre_completo=nombre_completo
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # Generar token
        token = auth_manager.generate_token(str(nuevo_usuario.id), nuevo_usuario.username)
        
        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'token': token,
            'user': nuevo_usuario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar usuario: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Autenticar usuario y generar token."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['username', 'password']):
            return jsonify({'error': 'Usuario y contraseña requeridos'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Buscar usuario
        usuario = Usuario.query.filter_by(username=username).first()
        
        if not usuario:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not usuario.activo:
            return jsonify({'error': 'Usuario inactivo'}), 403
        
        # Verificar contraseña
        if not auth_manager.verify_password(password, usuario.password_hash):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        # Actualizar último acceso
        usuario.ultimo_acceso = datetime.now()
        db.session.commit()
        
        # Generar token
        token = auth_manager.generate_token(str(usuario.id), usuario.username)
        
        return jsonify({
            'message': 'Login exitoso',
            'token': token,
            'user': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al iniciar sesión: {str(e)}'}), 500


@app.route('/api/verify-token', methods=['GET'])
@require_auth
def verify_token():
    """Verificar si el token es válido."""
    return jsonify({
        'valid': True,
        'user': request.current_user
    }), 200


@app.route('/api/db-status', methods=['GET'])
def db_status():
    """Verificar el estado de la base de datos (sin autenticación requerida para debug)."""
    try:
        ensayo_count = Ensayo.query.count()
        usuario_count = Usuario.query.count()
        
        # ✅ SEGURIDAD: No exponer credenciales de BD
        return jsonify({
            'status': 'connected',
            'ensayos': ensayo_count,
            'usuarios': usuario_count,
            'database_configured': True  # Solo confirma que existe
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': 'Database connection failed'
        }), 500


@app.route('/api/change-password', methods=['POST'])
@require_auth
def change_password():
    """Cambiar contraseña del usuario."""
    try:
        data = request.get_json()
        
        if not all(k in data for k in ['current_password', 'new_password']):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        user_id = request.current_user['user_id']
        usuario = Usuario.query.get(user_id)
        
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Verificar contraseña actual
        if not auth_manager.verify_password(data['current_password'], usuario.password_hash):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 401
        
        # Validar nueva contraseña
        is_valid, message = validate_password_strength(data['new_password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Actualizar contraseña
        usuario.password_hash = auth_manager.hash_password(data['new_password'])
        db.session.commit()
        
        return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cambiar contraseña: {str(e)}'}), 500


# ============= RUTAS DE EVALUACIÓN (PROTEGIDAS) =============

@app.route('/evaluate', methods=['POST'])
@require_auth
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
        
        # Guardar el archivo temporalmente para procesar
        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)
        
        # 💾 GUARDAR COPIA PERMANENTE para el visor del juez
        permanent_pdf_dir = Path(__file__).parent.parent / 'pdfs_procesado'
        permanent_pdf_dir.mkdir(exist_ok=True)  # Crear carpeta si no existe
        permanent_pdf_path = permanent_pdf_dir / filename
        
        try:
            # Copiar a ubicación permanente
            shutil.copy2(filepath, permanent_pdf_path)
            print(f"✅ PDF guardado permanentemente en: {permanent_pdf_path}")
            
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
@require_auth
def list_essays():
    """Listar todos los ensayos evaluados ordenados por puntuación (mayor a menor)."""
    try:
        ensayos = Ensayo.query.order_by(Ensayo.puntuacion_total.desc()).all()
        return jsonify([ensayo.to_summary() for ensayo in ensayos])
    except Exception as e:
        print(f"Error al listar ensayos: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/essays/export/csv', methods=['GET'])
@require_auth
def export_essays_csv():
    """Exportar ensayos a CSV (compatible con Excel) ordenados por puntuación."""
    try:
        # Obtener todos los ensayos ordenados por puntuación
        ensayos = Ensayo.query.order_by(Ensayo.puntuacion_total.desc()).all()
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow([
            'Ranking',
            'Puntuación Total',
            'Nombre de Archivo',
            'Autor',
            'Calidad Técnica',
            'Creatividad',
            'Vinculación Temática',
            'Bienestar Colectivo',
            'Uso Responsable IA',
            'Potencial Impacto',
            'Tiene Anexo',
            'Fecha Evaluación',
            'Longitud (palabras)',
            'Comentario General'
        ])
        
        # Escribir datos
        for i, ensayo in enumerate(ensayos, 1):
            writer.writerow([
                i,  # Ranking
                f"{ensayo.puntuacion_total:.2f}",
                ensayo.nombre_archivo,
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
        
        # Convertir a bytes para enviar
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


@app.route('/essays/<int:essay_id>', methods=['GET'])
@require_auth
def get_essay(essay_id):
    """Obtener un ensayo específico por ID."""
    try:
        ensayo = Ensayo.query.get_or_404(essay_id)
        return jsonify(ensayo.to_dict_with_text())
    except Exception as e:
        print(f"Error al obtener ensayo: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/essays/<int:essay_id>/pdf', methods=['GET'])
@require_auth
def get_essay_pdf(essay_id):
    """Servir el PDF de un ensayo específico."""
    try:
        ensayo = Ensayo.query.get_or_404(essay_id)
        
        # Construir la ruta al PDF original
        # Los PDFs están en /pdfs_procesado/
        pdf_dir = Path(__file__).parent.parent / 'pdfs_procesado'
        
        # El nombre del archivo es el nombre_archivo del ensayo
        # Quitar el .txt y agregar .pdf
        pdf_filename = ensayo.nombre_archivo.replace('_procesado.txt', '.pdf')
        pdf_path = pdf_dir / pdf_filename
        
        if not pdf_path.exists():
            # Intentar sin el sufijo _procesado
            pdf_filename_alt = ensayo.nombre_archivo.replace('.txt', '.pdf')
            pdf_path = pdf_dir / pdf_filename_alt
            
            if not pdf_path.exists():
                return jsonify({'error': 'PDF no encontrado'}), 404
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=pdf_filename
        )
        
    except Exception as e:
        print(f"Error al servir PDF: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ENDPOINTS DE CRITERIOS PERSONALIZADOS
# ============================================================================

@app.route('/api/criterios', methods=['GET'])
@require_auth
def get_criterios_personalizados():
    """Obtener todos los criterios personalizados del usuario actual."""
    try:
        user_id = request.user_id  # Viene del decorator @require_auth
        
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


@app.route('/api/criterios', methods=['POST'])
@require_auth
def crear_criterio():
    """Crear un nuevo criterio personalizado."""
    try:
        user_id = request.user_id
        data = request.json
        
        # Validar datos requeridos
        if not data.get('nombre') or not data.get('descripcion'):
            return jsonify({'error': 'Nombre y descripción son requeridos'}), 400
        
        peso = data.get('peso', 20.0)
        if peso <= 0 or peso > 100:
            return jsonify({'error': 'El peso debe estar entre 0 y 100'}), 400
        
        # Obtener el siguiente orden
        ultimo_criterio = CriterioPersonalizado.query.filter_by(
            usuario_id=user_id
        ).order_by(CriterioPersonalizado.orden.desc()).first()
        
        siguiente_orden = (ultimo_criterio.orden + 1) if ultimo_criterio else 0
        
        # Crear criterio
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


@app.route('/api/criterios/<int:criterio_id>', methods=['PUT'])
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
        
        # Actualizar campos
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
        
        criterio.fecha_modificacion = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'criterio': criterio.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar criterio: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/criterios/<int:criterio_id>', methods=['DELETE'])
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


@app.route('/api/criterios/reordenar', methods=['POST'])
@require_auth
def reordenar_criterios():
    """Reordenar criterios personalizados."""
    try:
        user_id = request.user_id
        data = request.json
        
        # data debe ser: {'criterios': [{'id': 1, 'orden': 0}, {'id': 2, 'orden': 1}, ...]}
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


@app.route('/compare', methods=['POST'])
@require_auth
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


@app.route('/api/evaluar_con_criterios/<int:ensayo_id>', methods=['POST'])
@require_auth
def evaluar_con_criterios(ensayo_id):
    """Evaluar un ensayo usando criterios personalizados con asistencia de IA."""
    try:
        # Obtener el ensayo
        ensayo = Ensayo.query.get(ensayo_id)
        if not ensayo:
            return jsonify({'error': 'Ensayo no encontrado'}), 404
        
        data = request.json
        criterios = data.get('criterios', [])
        
        if not criterios:
            return jsonify({'error': 'No se proporcionaron criterios'}), 400
        
        # Aquí puedes implementar la lógica de evaluación con IA
        # Por ahora, retornaremos sugerencias basadas en el peso de cada criterio
        evaluaciones = []
        
        for criterio in criterios:
            # Simulación de evaluación con IA (puedes integrar tu modelo aquí)
            puntuacion_sugerida = criterio['peso'] * 0.8  # Ejemplo: 80% del peso máximo
            
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


@app.route('/api/guardar_evaluacion_manual/<int:ensayo_id>', methods=['POST'])
@require_auth
def guardar_evaluacion_manual(ensayo_id):
    """Guardar una evaluación manual realizada por el juez."""
    try:
        # Obtener el ensayo
        ensayo = Ensayo.query.get(ensayo_id)
        if not ensayo:
            return jsonify({'error': 'Ensayo no encontrado'}), 404
        
        data = request.json
        evaluaciones = data.get('evaluaciones', [])
        comentario_general = data.get('comentario_general', '')
        puntuacion_total = data.get('puntuacion_total', 0)
        
        if not evaluaciones:
            return jsonify({'error': 'No se proporcionaron evaluaciones'}), 400
        
        # Actualizar el ensayo con la nueva evaluación
        ensayo.puntuacion_total = puntuacion_total
        ensayo.comentario_general = comentario_general
        ensayo.fecha_evaluacion = datetime.now()
        
        # Aquí puedes guardar las evaluaciones por criterio en una tabla separada
        # si decides crear un modelo EvaluacionCriterio en el futuro
        
        # Por ahora, guardamos un resumen en el comentario general
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


@app.route('/api/ensayos', methods=['GET'])
@require_auth
def get_ensayos():
    """Obtener lista de ensayos."""
    try:
        # Obtener todos los ensayos activos
        ensayos = Ensayo.query.filter_by(activo=True).order_by(Ensayo.fecha_evaluacion.desc()).all()
        
        ensayos_list = [{
            'id': e.id,
            'titulo': e.nombre_archivo.replace('.pdf', '').replace('Ensayo_', '').replace('_', ' '),
            'autor': e.autor if e.autor else 'Desconocido',
            'nombre_archivo': e.nombre_archivo,
            'puntuacion_total': float(e.puntuacion_total) if e.puntuacion_total else 0,
            'fecha_evaluacion': e.fecha_evaluacion.strftime('%Y-%m-%d %H:%M:%S') if e.fecha_evaluacion else None,
            'contenido_preview': e.texto_completo[:200] + '...' if e.texto_completo and len(e.texto_completo) > 200 else e.texto_completo
        } for e in ensayos]
        
        return jsonify({
            'success': True,
            'ensayos': ensayos_list,
            'total': len(ensayos_list)
        })
        
    except Exception as e:
        print(f"Error al obtener ensayos: {str(e)}")
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
