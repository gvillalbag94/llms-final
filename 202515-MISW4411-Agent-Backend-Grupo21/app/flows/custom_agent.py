"""
Workflow del Agente Especializado
==========================================

Este módulo define el flujo de ejecución del Agente Especializado utilizando
LangGraph. El agente implementa el patrón ReAct (Reasoning + Acting) que permite
tomar decisiones dinámicas sobre qué herramientas usar.

IMPLEMENTACIÓN SEMANA 7:
- Construir el workflow ReAct del agente especilizado
- Definir el estado del agente (solo necesita "messages")
- Crear nodo "llm" que razona y decide qué hacer
- Crear nodo "tools" que ejecuta herramientas solicitadas
- Crear función should_continue que decide si usar más herramientas
- Construir grafo con ciclo: llm ↔ tools

CARACTERÍSTICAS:
- Patrón ReAct: Reasoning (razonamiento) + Acting (acción)
- Decisiones dinámicas sobre qué herramientas usar
- Puede ejecutar múltiples herramientas en secuencia
- El LLM analiza resultados y decide siguientes pasos
- Ciclos de retroalimentación para iterar hasta completar la tarea
- Aristas condicionales para decidir cuándo terminar
"""

from typing import Annotated, Sequence, TypedDict, Literal
import logging
import sys
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage
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
# SEMANA 7: Definir el estado del agente
# ===============================================================================
class AgentState(TypedDict):
    """
    Estado del agente personalizado que se pasa entre nodos del grafo.
    
    Atributos:
        messages: Lista de mensajes en la conversación (input del usuario, 
                  respuestas del LLM, resultados de herramientas, respuesta final)
    """
    messages: Annotated[Sequence[BaseMessage], "Lista de mensajes en la conversación"]


# ===============================================================================
# SEMANA 7: Construir el agente ReAct con herramientas
# ===============================================================================
#
# DIFERENCIAS CON EL RAG AGENT:
# - RAG Agent: Flujo LINEAL (siempre ejecuta "ask")
# - Custom Agent: Flujo CÍCLICO (decide dinámicamente qué hacer)

