"""
Modelos de datos para el sistema de evaluación de ensayos.
"""
from typing import Optional
from pydantic import BaseModel, Field


class EvaluacionCriterio(BaseModel):
    """Evaluación de un criterio individual."""
    calificacion: int = Field(..., ge=1, le=5, description="Calificación del 1 al 5")
    comentario: str = Field(..., description="Comentario justificando la calificación")


class EvaluacionEnsayo(BaseModel):
    """Evaluación completa de un ensayo."""
    
    # Criterio 1: Calidad técnica y rigor académico (20%)
    calidad_tecnica: EvaluacionCriterio = Field(
        ..., 
        description="Evalúa la estructura, coherencia y solidez argumentativa del ensayo"
    )
    
    # Criterio 2: Creatividad y originalidad (20%)
    creatividad: EvaluacionCriterio = Field(
        ..., 
        description="Evalúa la capacidad del autor para aportar ideas nuevas e innovadoras"
    )
    
    # Criterio 3: Vinculación con los ejes temáticos (15%)
    vinculacion_tematica: EvaluacionCriterio = Field(
        ..., 
        description="Evalúa qué tan directamente aborda los temas de la convocatoria"
    )
    
    # Criterio 4: Reflexión sobre bienestar colectivo (20%)
    bienestar_colectivo: EvaluacionCriterio = Field(
        ..., 
        description="Analiza la sensibilidad frente a impactos sociales, éticos y ambientales"
    )
    
    # Criterio 5: Uso responsable de IA (15%)
    uso_ia: EvaluacionCriterio = Field(
        ..., 
        description="Evalúa la transparencia y ética en el uso de IA"
    )
    no_utilizo_ia: bool = Field(
        False, 
        description="Indica si el autor no utilizó IA"
    )
    
    # Criterio 6: Potencial de impacto (10%)
    potencial_impacto: EvaluacionCriterio = Field(
        ..., 
        description="Evalúa la capacidad para comunicar, inspirar y generar interés"
    )
    
    # Puntuación total
    puntuacion_total: Optional[float] = Field(
        None, 
        description="Puntuación total ponderada (calculada automáticamente)"
    )
    
    # Comentario general
    comentario_general: str = Field(
        ..., 
        description="Síntesis general sobre el ensayo con fortalezas y sugerencias"
    )
    
    justificacion_breve: Optional[str] = Field(
        None, 
        description="Justificación breve opcional adicional"
    )
    
    def calcular_puntuacion_total(self) -> float:
        """Calcula la puntuación total ponderada."""
        ponderaciones = {
            'calidad_tecnica': 0.20,
            'creatividad': 0.20,
            'vinculacion_tematica': 0.15,
            'bienestar_colectivo': 0.20,
            'uso_ia': 0.15,
            'potencial_impacto': 0.10
        }
        
        total = (
            self.calidad_tecnica.calificacion * ponderaciones['calidad_tecnica'] +
            self.creatividad.calificacion * ponderaciones['creatividad'] +
            self.vinculacion_tematica.calificacion * ponderaciones['vinculacion_tematica'] +
            self.bienestar_colectivo.calificacion * ponderaciones['bienestar_colectivo'] +
            self.uso_ia.calificacion * ponderaciones['uso_ia'] +
            self.potencial_impacto.calificacion * ponderaciones['potencial_impacto']
        )
        
        self.puntuacion_total = round(total, 2)
        return self.puntuacion_total


class EstadoEvaluacion(BaseModel):
    """Estado del proceso de evaluación."""
    ensayo: str = Field(..., description="Texto del ensayo a evaluar")
    evaluacion: Optional[EvaluacionEnsayo] = Field(None, description="Resultado de la evaluación")
    paso_actual: str = Field("inicio", description="Paso actual en el proceso")
