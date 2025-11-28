"""
Agente evaluador de ensayos usando LangGraph y LangChain.
"""
import os
import re
from typing import Dict, Any, Annotated, TypedDict, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from app.core.models import EstadoEvaluacion, EvaluacionEnsayo, EvaluacionCriterio
from app.core.prompts import (
    PROMPT_SISTEMA,
    PROMPT_CALIDAD_TECNICA,
    PROMPT_CREATIVIDAD,
    PROMPT_VINCULACION_TEMATICA,
    PROMPT_BIENESTAR_COLECTIVO,
    PROMPT_USO_RESPONSABLE_IA,
    PROMPT_POTENCIAL_IMPACTO,
    PROMPT_COMENTARIO_GENERAL
)

# Cargar variables de entorno
load_dotenv()


def merge_dicts(left: Optional[Dict], right: Optional[Dict]) -> Dict:
    """Reducer para combinar diccionarios de múltiples nodos."""
    if left is None:
        return right or {}
    if right is None:
        return left
    return {**left, **right}


# Definir el estado del grafo con reducer para actualizaciones concurrentes
class EstadoGrafo(TypedDict):
    """Estado del grafo de evaluación con soporte para actualizaciones concurrentes."""
    ensayo: str
    anexo_ia: str
    paso_actual: str
    evaluacion: Optional[EvaluacionEnsayo]
    # Usar Annotated con un reducer personalizado para combinar actualizaciones
    calidad_tecnica: Annotated[Optional[Dict[str, Any]], merge_dicts]
    creatividad: Annotated[Optional[Dict[str, Any]], merge_dicts]
    vinculacion_tematica: Annotated[Optional[Dict[str, Any]], merge_dicts]
    bienestar_colectivo: Annotated[Optional[Dict[str, Any]], merge_dicts]
    uso_responsable_ia: Annotated[Optional[Dict[str, Any]], merge_dicts]
    potencial_impacto: Annotated[Optional[Dict[str, Any]], merge_dicts]


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
        print(" Evaluando: Calidad técnica y rigor académico...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_CALIDAD_TECNICA)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        return {
            "calidad_tecnica": {
                "calificacion": evaluacion.calificacion,
                "comentario": evaluacion.comentario
            }
        }
    
    def _evaluar_creatividad(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalua creatividad y originalidad."""
        print("Evaluando: Creatividad y originalidad...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_CREATIVIDAD)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        return {
            "creatividad": {
                "calificacion": evaluacion.calificacion,
                "comentario": evaluacion.comentario
            }
        }
    
    def _evaluar_vinculacion(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa vinculación con ejes temáticos."""
        print("Evaluando: Vinculacion con ejes tematicos...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_VINCULACION_TEMATICA)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        return {
            "vinculacion_tematica": {
                "calificacion": evaluacion.calificacion,
                "comentario": evaluacion.comentario
            }
        }
    
    def _evaluar_bienestar(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa reflexión sobre bienestar colectivo."""
        print("Evaluando: Bienestar colectivo y responsabilidad social...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_BIENESTAR_COLECTIVO)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        return {
            "bienestar_colectivo": {
                "calificacion": evaluacion.calificacion,
                "comentario": evaluacion.comentario
            }
        }
    
    def _evaluar_uso_ia(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa uso responsable y reflexivo de herramientas de IA."""
        print("Evaluando: Uso responsable y reflexivo de herramientas de IA...")
        
        # Obtener el anexo de IA si está disponible
        anexo_ia = state.get("anexo_ia", "[NO SE PROPORCIONÓ ANEXO DE IA]")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_USO_RESPONSABLE_IA)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({
            "ensayo": state["ensayo"],
            "anexo_ia": anexo_ia
        })
        
        return {
            "uso_responsable_ia": {
                "calificacion": evaluacion.calificacion,
                "comentario": evaluacion.comentario
            }
        }
    
    def _evaluar_impacto(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Evalúa potencial de impacto."""
        print("Evaluando: Potencial de impacto y publicacion...")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", PROMPT_SISTEMA),
            ("user", PROMPT_POTENCIAL_IMPACTO)
        ])
        
        chain = prompt | self.llm_structured
        evaluacion = chain.invoke({"ensayo": state["ensayo"]})
        
        return {
            "potencial_impacto": {
                "calificacion": evaluacion.calificacion,
                "comentario": evaluacion.comentario
            }
        }
    
    def _generar_comentario_general(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Nodo: Genera comentario general y ensambla evaluacion final."""
        print("Generando comentario general...")
        
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

            5. USO RESPONSABLE DE IA: {state['uso_responsable_ia']['calificacion']}/5
            {state['uso_responsable_ia']['comentario']}

            6. POTENCIAL DE IMPACTO: {state['potencial_impacto']['calificacion']}/5
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
            uso_responsable_ia=EvaluacionCriterio(**state["uso_responsable_ia"]),
            potencial_impacto=EvaluacionCriterio(**state["potencial_impacto"]),
            comentario_general=comentario_general
        )
        
        # Calcular puntuación total
        evaluacion.calcular_puntuacion_total()
        
        return {
            "evaluacion": evaluacion,
            "paso_actual": "finalizado"
        }
    
    def _construir_grafo(self) -> StateGraph:
        """Construye el grafo de evaluacion con LangGraph.
        
        OPTIMIZACION: Los criterios se evaluan en paralelo para reducir
        el tiempo de respuesta de ~35s a ~10-15s por ensayo.
        """
        # Crear el grafo con el estado tipado
        workflow = StateGraph(EstadoGrafo)
        
        # Agregar nodos
        workflow.add_node("inicio", lambda x: x)  # Nodo dummy para paralelizacion
        workflow.add_node("calidad_tecnica", self._evaluar_calidad_tecnica)
        workflow.add_node("creatividad", self._evaluar_creatividad)
        workflow.add_node("vinculacion", self._evaluar_vinculacion)
        workflow.add_node("bienestar", self._evaluar_bienestar)
        workflow.add_node("uso_ia", self._evaluar_uso_ia)
        workflow.add_node("impacto", self._evaluar_impacto)
        workflow.add_node("comentario_general", self._generar_comentario_general)
        
        # PARALELIZACION: Todos los criterios se evaluan simultaneamente
        workflow.set_entry_point("inicio")
        
        # Desde inicio, lanzar todas las evaluaciones en paralelo
        workflow.add_edge("inicio", "calidad_tecnica")
        workflow.add_edge("inicio", "creatividad")
        workflow.add_edge("inicio", "vinculacion")
        workflow.add_edge("inicio", "bienestar")
        workflow.add_edge("inicio", "uso_ia")
        workflow.add_edge("inicio", "impacto")
        
        # Todos los criterios convergen al comentario general
        workflow.add_edge("calidad_tecnica", "comentario_general")
        workflow.add_edge("creatividad", "comentario_general")
        workflow.add_edge("vinculacion", "comentario_general")
        workflow.add_edge("bienestar", "comentario_general")
        workflow.add_edge("uso_ia", "comentario_general")
        workflow.add_edge("impacto", "comentario_general")
        
        workflow.add_edge("comentario_general", END)
        
        # Compilar el grafo
        return workflow.compile()
    
    def evaluar(self, ensayo: str, anexo_ia: str = None) -> EvaluacionEnsayo:
        """
        Evalúa un ensayo completo.
        
        Args:
            ensayo: Texto del ensayo a evaluar
            anexo_ia: Texto del anexo de IA (opcional)
            
        Returns:
            Objeto EvaluacionEnsayo con todos los criterios evaluados
        """
        print("\n" + "="*60)
        print("INICIANDO EVALUACION DE ENSAYO")
        if anexo_ia:
            print("Anexo de IA detectado y sera incluido en la evaluacion")
        print("="*60 + "\n")
        
        # Estado inicial con todos los campos requeridos
        estado_inicial = {
            "ensayo": ensayo,
            "anexo_ia": anexo_ia if anexo_ia else "[NO SE PROPORCIONÓ ANEXO DE IA]",
            "paso_actual": "inicio",
            "evaluacion": None,
            "calidad_tecnica": None,
            "creatividad": None,
            "vinculacion_tematica": None,
            "bienestar_colectivo": None,
            "uso_responsable_ia": None,
            "potencial_impacto": None
        }
        
        # Ejecutar el grafo
        resultado = self.graph.invoke(estado_inicial)
        
        print("\n" + "="*60)
        print("EVALUACIÓN COMPLETADA")
        print("="*60 + "\n")
        
        return resultado["evaluacion"]