def build_custom_agent(model, tools_by_name):
    """
    Construye un agente ReAct que puede usar múltiples herramientas.
    
    El agente implementa un ciclo de retroalimentación donde:
    1. El LLM razona sobre la tarea y decide qué herramienta usar
    2. Se ejecuta la herramienta seleccionada
    3. El resultado vuelve al LLM para continuar razonando
    4. El ciclo se repite hasta que el LLM decide que tiene suficiente información
    
    Args:
        model: El modelo LLM con herramientas ya vinculadas (bind_tools)
        tools_by_name: Diccionario mapeando nombres a herramientas MCP
    
    Returns:
        CompiledGraph: El grafo compilado listo para ejecutar
    """
    
    # Crear el grafo de estado
    graph = StateGraph(AgentState)
    
    # ===========================================================================
    # Nodo "agent": El LLM razona y decide qué hacer
    # ===========================================================================
    async def agent_node(state: AgentState) -> AgentState:
        """
        Nodo que invoca el LLM para razonar sobre la tarea y decidir qué hacer.
        
        El LLM puede:
        - Responder directamente si tiene suficiente información
        - Solicitar el uso de herramientas si necesita más información
        
        Args:
            state: Estado actual del agente con el historial de mensajes
        
        Returns:
            Estado actualizado con la respuesta del LLM
        """
        messages = state["messages"]
        logger.info(f"[CUSTOM AGENT] Agente razonando sobre {len(messages)} mensajes...")
        
        try:
            # Invocar el modelo LLM con el historial de mensajes
            # El modelo tiene bind_tools aplicado, por lo que puede decidir usar herramientas
            response = await model.ainvoke(messages)
            
            logger.info(f"[CUSTOM AGENT] LLM respondió. Tipo: {type(response)}")
            
            # Actualizar el estado con la respuesta del LLM
            return {
                "messages": list(messages) + [response]
            }
        except Exception as e:
            error_msg = f"Error en el nodo agent: {str(e)}"
            logger.error(f"[CUSTOM AGENT] {error_msg}")
            # En caso de error, crear un mensaje de error
            error_message = AIMessage(content=f"Error al procesar la solicitud: {str(e)}")
            return {
                "messages": list(messages) + [error_message]
            }
    
    # ===========================================================================
    # Nodo "tools": Ejecuta las herramientas solicitadas por el LLM
    # ===========================================================================
    async def tools_node(state: AgentState) -> AgentState:
        """
        Nodo que ejecuta las herramientas solicitadas por el LLM.
        
        Extrae las llamadas a herramientas del último mensaje del LLM y las ejecuta.
        Los resultados se agregan al estado para que el LLM pueda usarlos en la siguiente iteración.
        
        Args:
            state: Estado actual del agente
        
        Returns:
            Estado actualizado con los resultados de las herramientas
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        logger.info(f"[CUSTOM AGENT] Ejecutando herramientas...")
        
        # Verificar si el último mensaje tiene tool calls
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            logger.warning("[CUSTOM AGENT] No se encontraron tool calls en el último mensaje")
            return state
        
        tool_messages = []
        
        # Ejecutar cada herramienta solicitada
        for tool_call in last_message.tool_calls:
            # tool_call puede ser un dict o un objeto, manejamos ambos casos
            if isinstance(tool_call, dict):
                tool_name = tool_call.get("name") or tool_call.get("function", {}).get("name")
                tool_args = tool_call.get("args") or tool_call.get("arguments") or tool_call.get("function", {}).get("arguments", {})
                tool_call_id = tool_call.get("id") or tool_call.get("function", {}).get("name", "unknown")
            else:
                # Si es un objeto, acceder a sus atributos
                tool_name = getattr(tool_call, "name", None)
                if not tool_name:
                    # Intentar acceder a function.name si existe
                    func = getattr(tool_call, "function", None)
                    if func:
                        if isinstance(func, dict):
                            tool_name = func.get("name")
                        else:
                            tool_name = getattr(func, "name", None)
                
                tool_args = getattr(tool_call, "args", None) or getattr(tool_call, "arguments", None)
                if not tool_args:
                    func = getattr(tool_call, "function", None)
                    if func:
                        if isinstance(func, dict):
                            tool_args = func.get("arguments", {})
                        else:
                            tool_args = getattr(func, "arguments", {})
                
                tool_call_id = getattr(tool_call, "id", None) or tool_name or "unknown"
                tool_args = tool_args or {}
            
            # Si tool_args es string, intentar parsearlo como JSON
            if isinstance(tool_args, str):
                try:
                    import json
                    tool_args = json.loads(tool_args)
                except:
                    tool_args = {}
            
            # Validar que tenemos un nombre de herramienta
            if not tool_name:
                logger.warning(f"[CUSTOM AGENT] Tool call sin nombre, saltando: {tool_call}")
                continue
            
            logger.info(f"[CUSTOM AGENT] Ejecutando herramienta: {tool_name} con args: {tool_args}")
            
            try:
                # Obtener la herramienta del diccionario
                if tool_name not in tools_by_name:
                    error_msg = f"Herramienta '{tool_name}' no encontrada"
                    logger.error(f"[CUSTOM AGENT] {error_msg}")
                    tool_messages.append(
                        ToolMessage(
                            content=error_msg,
                            tool_call_id=str(tool_call_id)
                        )
                    )
                    continue
                
                tool = tools_by_name[tool_name]
                
                # Invocar la herramienta de forma asíncrona
                tool_result = await tool.ainvoke(tool_args)
                
                # Convertir el resultado a string si es necesario
                if isinstance(tool_result, str):
                    result_content = tool_result
                elif isinstance(tool_result, dict):
                    result_content = tool_result.get("content", tool_result.get("result", str(tool_result)))
                else:
                    result_content = str(tool_result)
                
                logger.info(f"[CUSTOM AGENT] Herramienta {tool_name} ejecutada exitosamente ({len(result_content)} caracteres)")
                
                # Crear mensaje con el resultado de la herramienta
                tool_messages.append(
                    ToolMessage(
                        content=result_content,
                        tool_call_id=str(tool_call_id)
                    )
                )
                
            except Exception as e:
                error_msg = f"Error al ejecutar herramienta {tool_name}: {str(e)}"
                logger.error(f"[CUSTOM AGENT] {error_msg}")
                tool_messages.append(
                    ToolMessage(
                        content=error_msg,
                        tool_call_id=str(tool_call_id)
                    )
                )
        
        # Actualizar el estado con los resultados de las herramientas
        return {
            "messages": list(messages) + tool_messages
        }
    
    # ===========================================================================
    # Función condicional: Decide si continuar o terminar
    # ===========================================================================
    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """
        Función que decide si el agente debe continuar usando herramientas o terminar.
        
        Esta función implementa la lógica de aristas condicionales:
        - Si el último mensaje tiene tool calls, va a "tools"
        - Si el último mensaje es una respuesta final, va a "end"
        
        Args:
            state: Estado actual del agente
        
        Returns:
            "tools" si debe ejecutar herramientas, "end" si debe terminar
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # Verificar si el último mensaje tiene tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            logger.info(f"[CUSTOM AGENT] Decisión: continuar con herramientas ({len(last_message.tool_calls)} tool calls)")
            return "tools"
        else:
            logger.info("[CUSTOM AGENT] Decisión: terminar (respuesta final)")
            return "end"
    
    # ===========================================================================
    # Construir el grafo: agregar nodos, edges y condiciones
    # ===========================================================================
    
    # Agregar los nodos al grafo
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    
    # Definir el punto de entrada
    graph.set_entry_point("agent")
    
    # Agregar arista condicional desde "agent"
    # La función should_continue decide si ir a "tools" o "end"
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Agregar arista desde "tools" de vuelta a "agent" (ciclo de retroalimentación)
    graph.add_edge("tools", "agent")
    
    # Compilar el grafo
    flow = graph.compile()
    
    logger.info("[CUSTOM AGENT] Grafo ReAct compilado exitosamente con ciclos de retroalimentación")
    return flow