"""
Modelos de base de datos para almacenar ensayos y evaluaciones.
"""
import os
from datetime import datetime
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON

db = SQLAlchemy()


class Ensayo(db.Model):
    """Modelo para almacenar ensayos evaluados."""
    
    __tablename__ = 'ensayos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    texto_completo = db.Column(db.Text, nullable=False)
    fecha_evaluacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Evaluación almacenada como JSON
    puntuacion_total = db.Column(db.Float, nullable=False)
    calidad_tecnica = db.Column(JSON, nullable=False)
    creatividad = db.Column(JSON, nullable=False)
    vinculacion_tematica = db.Column(JSON, nullable=False)
    bienestar_colectivo = db.Column(JSON, nullable=False)
    potencial_impacto = db.Column(JSON, nullable=False)
    comentario_general = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        """Convierte el ensayo a un diccionario."""
        return {
            'id': self.id,
            'nombre_archivo': self.nombre_archivo,
            'fecha_evaluacion': self.fecha_evaluacion.isoformat(),
            'puntuacion_total': self.puntuacion_total,
            'calidad_tecnica': self.calidad_tecnica,
            'creatividad': self.creatividad,
            'vinculacion_tematica': self.vinculacion_tematica,
            'bienestar_colectivo': self.bienestar_colectivo,
            'potencial_impacto': self.potencial_impacto,
            'comentario_general': self.comentario_general
        }
    
    def to_dict_with_text(self):
        """Convierte el ensayo a un diccionario incluyendo el texto completo."""
        data = self.to_dict()
        data['texto_completo'] = self.texto_completo
        return data
    
    def to_summary(self):
        """Devuelve un resumen del ensayo para listados."""
        return {
            'id': self.id,
            'nombre_archivo': self.nombre_archivo,
            'fecha_evaluacion': self.fecha_evaluacion.isoformat(),
            'puntuacion_total': self.puntuacion_total,
            'texto_preview': self.texto_completo[:200] + '...' if len(self.texto_completo) > 200 else self.texto_completo
        }


def init_db(app):
    """Inicializa la base de datos."""
    # Configurar la base de datos SQLite
    db_path = Path(__file__).parent / 'essays.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print(f"✅ Base de datos inicializada en: {db_path}")
