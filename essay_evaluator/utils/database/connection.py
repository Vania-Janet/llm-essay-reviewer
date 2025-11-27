"""
Modelos de base de datos para almacenar ensayos, evaluaciones y comparaciones.
Optimizado con índices para búsquedas rápidas y cache de comparaciones.
"""
import os
import hashlib
from datetime import datetime
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON, Index, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Usuario(db.Model):
    """Modelo para usuarios del sistema con contraseñas hasheadas."""
    
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # bcrypt hash
    nombre_completo = db.Column(db.String(200), nullable=True)
    rol = db.Column(db.String(50), default='usuario', nullable=False)  # usuario, admin, etc.
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Usuario {self.username}>'
    
    def to_dict(self):
        """Convertir usuario a diccionario (sin password_hash)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nombre_completo': self.nombre_completo,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None
        }


class CriterioPersonalizado(db.Model):
    """Modelo para criterios de evaluación personalizados creados por jueces/usuarios."""
    
    __tablename__ = 'criterios_personalizados'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Información del criterio
    nombre = db.Column(db.String(100), nullable=False)  # "Claridad de escritura", "Uso de datos", etc.
    descripcion = db.Column(db.Text, nullable=False)  # Qué evalúa este criterio
    peso = db.Column(db.Float, nullable=False, default=20.0)  # Porcentaje del total (debe sumar 100 entre todos)
    icono = db.Column(db.String(10), nullable=True, default='📝')  # Emoji para UI
    
    # Orden de presentación
    orden = db.Column(db.Integer, nullable=False, default=0)
    
    # Control
    activo = db.Column(db.Boolean, default=True, nullable=False, index=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con usuario
    usuario = relationship('Usuario', backref='criterios_personalizados')
    
    # Índice para búsquedas del usuario
    __table_args__ = (
        Index('idx_usuario_activo', 'usuario_id', 'activo'),
        Index('idx_usuario_orden', 'usuario_id', 'orden'),
    )
    
    def __repr__(self):
        return f'<CriterioPersonalizado {self.nombre} ({self.peso}%)>'
    
    def to_dict(self):
        """Convertir criterio a diccionario."""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'peso': self.peso,
            'icono': self.icono,
            'orden': self.orden,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }


class Ensayo(db.Model):
    """Modelo para almacenar ensayos evaluados con índices optimizados."""
    
    __tablename__ = 'ensayos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(255), nullable=False, index=True)  # Índice para búsqueda rápida
    autor = db.Column(db.String(255), nullable=True, index=True)  # Extraído del nombre
    texto_completo = db.Column(db.Text, nullable=False)
    fecha_evaluacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Índice para ordenar
    
    # Hash del texto para detección de duplicados rápida
    texto_hash = db.Column(db.String(64), unique=True, index=True)
    
    # Evaluación almacenada como JSON
    puntuacion_total = db.Column(db.Float, nullable=False, index=True)  # Índice para ranking
    calidad_tecnica = db.Column(JSON, nullable=False)
    creatividad = db.Column(JSON, nullable=False)
    vinculacion_tematica = db.Column(JSON, nullable=False)
    bienestar_colectivo = db.Column(JSON, nullable=False)
    uso_responsable_ia = db.Column(JSON, nullable=False)
    potencial_impacto = db.Column(JSON, nullable=False)
    comentario_general = db.Column(db.Text, nullable=False)
    
    # Información del anexo de IA
    tiene_anexo = db.Column(db.Boolean, default=False, index=True)  # Índice para filtrar
    ruta_anexo = db.Column(db.String(500), nullable=True)
    texto_anexo = db.Column(db.Text, nullable=True)  # Guardar texto del anexo para acceso rápido
    
    # Metadatos adicionales
    longitud_texto = db.Column(db.Integer, nullable=True)  # Para estadísticas rápidas
    num_palabras = db.Column(db.Integer, nullable=True)
    activo = db.Column(db.Boolean, default=True, index=True)  # Para soft delete
    
    # Relaciones con otras tablas
    puntajes_criterios = relationship('PuntajeCriterio', back_populates='ensayo', cascade='all, delete-orphan')
    comparaciones_1 = relationship('Comparacion', foreign_keys='Comparacion.ensayo_1_id', back_populates='ensayo_1', cascade='all, delete-orphan')
    comparaciones_2 = relationship('Comparacion', foreign_keys='Comparacion.ensayo_2_id', back_populates='ensayo_2', cascade='all, delete-orphan')
    
    # Índices compuestos para búsquedas comunes
    __table_args__ = (
        Index('idx_puntuacion_fecha', 'puntuacion_total', 'fecha_evaluacion'),
        Index('idx_autor_puntuacion', 'autor', 'puntuacion_total'),
        Index('idx_anexo_puntuacion', 'tiene_anexo', 'puntuacion_total'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Calcular hash del texto
        if self.texto_completo:
            self.texto_hash = hashlib.sha256(self.texto_completo.encode('utf-8')).hexdigest()
            self.longitud_texto = len(self.texto_completo)
            self.num_palabras = len(self.texto_completo.split())
        # Extraer autor del nombre de archivo
        if self.nombre_archivo and not self.autor:
            self.autor = self._extraer_autor(self.nombre_archivo)
    
    @staticmethod
    def _extraer_autor(nombre_archivo: str) -> str:
        """Extrae el autor del nombre de archivo."""
        # Formato esperado: "Ensayo_Autor_Titulo.pdf"
        partes = nombre_archivo.replace('.pdf', '').split('_')
        if len(partes) >= 2 and partes[0] in ['Ensayo', 'AnexoIA']:
            return partes[1]
        return 'Desconocido'
    
    def to_dict(self):
        """Convierte el ensayo a un diccionario con estructura de evaluación."""
        return {
            'id': self.id,
            'nombre_archivo': self.nombre_archivo,
            'fecha_evaluacion': self.fecha_evaluacion.isoformat(),
            'puntuacion_total': self.puntuacion_total,
            'tiene_anexo': self.tiene_anexo,
            'evaluacion': {
                'puntuacion_total': self.puntuacion_total,
                'calidad_tecnica': self.calidad_tecnica,
                'creatividad': self.creatividad,
                'vinculacion_tematica': self.vinculacion_tematica,
                'bienestar_colectivo': self.bienestar_colectivo,
                'uso_responsable_ia': self.uso_responsable_ia,
                'potencial_impacto': self.potencial_impacto,
                'comentario_general': self.comentario_general
            }
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
            'texto_preview': self.texto_completo[:200] + '...' if len(self.texto_completo) > 200 else self.texto_completo,
            'tiene_anexo': self.tiene_anexo,
            'evaluacion': {
                'puntuacion_total': self.puntuacion_total
            }
        }


class PuntajeCriterio(db.Model):
    """Tabla normalizada para puntajes de criterios individuales.
    Permite búsquedas y análisis rápidos por criterio específico."""
    
    __tablename__ = 'puntajes_criterios'
    
    id = db.Column(db.Integer, primary_key=True)
    ensayo_id = db.Column(db.Integer, ForeignKey('ensayos.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Tipo de criterio
    criterio = db.Column(db.String(50), nullable=False, index=True)
    # Opciones: 'calidad_tecnica', 'creatividad', 'vinculacion_tematica', 
    #           'bienestar_colectivo', 'uso_responsable_ia', 'potencial_impacto'
    
    # Puntaje del criterio
    calificacion = db.Column(db.Float, nullable=False, index=True)
    comentario = db.Column(db.Text, nullable=True)
    
    # Peso del criterio en la calificación total
    peso = db.Column(db.Float, nullable=False)
    
    # Timestamp
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación
    ensayo = relationship('Ensayo', back_populates='puntajes_criterios')
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_criterio_calificacion', 'criterio', 'calificacion'),
        Index('idx_ensayo_criterio', 'ensayo_id', 'criterio'),
        UniqueConstraint('ensayo_id', 'criterio', name='uq_ensayo_criterio'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'ensayo_id': self.ensayo_id,
            'criterio': self.criterio,
            'calificacion': self.calificacion,
            'comentario': self.comentario,
            'peso': self.peso,
            'fecha_creacion': self.fecha_creacion.isoformat()
        }


class Comparacion(db.Model):
    """Cache de comparaciones entre ensayos.
    Almacena resultados de comparaciones frecuentes para carga rápida."""
    
    __tablename__ = 'comparaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Ensayos comparados (siempre ordenar IDs: menor primero)
    ensayo_1_id = db.Column(db.Integer, ForeignKey('ensayos.id', ondelete='CASCADE'), nullable=False, index=True)
    ensayo_2_id = db.Column(db.Integer, ForeignKey('ensayos.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Hash único de la comparación para evitar duplicados
    comparacion_hash = db.Column(db.String(64), unique=True, index=True)
    
    # Resultado de la comparación (generado por LLM)
    resultado_comparacion = db.Column(db.Text, nullable=False)
    
    # Diferencias de puntajes
    diferencia_total = db.Column(db.Float, nullable=True)
    diferencia_calidad_tecnica = db.Column(db.Float, nullable=True)
    diferencia_creatividad = db.Column(db.Float, nullable=True)
    diferencia_vinculacion = db.Column(db.Float, nullable=True)
    diferencia_bienestar = db.Column(db.Float, nullable=True)
    diferencia_uso_ia = db.Column(db.Float, nullable=True)
    diferencia_impacto = db.Column(db.Float, nullable=True)
    
    # Metadatos
    fecha_comparacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    veces_accedida = db.Column(db.Integer, default=0)  # Contador de popularidad
    ultima_accedida = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    ensayo_1 = relationship('Ensayo', foreign_keys=[ensayo_1_id], back_populates='comparaciones_1')
    ensayo_2 = relationship('Ensayo', foreign_keys=[ensayo_2_id], back_populates='comparaciones_2')
    
    # Índices compuestos
    __table_args__ = (
        Index('idx_ensayos_comparados', 'ensayo_1_id', 'ensayo_2_id'),
        Index('idx_fecha_accesos', 'fecha_comparacion', 'veces_accedida'),
        UniqueConstraint('ensayo_1_id', 'ensayo_2_id', name='uq_comparacion'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Asegurar que ensayo_1_id < ensayo_2_id
        if self.ensayo_1_id and self.ensayo_2_id:
            if self.ensayo_1_id > self.ensayo_2_id:
                self.ensayo_1_id, self.ensayo_2_id = self.ensayo_2_id, self.ensayo_1_id
            # Generar hash único
            self.comparacion_hash = self._generar_hash()
    
    def _generar_hash(self) -> str:
        """Genera un hash único para la comparación."""
        data = f"{self.ensayo_1_id}_{self.ensayo_2_id}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def registrar_acceso(self):
        """Incrementa el contador de accesos."""
        self.veces_accedida += 1
        self.ultima_accedida = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'ensayo_1_id': self.ensayo_1_id,
            'ensayo_2_id': self.ensayo_2_id,
            'resultado_comparacion': self.resultado_comparacion,
            'diferencias': {
                'total': self.diferencia_total,
                'calidad_tecnica': self.diferencia_calidad_tecnica,
                'creatividad': self.diferencia_creatividad,
                'vinculacion': self.diferencia_vinculacion,
                'bienestar': self.diferencia_bienestar,
                'uso_ia': self.diferencia_uso_ia,
                'impacto': self.diferencia_impacto
            },
            'fecha_comparacion': self.fecha_comparacion.isoformat(),
            'veces_accedida': self.veces_accedida
        }


class ComparacionMultiple(db.Model):
    """Cache para comparaciones de más de 2 ensayos.
    Útil para competencias o rankings de múltiples ensayos."""
    
    __tablename__ = 'comparaciones_multiples'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Hash único basado en los IDs de todos los ensayos
    comparacion_hash = db.Column(db.String(64), unique=True, index=True)
    
    # IDs de ensayos como JSON array ordenado
    ensayos_ids = db.Column(JSON, nullable=False)
    
    # Resultado completo de la comparación
    resultado_comparacion = db.Column(db.Text, nullable=False)
    
    # Ranking generado (JSON con orden y justificaciones)
    ranking = db.Column(JSON, nullable=True)
    
    # Metadatos
    num_ensayos = db.Column(db.Integer, nullable=False, index=True)
    fecha_comparacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    veces_accedida = db.Column(db.Integer, default=0)
    ultima_accedida = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Índice para búsquedas por número de ensayos
    __table_args__ = (
        Index('idx_num_ensayos_fecha', 'num_ensayos', 'fecha_comparacion'),
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.ensayos_ids:
            # Ordenar IDs para consistencia
            self.ensayos_ids = sorted(self.ensayos_ids)
            self.num_ensayos = len(self.ensayos_ids)
            self.comparacion_hash = self._generar_hash()
    
    def _generar_hash(self) -> str:
        """Genera un hash único basado en todos los IDs."""
        data = '_'.join(map(str, self.ensayos_ids))
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def registrar_acceso(self):
        """Incrementa el contador de accesos."""
        self.veces_accedida += 1
        self.ultima_accedida = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'ensayos_ids': self.ensayos_ids,
            'num_ensayos': self.num_ensayos,
            'resultado_comparacion': self.resultado_comparacion,
            'ranking': self.ranking,
            'fecha_comparacion': self.fecha_comparacion.isoformat(),
            'veces_accedida': self.veces_accedida
        }


class EstadisticaGlobal(db.Model):
    """Tabla para estadísticas globales precalculadas.
    Evita consultas pesadas recurrentes."""
    
    __tablename__ = 'estadisticas_globales'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Tipo de estadística
    tipo = db.Column(db.String(50), nullable=False, unique=True, index=True)
    # Opciones: 'promedio_general', 'mediana_general', 'top_10', 'distribucion_puntajes', etc.
    
    # Valor de la estadística (JSON para flexibilidad)
    valor = db.Column(JSON, nullable=False)
    
    # Timestamp de última actualización
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Flag para indicar si está desactualizada
    desactualizada = db.Column(db.Boolean, default=False, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'valor': self.valor,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat(),
            'desactualizada': self.desactualizada
        }


# ==================== FUNCIONES HELPER ====================

def get_ensayos_ranking(limit: int = 50, offset: int = 0, tiene_anexo: bool = None) -> list:
    """Obtiene ensayos ordenados por puntuación con paginación rápida.
    
    Args:
        limit: Número máximo de resultados
        offset: Desplazamiento para paginación
        tiene_anexo: Filtrar por presencia de anexo (None = todos)
    
    Returns:
        Lista de ensayos en formato diccionario
    """
    query = Ensayo.query.filter_by(activo=True)
    
    if tiene_anexo is not None:
        query = query.filter_by(tiene_anexo=tiene_anexo)
    
    ensayos = query.order_by(Ensayo.puntuacion_total.desc()).limit(limit).offset(offset).all()
    return [ensayo.to_summary() for ensayo in ensayos]


def get_or_create_comparacion(ensayo_1_id: int, ensayo_2_id: int) -> Comparacion:
    """Obtiene una comparación existente o retorna None para crear nueva.
    
    Args:
        ensayo_1_id: ID del primer ensayo
        ensayo_2_id: ID del segundo ensayo
    
    Returns:
        Objeto Comparacion si existe, None si hay que crear nueva
    """
    # Normalizar orden de IDs
    id_menor, id_mayor = min(ensayo_1_id, ensayo_2_id), max(ensayo_1_id, ensayo_2_id)
    
    # Buscar comparación existente
    comparacion = Comparacion.query.filter_by(
        ensayo_1_id=id_menor,
        ensayo_2_id=id_mayor
    ).first()
    
    if comparacion:
        comparacion.registrar_acceso()
    
    return comparacion


def get_or_create_comparacion_multiple(ensayos_ids: list) -> ComparacionMultiple:
    """Obtiene una comparación múltiple existente o retorna None para crear nueva.
    
    Args:
        ensayos_ids: Lista de IDs de ensayos a comparar
    
    Returns:
        Objeto ComparacionMultiple si existe, None si hay que crear nueva
    """
    # Normalizar orden de IDs
    ensayos_ids_ordenados = sorted(ensayos_ids)
    
    # Generar hash para búsqueda
    data = '_'.join(map(str, ensayos_ids_ordenados))
    hash_busqueda = hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    # Buscar comparación existente
    comparacion = ComparacionMultiple.query.filter_by(comparacion_hash=hash_busqueda).first()
    
    if comparacion:
        comparacion.registrar_acceso()
    
    return comparacion


def guardar_comparacion(ensayo_1_id: int, ensayo_2_id: int, resultado: str, diferencias: dict = None):
    """Guarda una nueva comparación en la base de datos.
    
    Args:
        ensayo_1_id: ID del primer ensayo
        ensayo_2_id: ID del segundo ensayo
        resultado: Texto del resultado de la comparación
        diferencias: Dict con diferencias de puntajes por criterio
    """
    comparacion = Comparacion(
        ensayo_1_id=ensayo_1_id,
        ensayo_2_id=ensayo_2_id,
        resultado_comparacion=resultado
    )
    
    if diferencias:
        comparacion.diferencia_total = diferencias.get('total')
        comparacion.diferencia_calidad_tecnica = diferencias.get('calidad_tecnica')
        comparacion.diferencia_creatividad = diferencias.get('creatividad')
        comparacion.diferencia_vinculacion = diferencias.get('vinculacion')
        comparacion.diferencia_bienestar = diferencias.get('bienestar')
        comparacion.diferencia_uso_ia = diferencias.get('uso_ia')
        comparacion.diferencia_impacto = diferencias.get('impacto')
    
    db.session.add(comparacion)
    db.session.commit()
    return comparacion


def guardar_comparacion_multiple(ensayos_ids: list, resultado: str, ranking: dict = None):
    """Guarda una nueva comparación múltiple en la base de datos.
    
    Args:
        ensayos_ids: Lista de IDs de ensayos comparados
        resultado: Texto del resultado de la comparación
        ranking: Dict con el ranking generado
    """
    comparacion = ComparacionMultiple(
        ensayos_ids=ensayos_ids,
        resultado_comparacion=resultado,
        ranking=ranking
    )
    
    db.session.add(comparacion)
    db.session.commit()
    return comparacion


def invalidar_comparaciones(ensayo_id: int):
    """Invalida todas las comparaciones que involucran un ensayo.
    
    Se debe llamar cuando un ensayo es re-evaluado para regenerar comparaciones.
    
    Args:
        ensayo_id: ID del ensayo modificado
    """
    # Borrar comparaciones binarias
    Comparacion.query.filter(
        (Comparacion.ensayo_1_id == ensayo_id) | (Comparacion.ensayo_2_id == ensayo_id)
    ).delete()
    
    # Borrar comparaciones múltiples que incluyan este ensayo
    comparaciones_multiples = ComparacionMultiple.query.all()
    for comp in comparaciones_multiples:
        if ensayo_id in comp.ensayos_ids:
            db.session.delete(comp)
    
    db.session.commit()


def actualizar_estadistica(tipo: str, valor: dict):
    """Actualiza o crea una estadística global.
    
    Args:
        tipo: Tipo de estadística (e.g., 'promedio_general', 'top_10')
        valor: Valor de la estadística (JSON serializable)
    """
    estadistica = EstadisticaGlobal.query.filter_by(tipo=tipo).first()
    
    if estadistica:
        estadistica.valor = valor
        estadistica.fecha_actualizacion = datetime.utcnow()
        estadistica.desactualizada = False
    else:
        estadistica = EstadisticaGlobal(tipo=tipo, valor=valor)
        db.session.add(estadistica)
    
    db.session.commit()
    return estadistica


def marcar_estadisticas_desactualizadas():
    """Marca todas las estadísticas como desactualizadas.
    
    Se debe llamar cuando se agrega/modifica/elimina un ensayo.
    """
    EstadisticaGlobal.query.update({EstadisticaGlobal.desactualizada: True})
    db.session.commit()


def get_estadisticas_rapidas() -> dict:
    """Obtiene estadísticas globales precalculadas o las genera si no existen.
    
    Returns:
        Dict con estadísticas: promedio, mediana, top_10, distribución, etc.
    """
    stats = {}
    
    # Promedio general
    promedio_stat = EstadisticaGlobal.query.filter_by(tipo='promedio_general', desactualizada=False).first()
    if promedio_stat:
        stats['promedio_general'] = promedio_stat.valor
    else:
        # Calcular y guardar
        promedio = db.session.query(db.func.avg(Ensayo.puntuacion_total)).filter_by(activo=True).scalar()
        actualizar_estadistica('promedio_general', {'valor': float(promedio) if promedio else 0.0})
        stats['promedio_general'] = {'valor': float(promedio) if promedio else 0.0}
    
    # Total de ensayos
    total_stat = EstadisticaGlobal.query.filter_by(tipo='total_ensayos', desactualizada=False).first()
    if total_stat:
        stats['total_ensayos'] = total_stat.valor
    else:
        total = Ensayo.query.filter_by(activo=True).count()
        actualizar_estadistica('total_ensayos', {'valor': total})
        stats['total_ensayos'] = {'valor': total}
    
    # Ensayos con anexo
    anexo_stat = EstadisticaGlobal.query.filter_by(tipo='con_anexo', desactualizada=False).first()
    if anexo_stat:
        stats['con_anexo'] = anexo_stat.valor
    else:
        con_anexo = Ensayo.query.filter_by(activo=True, tiene_anexo=True).count()
        actualizar_estadistica('con_anexo', {'valor': con_anexo})
        stats['con_anexo'] = {'valor': con_anexo}
    
    return stats


def guardar_puntajes_criterios(ensayo_id: int, criterios: dict, pesos: dict):
    """Guarda los puntajes de criterios individuales para un ensayo.
    
    Args:
        ensayo_id: ID del ensayo evaluado
        criterios: Dict con {nombre_criterio: {calificacion, comentario}}
        pesos: Dict con {nombre_criterio: peso}
    """
    # Borrar puntajes anteriores si existen
    PuntajeCriterio.query.filter_by(ensayo_id=ensayo_id).delete()
    
    # Crear nuevos puntajes
    for nombre_criterio, datos in criterios.items():
        puntaje = PuntajeCriterio(
            ensayo_id=ensayo_id,
            criterio=nombre_criterio,
            calificacion=datos['calificacion'],
            comentario=datos.get('comentario', ''),
            peso=pesos.get(nombre_criterio, 1.0)
        )
        db.session.add(puntaje)
    
    db.session.commit()


def get_puntajes_por_criterio(ensayo_id: int) -> dict:
    """Obtiene todos los puntajes de criterios para un ensayo.
    
    Args:
        ensayo_id: ID del ensayo
    
    Returns:
        Dict con {nombre_criterio: {calificacion, comentario, peso}}
    """
    puntajes = PuntajeCriterio.query.filter_by(ensayo_id=ensayo_id).all()
    return {p.criterio: p.to_dict() for p in puntajes}


def init_db(app):
    """Inicializa la base de datos."""
    # Configurar la base de datos SQLite en el directorio raíz del proyecto
    # Esto asegura que siempre use la misma base de datos sin importar desde dónde se ejecute
    project_root = Path(__file__).parent
    db_path = project_root / 'essays.db'
    
    # Usar ruta absoluta para evitar problemas de ruta relativa
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path.absolute()}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print(f"✅ Base de datos inicializada en: {db_path.absolute()}")
        
        # Verificar cuántos ensayos hay en la base de datos
        try:
            ensayo_count = db.session.query(Ensayo).count()
            usuario_count = db.session.query(Usuario).count()
            print(f"📊 Base de datos contiene: {ensayo_count} ensayos, {usuario_count} usuarios")
        except Exception as e:
            print(f"⚠️  Error al contar registros: {e}")
