"""
Core Package - Lógica de negocio principal.

Contiene:
- evaluator: Motor de evaluación de ensayos con IA
- models: Modelos Pydantic para estructuras de datos
- prompts: Plantillas de prompts para la IA
"""

from .evaluator import EvaluadorEnsayos
from .models import EvaluacionEnsayo, EvaluacionCriterio

__all__ = ['EvaluadorEnsayos', 'EvaluacionEnsayo', 'EvaluacionCriterio']
