"""
Servicio del Agente Especializado
==================================

Este módulo gestiona el ciclo de vida del Agente Especializado (ReAct), incluyendo
la inicialización de la sesión MCP, carga de múltiples herramientas y ejecución
del agente para procesar tareas complejas de los usuarios.

IMPLEMENTACIÓN SEMANA 7:
- Completar el método ask_custom para invocar el agente ReAct
- Pasar la pregunta del usuario al agente compilado
- Extraer el último mensaje (respuesta final) del resultado
- Retornar el string de la respuesta final
"""

from langchain_core.messages import HumanMessage, AIMessage
from flows.custom_agent import build_custom_agent
from mcp.client.stdio import stdio_client
from mcp_server.tools import load_tools
from mcp_server.model import llm
from mcp import ClientSession
import asyncio
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CustomAgentService:


    def __init__(self):
        self.server_parameters = None
        self._lock = asyncio.Lock()
        self._stdio_ctx = None
        self._session = None
        self.agent = None

    
    def set_server_parameters(self, server_parameters):
        self.server_parameters = server_parameters
    

    async def initialize(self):
        """
        Inicializa la sesión MCP y construye el agente personalizado.
        
        NOTA: Este método ya está implementado y NO necesita modificación.
        """
        async with self._lock:
            if self._session is None:
                if not self.server_parameters:
                    raise ValueError("MCP server parameters not set. Call set_server_parameters() first")
                
                logger.info("Starting stdio_client...")
                self._stdio_ctx = stdio_client(self.server_parameters)
                read, write = await self._stdio_ctx.__aenter__()
                self._session = await ClientSession(read, write).__aenter__()
                await self._session.initialize()
                logger.info("MCP session initialized successfully")

                # Cargar herramientas del MCP server
                tools, tools_by_name = await load_tools(self._session)
                logger.info(f"Loaded {len(tools)} tools from MCP server")

                # Construir el agente personalizado con herramientas vinculadas
                # IMPORTANTE: El model ya viene con bind_tools(tools) aplicado
                self.agent = build_custom_agent(llm.bind_tools(tools), tools_by_name)
                logger.info("Custom Agent created successfully")
    

    # ===============================================================================
    # SEMANA 7: Implementar la ejecución del agente personalizado
    # ===============================================================================
    

    async def ask_custom(self, question):
        """
        Procesa una pregunta usando el agente personalizado ReAct.
        
        El agente puede usar múltiples herramientas en secuencia hasta completar la tarea.
        El estado se mantiene a lo largo de todo el flujo de razonamiento.
        
        Args:
            question (str): La pregunta o tarea del usuario
        
        Returns:
            str: La respuesta generada por el agente
        """
        # Asegurarse de que el agente está inicializado
        if self._session is None or self.agent is None:
            await self.initialize()
        
        logger.info(f"[CUSTOM SERVICE] Processing question: {question}")
        
        try:
            # Crear el estado inicial con el mensaje del usuario
            initial_state = {
                "messages": [HumanMessage(content=question)]
            }
            
            # Invocar el agente compilado
            # El agente ejecutará el ciclo ReAct hasta completar la tarea
            logger.info("[CUSTOM SERVICE] Invocando agente ReAct...")
            final_state = await self.agent.ainvoke(initial_state)
            
            # Extraer la respuesta final del último mensaje
            messages = final_state.get("messages", [])
            if not messages:
                return "No se generó ninguna respuesta."
            
            # El último mensaje debería ser la respuesta final del LLM
            last_message = messages[-1]
            
            # Extraer el contenido de la respuesta
            if hasattr(last_message, 'content'):
                answer = last_message.content
            else:
                answer = str(last_message)
            
            # Validar que la respuesta no sea None o vacía
            if answer is None:
                logger.warning("[CUSTOM SERVICE] La respuesta es None, buscando en mensajes anteriores...")
                # Buscar en mensajes anteriores
                for msg in reversed(messages):
                    if hasattr(msg, 'content') and msg.content:
                        answer = msg.content
                        break
                if answer is None:
                    answer = "No se pudo generar una respuesta. Por favor, intenta con otra pregunta."
            
            # Asegurar que sea string
            if not isinstance(answer, str):
                answer = str(answer) if answer else "No se pudo generar una respuesta."
            
            logger.info(f"[CUSTOM SERVICE] Respuesta generada exitosamente ({len(answer)} caracteres)")
            logger.info(f"[CUSTOM SERVICE] Total de mensajes en el flujo: {len(messages)}")
            
            return answer
            
        except Exception as e:
            error_msg = f"Error al procesar la pregunta: {str(e)}"
            logger.error(f"[CUSTOM SERVICE] {error_msg}")
            raise Exception(error_msg)
    

    async def shutdown(self):
        """
        Cierra la sesión MCP y limpia recursos.
        
        NOTA: Este método ya está implementado y NO necesita modificación.
        """
        async with self._lock:
            if self._session:
                await self._session.__aexit__(None, None, None)
                self._session = None
            if self._stdio_ctx:
                await self._stdio_ctx.__aexit__(None, None, None)
                self._stdio_ctx = None
            logger.debug("MCP session and stdio_client shut down")


CUSTOM_AGENT_SERVICE = CustomAgentService()
