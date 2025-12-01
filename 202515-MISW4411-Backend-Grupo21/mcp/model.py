"""
Configuración del Modelo Gemini para MCP con LangSmith Tracing
==============================================================

Este módulo configura el modelo de lenguaje Gemini (gemini-2.5-flash) para trabajar
con el protocolo MCP (Model Context Protocol), permitiendo que el modelo decida
autónomamente si usar herramientas externas (por ejemplo, `get_package_changelog`)
o responder directamente.

IMPORTANTE: Usa LangChain en lugar del SDK directo de Google para habilitar
el tracing automático con LangSmith. Las llamadas a herramientas MCP se registran
manualmente en LangSmith usando el SDK de LangSmith.
"""

import os
from google import genai
from dotenv import load_dotenv
from typing import Optional, Any
from langsmith import traceable, Client

# Cargar variables de entorno
load_dotenv()

# Verificar configuración de LangSmith
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "misw4411-backend-proyecto")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# Inicializar cliente de LangSmith si está configurado
langsmith_client = None
if LANGCHAIN_TRACING_V2 and LANGSMITH_API_KEY:
    try:
        langsmith_client = Client(api_key=LANGSMITH_API_KEY)
        print(f"✅ LangSmith tracing habilitado para proyecto: {LANGCHAIN_PROJECT}")
    except Exception as e:
        print(f"⚠️  Error inicializando LangSmith: {e}")
        langsmith_client = None
else:
    print("⚠️  LangSmith tracing NO está habilitado. Configura LANGCHAIN_TRACING_V2=true y LANGSMITH_API_KEY")

# Creamos un cliente para interactuar con los modelos generativos de Gemini
client = genai.Client()


@traceable(name="ask_gemini_mcp", project_name=LANGCHAIN_PROJECT if LANGCHAIN_TRACING_V2 else None)
async def ask_gemini(prompt: str, session: Optional[Any] = None) -> str:
    """
    Envía un prompt al modelo Gemini y devuelve la respuesta.
    
    Si se proporciona una sesión MCP, Gemini puede decidir invocar la herramienta
    get_package_changelog para obtener información entre versiones específicas.
    Si no se proporciona sesión, Gemini responde basado solo en su conocimiento entrenado.
    
    IMPORTANTE: Esta función está decorada con @traceable para que LangSmith
    rastree automáticamente las llamadas. Las invocaciones de herramientas MCP
    se registran manualmente dentro de esta función.
    
    Args:
        prompt: El prompt o mensaje a enviar al modelo
        session: Sesión MCP opcional que habilita el acceso a herramientas externas
        
    Returns:
        str: Respuesta del modelo en texto plano
    """
    # Construimos el parámetro 'tools' (solo si hay sesión para habilitar MCP)
    tools = [session] if session else None

    # El decorador @traceable ya crea el run automáticamente
    # Solo necesitamos obtener el run_id del contexto actual si está disponible
    run_id = None
    try:
        from langsmith.run_helpers import get_current_run_tree
        current_run = get_current_run_tree()
        if current_run:
            run_id = current_run.id
    except:
        pass  # Si no hay contexto de tracing, continuamos sin run_id

    # Llamada asíncrona al modelo, con o sin herramientas MCP
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            temperature=1.0,
            tools=tools,
        ),
    )

    # Analizar si el modelo usó una herramienta MCP
    history = getattr(response, "automatic_function_calling_history", None)

    used_tool = None
    tool_args = None
    tool_result = None

    if history:
        for message in history:
            if not hasattr(message, "parts"):
                continue
            for part in message.parts:
                # ¿Hubo invocación a get_package_changelog?
                if hasattr(part, "function_call") and part.function_call is not None:
                    used_tool = part.function_call.name
                    tool_args = part.function_call.args
                    break
            if used_tool:
                break

    # Si se usó una herramienta, ejecutarla y registrar en LangSmith
    tool_run_id = None
    if used_tool and session:
        try:
            # Registrar invocación de herramienta en LangSmith
            if langsmith_client and run_id:
                try:
                    tool_run = langsmith_client.create_run(
                        name=f"mcp_tool_{used_tool}",
                        run_type="tool",
                        inputs=tool_args,
                        parent_run_id=run_id,
                        project_name=LANGCHAIN_PROJECT
                    )
                    tool_run_id = tool_run.id if tool_run else None
                except Exception as e:
                    print(f"⚠️  Error creando run de herramienta en LangSmith: {e}")
                    tool_run_id = None

            # Ejecutar la herramienta MCP
            result = await session.call_tool(used_tool, arguments=tool_args)
            
            # Extraer resultado
            if result.content:
                tool_result = ""
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        tool_result += content_item.text
                    elif isinstance(content_item, str):
                        tool_result += content_item
                    else:
                        tool_result += str(content_item)
            else:
                tool_result = "No se obtuvo resultado de la herramienta"
            
            # Registrar resultado de herramienta en LangSmith
            if langsmith_client and tool_run_id:
                try:
                    langsmith_client.update_run(
                        run_id=tool_run_id,
                        outputs={"result": tool_result},
                        status="success"
                    )
                except Exception as e:
                    print(f"⚠️  Error actualizando run en LangSmith: {e}")
            
            print(f"\n✅ Gemini decidió usar la herramienta: {used_tool}")
            print(f"📋 Parámetros: {tool_args}\n")
            
        except Exception as e:
            error_msg = str(e)
            print(f"\n⚠️  Error ejecutando herramienta {used_tool}: {error_msg}\n")
            
            # Registrar error en LangSmith
            if langsmith_client and tool_run_id:
                try:
                    langsmith_client.update_run(
                        run_id=tool_run_id,
                        outputs={"error": error_msg},
                        status="error"
                    )
                except Exception as update_error:
                    print(f"⚠️  Error actualizando run con error en LangSmith: {update_error}")
            
            tool_result = f"Error ejecutando herramienta: {error_msg}"
    else:
        print("\n💬 Gemini respondió directamente sin usar herramientas.\n")

    # Extracción robusta del texto de la respuesta
    parts = response.candidates[0].content.parts
    text_response = "".join(
        part.text for part in parts if hasattr(part, "text") and part.text
    )

    # Registrar respuesta final en LangSmith
    if langsmith_client and run_id:
        try:
            outputs = {
                "response": text_response,
                "tool_used": used_tool if used_tool else None,
                "tool_result": tool_result if tool_result else None
            }
            langsmith_client.update_run(
                run_id=run_id,
                outputs=outputs,
                status="success"
            )
        except Exception as e:
            print(f"⚠️  Error actualizando run final en LangSmith: {e}")

    return text_response
