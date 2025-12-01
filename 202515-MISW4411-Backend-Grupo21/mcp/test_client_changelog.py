"""
Cliente de prueba para el servidor MCP package_changelog_server
================================================================

Este script prueba las herramientas disponibles en el servidor de changelog de paquetes.
"""

import asyncio
import sys
import os

# Agregar el directorio actual al path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.config import SERVER_PARAMS

async def test_changelog_server():
    """
    Prueba las herramientas del servidor de changelog de paquetes
    """
    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                # Inicializar sesión
                await session.initialize()
                
                # Listar herramientas disponibles
                tools = await session.list_tools()
                print("🔧 Herramientas disponibles:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                    if hasattr(tool, 'inputSchema'):
                        print(f"    Schema: {tool.inputSchema}")
                    print()
                
                print("="*50 + "\n")
                
                # Probar get_package_changelog
                print("📚 Probando get_package_changelog...")
                print("Paquete: Django, de 4.2 a 5.0\n")
                resultado1 = await session.call_tool(
                    "get_package_changelog",
                    arguments={
                        "package_name": "Django",
                        "from_version": "4.2",
                        "to_version": "5.0",
                        "ecosystem": "pypi"
                    }
                )
                if resultado1.content:
                    text_result = resultado1.content[0].text if hasattr(resultado1.content[0], 'text') else str(resultado1.content[0])
                    print(f"Resultado:\n{text_result}")
                else:
                    print("Sin resultado")
                
                print("\n" + "="*50 + "\n")
                
                # Probar get_package_info
                print("📦 Probando get_package_info...")
                print("Paquete: requests\n")
                resultado2 = await session.call_tool(
                    "get_package_info",
                    arguments={
                        "package_name": "requests",
                        "ecosystem": "pypi"
                    }
                )
                if resultado2.content:
                    text_result = resultado2.content[0].text if hasattr(resultado2.content[0], 'text') else str(resultado2.content[0])
                    print(f"Resultado:\n{text_result[:800]}...")  # Primeros 800 caracteres
                else:
                    print("Sin resultado")
                
                print("\n" + "="*50)
                print("✅ Pruebas completadas exitosamente")
                
    except Exception as e:
        print(f"❌ Error al ejecutar las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_changelog_server())

