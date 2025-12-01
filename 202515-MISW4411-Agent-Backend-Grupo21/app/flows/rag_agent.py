"""
Workflow del Agente RAG
========================

Este módulo define el flujo de ejecución del Agente RAG utilizando LangGraph.
El agente implementa un flujo LINEAL que consulta el sistema RAG y genera una
respuesta basada en el contexto recuperado.

IMPLEMENTACIÓN SEMANA 6:
- Construir el workflow del agente RAG con LangGraph
- Definir el estado del agente (AgentState)
- Crear nodo "ask" que invoca la herramienta MCP del RAG
- Crear nodo "llm" que genera respuesta con el contexto
- Conectar los nodos en flujo lineal: ask → llm

CARACTERÍSTICAS:
- Flujo determinístico (sin ramificaciones)
- No usa bind_tools (herramienta específica recibida como parámetro)
- Siempre ejecuta la misma secuencia de pasos
"""

from typing import Annotated, Sequence, TypedDict

import logging
import sys
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END


# Configurar logging con UTF-8
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
# Asegurar que el handler use UTF-8
for handler in logging.root.handlers:
    if hasattr(handler, 'stream') and hasattr(handler.stream, 'reconfigure'):
        try:
            handler.stream.reconfigure(encoding='utf-8')
        except:
            pass

logger = logging.getLogger(__name__)


# ===============================================================================
# SEMANA 6: Definir el estado del agente
# ===============================================================================
class AgentState(TypedDict):
    """
    Estado del agente RAG que se pasa entre nodos del grafo.
    
    Atributos:
        messages: Lista de mensajes en la conversación (input del usuario, respuesta del RAG, respuesta final)
        question: La pregunta original del usuario
        rag_response: La respuesta obtenida del sistema RAG
        final_answer: La respuesta final formateada por el LLM
    """
    messages: Annotated[Sequence[BaseMessage], "Lista de mensajes en la conversación"]
    question: str
    rag_response: str
    final_answer: str


# ===============================================================================
# SEMANA 6: Construir el flujo del agente RAG
# ===============================================================================
def build_rag_agent(model, ask_tool):
    """
    Construye un agente RAG con flujo lineal.
    
    El flujo es: ask (consulta RAG) → llm (formatea respuesta) → END
    
    Args:
        model: El modelo LLM (Gemini) configurado
        ask_tool: Herramienta MCP para consultar el RAG
    
    Returns:
        CompiledGraph: El grafo compilado listo para ejecutar
    """
    
    # Crear el grafo de estado
    graph = StateGraph(AgentState)
    
    # ===========================================================================
    # Nodo 1: "ask" - Consulta el sistema RAG usando la herramienta MCP
    # ===========================================================================
    async def ask_node(state: AgentState) -> AgentState:
        """
        Nodo que invoca la herramienta MCP para consultar el sistema RAG.
        
        Args:
            state: Estado actual del agente
        
        Returns:
            Estado actualizado con la respuesta del RAG
        """
        question = state["question"]
        logger.info(f"[RAG AGENT] Consultando RAG con pregunta: {question[:100]}...")
        
        try:
            # Invocar la herramienta MCP para consultar el RAG
            # La herramienta ask_tool es un objeto LangChain que puede ser invocado
            # El parámetro debe coincidir con el nombre del argumento en la definición MCP: "query"
            tool_result = await ask_tool.ainvoke({"query": question})
            
            # Extraer la respuesta (puede ser string o dict dependiendo de la herramienta)
            if isinstance(tool_result, str):
                rag_response = tool_result
            elif isinstance(tool_result, dict):
                # Si es un dict, intentar extraer el contenido
                rag_response = tool_result.get("content", tool_result.get("result", str(tool_result)))
            else:
                rag_response = str(tool_result)
            
            logger.info(f"[RAG AGENT] Respuesta RAG recibida ({len(rag_response)} caracteres)")
            
            # Actualizar el estado con la respuesta del RAG
            return {
                **state,
                "rag_response": rag_response,
                "messages": list(state["messages"]) + [
                    AIMessage(content=f"Respuesta del RAG: {rag_response}")
                ]
            }
        except Exception as e:
            error_msg = f"Error al consultar el sistema RAG: {str(e)}"
            logger.error(f"[RAG AGENT] {error_msg}")
            return {
                **state,
                "rag_response": error_msg,
                "messages": list(state["messages"]) + [
                    AIMessage(content=f"Error: {error_msg}")
                ]
            }
    
    # ===========================================================================
    # Nodo 2: "llm" - Genera respuesta formateada usando el LLM
    # ===========================================================================
    async def llm_node(state: AgentState) -> AgentState:
        """
        Nodo que usa el LLM para formatear la respuesta del RAG.
        
        El LLM recibe la pregunta original y la respuesta del RAG, y genera
        una respuesta formateada (resumen, tabla, viñetas, etc.).
        
        Args:
            state: Estado actual del agente
        
        Returns:
            Estado actualizado con la respuesta final formateada
        """
        question = state["question"]
        rag_response = state["rag_response"]
        
        logger.info("[RAG AGENT] Generando respuesta formateada con LLM...")
        
        # Construir el prompt para el LLM
        prompt = f"""Eres un asistente experto en formatear respuestas de manera clara y estructurada.

El usuario hizo la siguiente pregunta:
{question}

El sistema RAG recuperó la siguiente información:
{rag_response}

Por favor, formatea esta información en una respuesta clara y bien estructurada. Puedes:
- Crear un resumen conciso
- Organizar la información en viñetas si hay múltiples puntos
- Crear una tabla si la información es tabular
- Destacar los puntos más relevantes

Responde de manera profesional y clara:"""
        
        try:
            # Invocar el modelo LLM
            response = await model.ainvoke([HumanMessage(content=prompt)])
            
            # Extraer el contenido de la respuesta
            final_answer = response.content if hasattr(response, 'content') else str(response)
            
            logger.info(f"[RAG AGENT] Respuesta final generada ({len(final_answer)} caracteres)")
            
            # Actualizar el estado con la respuesta final
            return {
                **state,
                "final_answer": final_answer,
                "messages": list(state["messages"]) + [
                    AIMessage(content=final_answer)
                ]
            }
        except Exception as e:
            error_msg = f"Error al generar respuesta con LLM: {str(e)}"
            logger.error(f"[RAG AGENT] {error_msg}")
            # En caso de error, usar la respuesta del RAG directamente
            return {
                **state,
                "final_answer": rag_response,
                "messages": list(state["messages"]) + [
                    AIMessage(content=rag_response)
                ]
            }
    
    # ===========================================================================
    # Construir el grafo: agregar nodos y edges
    # ===========================================================================
    
    # Agregar los nodos al grafo
    graph.add_node("ask", ask_node)
    graph.add_node("llm", llm_node)
    
    # Definir el flujo lineal: ask → llm → END
    graph.set_entry_point("ask")
    graph.add_edge("ask", "llm")
    graph.add_edge("llm", END)
    
    # Compilar el grafo
    flow = graph.compile()
    
    logger.info("[RAG AGENT] Grafo compilado exitosamente")
    return flow
