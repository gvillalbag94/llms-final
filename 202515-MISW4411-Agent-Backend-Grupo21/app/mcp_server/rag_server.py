"""
Servidor MCP para el Agente RAG
================================

Este módulo implementa el servidor MCP que expone la herramienta para consultar
el sistema RAG externo. El agente RAG utilizará esta herramienta para recuperar
contexto relevante de la base de datos vectorial.

IMPLEMENTACIÓN SEMANA 6:
- Implementar la herramienta MCP "ask" que consulta el sistema RAG
- La herramienta debe conectarse a la API del RAG (desarrollado en semanas anteriores)
- Debe manejar errores de conexión y timeout
- Retornar el contexto recuperado como string
"""

from mcp.server.fastmcp import FastMCP
import logging
import httpx
import os
import sys


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

mcp = FastMCP("rag-server")


# ===============================================================================
# SEMANA 6: Implementar el servidor MCP para RAG
# ===============================================================================

# URL del backend RAG (configurable mediante variable de entorno)
# El servidor MCP se ejecuta dentro del contenedor Docker, por lo que debe
# usar el nombre del servicio Docker para conectarse al RAG backend
RAG_BASE_URL = os.getenv("RAG_BASE_URL", "http://rag-backend:8000")
RAG_ENDPOINT = f"{RAG_BASE_URL}/api/v1/ask"

# Log la URL configurada para debugging (solo al inicio del módulo)
# Nota: Estos logs pueden no aparecer si el servidor MCP se ejecuta como proceso separado
try:
    logger.info(f"[MCP RAG] RAG_BASE_URL configurada al inicio: {RAG_BASE_URL}")
    logger.info(f"[MCP RAG] RAG_ENDPOINT: {RAG_ENDPOINT}")
except:
    pass  # Si el logger no está inicializado aún, continuar


@mcp.tool()
async def ask(query: str) -> str:
    """
    Consulta el sistema RAG externo para recuperar contexto relevante sobre una pregunta.
    
    Esta herramienta se conecta al backend RAG desarrollado en semanas anteriores
    y retorna la respuesta generada con el contexto recuperado de la base de datos vectorial.
    
    Args:
        query (str): La pregunta del usuario que se quiere responder
    
    Returns:
        str: La respuesta generada por el sistema RAG con el contexto recuperado
    
    Raises:
        Exception: Si hay un error de conexión o timeout con el backend RAG
    """
    try:
        # Usar la variable de entorno RAG_BASE_URL si está disponible
        # Si no, usar el valor por defecto (que debería estar configurado en docker-compose)
        current_rag_url = os.getenv("RAG_BASE_URL", "http://rag-backend:8000")
        current_endpoint = f"{current_rag_url}/api/v1/ask"
        
        logger.info(f"[MCP RAG] Consultando RAG backend con pregunta: {query[:100]}...")
        logger.info(f"[MCP RAG] Usando endpoint: {current_endpoint}")
        logger.info(f"[MCP RAG] RAG_BASE_URL env: {os.getenv('RAG_BASE_URL', 'NOT SET')}")
        
        # Preparar el payload para la API del RAG
        # Usar la colección python_docs donde se cargaron los documentos
        payload = {
            "question": query,
            "top_k": 5,
            "collection": "python_docs",  
            "force_rebuild": False,
            "use_reranking": False,
            "use_query_rewriting": False
        }
        
        logger.info(f"[MCP RAG] Payload: {payload}")
        
        # Realizar la petición HTTP al backend RAG
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"[MCP RAG] Enviando petición a: {current_endpoint}")
            response = await client.post(
                current_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            logger.info(f"[MCP RAG] Respuesta recibida: Status {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            
            # Extraer la respuesta del RAG
            answer = result.get("answer", "No se pudo obtener una respuesta del sistema RAG.")
            
            logger.info(f"[MCP RAG] Respuesta recibida exitosamente ({len(answer)} caracteres)")
            return answer
            
    except httpx.TimeoutException:
        error_msg = f"Timeout al consultar el sistema RAG. El servidor no respondió en 30 segundos."
        logger.error(f"[MCP RAG] {error_msg}")
        raise Exception(error_msg)
    except httpx.HTTPStatusError as e:
        error_msg = f"Error HTTP {e.response.status_code} al consultar el sistema RAG: {e.response.text}"
        logger.error(f"[MCP RAG] {error_msg}")
        raise Exception(error_msg)
    except httpx.RequestError as e:
        error_msg = f"Error de conexión con el sistema RAG en {RAG_ENDPOINT}: {str(e)}"
        logger.error(f"[MCP RAG] {error_msg}")
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Error inesperado al consultar el sistema RAG: {str(e)}"
        logger.error(f"[MCP RAG] {error_msg}")
        raise Exception(error_msg)


if __name__ == "__main__":
    mcp.run(transport="stdio")