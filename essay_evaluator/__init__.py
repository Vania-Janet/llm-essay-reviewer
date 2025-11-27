"""
Essay Evaluator - AI-Powered Academic Essay Assessment System

A comprehensive system for automated evaluation of academic essays using
GPT-4, LangGraph, and LangChain.
"""

__version__ = "1.0.0"
__author__ = "Vania Janet"
__email__ = "vania@example.com"

from essay_evaluator.core.agent.evaluator import EvaluadorEnsayos
from essay_evaluator.core.models.evaluation import EvaluacionEnsayo, EvaluacionCriterio

__all__ = [
    "EvaluadorEnsayos",
    "EvaluacionEnsayo", 
    "EvaluacionCriterio",
]
