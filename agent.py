"""
Agente evaluador de ensayos usando LangGraph y LangChain.
"""
import os
import re
from typing import Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from models import EstadoEvaluacion, EvaluacionEnsayo, EvaluacionCriterio
from prompts import (
    PROMPT_SISTEMA,
    PROMPT_CALIDAD_TECNICA,
    PROMPT_CREATIVIDAD,
    PROMPT_VINCULACION_TEMATICA,
    PROMPT_BIENESTAR_COLECTIVO,
    PROMPT_POTENCIAL_IMPACTO,
    PROMPT_COMENTARIO_GENERAL
)

# Cargar variables de entorno
load_dotenv()


class EvaluadorEnsayos:
    """Agente evaluador de ensayos basado en LangGraph."""
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.3):
        """
        Inicializa el evaluador.
        
        Args:
            model_name: Nombre del modelo de OpenAI a usar
            temperature: Temperatura para la generación
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # LLM con structured output para extraer calificaciones
        self.llm_structured = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        ).with_structured_output(EvaluacionCriterio)
        
        self.graph = self._construir_grafo()
    
    def _evaluar_calidad_tecnica(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa calidad técnica y rigor académico."""
        print("📝 Evaluando: Calidad técnica y rigor académico...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_CALIDAD_TECNICA)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        state["calidad_tecnica"] = {
            "calificacion": evaluacion.calificacion,
            "comentario": evaluacion.comentario
        }
        state["paso_actual"] = "creatividad"
        return state
    
    def _evaluar_creatividad(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa creatividad y originalidad."""
        print("🎨 Evaluando: Creatividad y originalidad...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_CREATIVIDAD)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        state["creatividad"] = {
            "calificacion": evaluacion.calificacion,
            "comentario": evaluacion.comentario
        }
        state["paso_actual"] = "vinculacion"
        return state
    
    def _evaluar_vinculacion(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa vinculación con ejes temáticos."""
        print("🎯 Evaluando: Vinculación con ejes temáticos...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_VINCULACION_TEMATICA)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        state["vinculacion_tematica"] = {
            "calificacion": evaluacion.calificacion,
            "comentario": evaluacion.comentario
        }
        state["paso_actual"] = "bienestar"
        return state
    
    def _evaluar_bienestar(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa reflexión sobre bienestar colectivo."""
        print("🌍 Evaluando: Bienestar colectivo y responsabilidad social...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_BIENESTAR_COLECTIVO)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        state["bienestar_colectivo"] = {
            "calificacion": evaluacion.calificacion,
            "comentario": evaluacion.comentario
        }
        state["paso_actual"] = "impacto"
        return state
    
    def _evaluar_impacto(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa potencial de impacto."""
        print("✨ Evaluando: Potencial de impacto y publicación...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_POTENCIAL_IMPACTO)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        state["potencial_impacto"] = {
            "calificacion": evaluacion.calificacion,
            "comentario": evaluacion.comentario
        }
        state["paso_actual"] = "comentario_general"
        return state
    
    def _generar_comentario_general(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Genera comentario general y ensambla evaluación final."""
        print("📋 Generando comentario general...")
        
        # Preparar resumen de evaluaciones previas
        evaluaciones_previas = f"""
1. CALIDAD TÉCNICA Y RIGOR ACADÉMICO: {state['calidad_tecnica']['calificacion']}/5
   {state['calidad_tecnica']['comentario']}

2. CREATIVIDAD Y ORIGINALIDAD: {state['creatividad']['calificacion']}/5
   {state['creatividad']['comentario']}

3. VINCULACIÓN TEMÁTICA: {state['vinculacion_tematica']['calificacion']}/5
   {state['vinculacion_tematica']['comentario']}

4. BIENESTAR COLECTIVO: {state['bienestar_colectivo']['calificacion']}/5
   {state['bienestar_colectivo']['comentario']}

5. POTENCIAL DE IMPACTO: {state['potencial_impacto']['calificacion']}/5
   {state['potencial_impacto']['comentario']}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_COMENTARIO_GENERAL)
        ])
        
        chain = prompt | self.llm
        respuesta = chain.invoke({
            "evaluaciones_previas": evaluaciones_previas,
            "ensayo": state["ensayo"]
        })
        
        comentario_general = respuesta.content.strip()
        
        # Ensamblar evaluación completa
        evaluacion = EvaluacionEnsayo(
            calidad_tecnica=EvaluacionCriterio(**state["calidad_tecnica"]),
            creatividad=EvaluacionCriterio(**state["creatividad"]),
            vinculacion_tematica=EvaluacionCriterio(**state["vinculacion_tematica"]),
            bienestar_colectivo=EvaluacionCriterio(**state["bienestar_colectivo"]),
            potencial_impacto=EvaluacionCriterio(**state["potencial_impacto"]),
            comentario_general=comentario_general
        )
        
        # Calcular puntuación total
        evaluacion.calcular_puntuacion_total()
        
        state["evaluacion"] = evaluacion
        state["paso_actual"] = "finalizado"
        
        return state
    
    def _construir_grafo(self) -> StateGraph:
        """Construye el grafo de evaluación con LangGraph."""
        # Crear el grafo
        workflow = StateGraph(dict)
        
        # Agregar nodos
        workflow.add_node("calidad_tecnica", self._evaluar_calidad_tecnica)
        workflow.add_node("creatividad", self._evaluar_creatividad)
        workflow.add_node("vinculacion", self._evaluar_vinculacion)
        workflow.add_node("bienestar", self._evaluar_bienestar)
        workflow.add_node("impacto", self._evaluar_impacto)
        workflow.add_node("comentario_general", self._generar_comentario_general)
        
        # Definir el flujo (edges)
        workflow.set_entry_point("calidad_tecnica")
        workflow.add_edge("calidad_tecnica", "creatividad")
        workflow.add_edge("creatividad", "vinculacion")
        workflow.add_edge("vinculacion", "bienestar")
        workflow.add_edge("bienestar", "impacto")
        workflow.add_edge("impacto", "comentario_general")
        workflow.add_edge("comentario_general", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    def evaluar(self, ensayo: str) -> EvaluacionEnsayo:
        """
        Evalúa un ensayo completo.
        
        Args:
            ensayo: Texto del ensayo a evaluar
            
        Returns:
            Objeto EvaluacionEnsayo con todos los criterios evaluados
        """
        print("\n" + "="*60)
        print("🎓 INICIANDO EVALUACIÓN DE ENSAYO")
        print("="*60 + "\n")
        
        # Estado inicial
        estado_inicial = {
            "ensayo": ensayo,
            "paso_actual": "inicio"
        }
        
        # Ejecutar el grafo
        resultado = self.graph.invoke(estado_inicial)
        
        print("\n" + "="*60)
        print("EVALUACIÓN COMPLETADA")
        print("="*60 + "\n")
        
        return resultado["evaluacion"]
