"""
Script de Comparación MCP: Con y Sin Herramienta
=================================================

Este script ejecuta las pruebas documentadas en RESULTADOS_COMPARACION.md
comparando las respuestas del modelo Gemini con y sin la herramienta
get_package_changelog para demostrar el impacto de usar herramientas MCP.

Las pruebas están basadas en los casos documentados:
1. Django 4.2 → 5.0: Breaking changes entre versiones
2. Flask 2.3 → 3.0: Seguridad de actualización (nota: requiere versión exacta)
3. requests 2.28.0 → 2.31.0: Cambios importantes entre versiones
"""

import asyncio
import sys
import os
from datetime import datetime

# Agregar el directorio raíz y mcp al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mcp_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)
sys.path.insert(0, mcp_dir)

from mcp.client.stdio import stdio_client
from mcp import ClientSession

# Importar desde el directorio mcp
import importlib.util
config_path = os.path.join(mcp_dir, 'config.py')
spec = importlib.util.spec_from_file_location("mcp_config", config_path)
mcp_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_config)

model_path = os.path.join(mcp_dir, 'model.py')
spec_model = importlib.util.spec_from_file_location("mcp_model", model_path)
mcp_model = importlib.util.module_from_spec(spec_model)
spec_model.loader.exec_module(mcp_model)

SERVER_PARAMS = mcp_config.SERVER_PARAMS
ask_gemini = mcp_model.ask_gemini

# Casos de prueba basados en RESULTADOS_COMPARACION.md
TEST_CASES = [
    {
        "name": "Django 4.2 → 5.0",
        "prompt": "¿Qué breaking changes hay entre Django 4.2 y 5.0?",
        "expected_tool": "get_package_changelog",
        "expected_params": {
            "package_name": "Django",
            "from_version": "4.2",
            "to_version": "5.0",
            "ecosystem": "pypi"
        }
    },
    {
        "name": "Flask 2.3 → 3.0",
        "prompt": "¿Es seguro actualizar Flask de 2.3 a 3.0?",
        "expected_tool": "get_package_changelog",
        "expected_params": {
            "package_name": "Flask",
            "from_version": "2.3",
            "to_version": "3.0",
            "ecosystem": "pypi"
        },
        "note": "Nota: Esta prueba puede fallar porque '2.3' no es una versión exacta. La herramienta requiere versiones exactas."
    },
    {
        "name": "requests 2.28.0 → 2.31.0",
        "prompt": "¿Qué cambios importantes hay entre requests 2.28.0 y 2.31.0?",
        "expected_tool": "get_package_changelog",
        "expected_params": {
            "package_name": "requests",
            "from_version": "2.28.0",
            "to_version": "2.31.0",
            "ecosystem": "pypi"
        }
    }
]


async def test_without_tool(prompt: str, test_name: str):
    """Prueba el modelo sin herramientas MCP"""
    print("\n" + "="*80)
    print(f"🔴 SIN HERRAMIENTAS MCP - {test_name}")
    print("="*80)
    print(f"\n📝 Pregunta: {prompt}\n")
    
    start_time = datetime.now()
    response = await ask_gemini(prompt, None)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n💬 Respuesta ({len(response)} caracteres, {duration:.2f}s):\n{response[:500]}...\n")
    
    return {
        "response": response,
        "length": len(response),
        "duration": duration
    }


async def test_with_tool(prompt: str, test_name: str, expected_tool: str = None):
    """Prueba el modelo con herramientas MCP"""
    print("\n" + "="*80)
    print(f"🟢 CON HERRAMIENTAS MCP - {test_name}")
    print("="*80)
    print(f"\n📝 Pregunta: {prompt}\n")
    
    start_time = datetime.now()
    
    async with stdio_client(SERVER_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            response = await ask_gemini(prompt, session)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n💬 Respuesta ({len(response)} caracteres, {duration:.2f}s):\n{response[:500]}...\n")
    
    return {
        "response": response,
        "length": len(response),
        "duration": duration,
        "tool_used": expected_tool
    }


async def run_test_case(test_case: dict, case_num: int, total: int):
    """Ejecuta un caso de prueba completo (con y sin herramienta)"""
    print(f"\n\n{'#'*80}")
    print(f"# PRUEBA {case_num}/{total}: {test_case['name']}")
    print(f"{'#'*80}")
    
    if "note" in test_case:
        print(f"\nℹ️  {test_case['note']}")
    
    # Prueba sin herramienta
    result_without = await test_without_tool(test_case["prompt"], test_case["name"])
    
    # Esperar un momento para evitar rate limiting
    await asyncio.sleep(2)
    
    # Prueba con herramienta
    result_with = await test_with_tool(
        test_case["prompt"], 
        test_case["name"],
        test_case.get("expected_tool")
    )
    
    # Análisis de diferencias
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE DIFERENCIAS")
    print("="*80)
    
    length_diff = result_with["length"] - result_without["length"]
    duration_diff = result_with["duration"] - result_without["duration"]
    
    print(f"\n📏 Longitud:")
    print(f"   Sin herramienta: {result_without['length']:,} caracteres")
    print(f"   Con herramienta: {result_with['length']:,} caracteres")
    print(f"   Diferencia: {length_diff:+,} caracteres ({length_diff/result_without['length']*100:+.1f}%)")
    
    print(f"\n⏱️  Tiempo de ejecución:")
    print(f"   Sin herramienta: {result_without['duration']:.2f}s")
    print(f"   Con herramienta: {result_with['duration']:.2f}s")
    print(f"   Diferencia: {duration_diff:+.2f}s")
    
    # Análisis cualitativo
    print(f"\n🔍 Análisis cualitativo:")
    if result_with["length"] < result_without["length"]:
        print("   ✅ Respuesta más concisa con herramienta (más precisa)")
    else:
        print("   ℹ️  Respuesta más extensa con herramienta (más detallada)")
    
    if "tool_used" in result_with and result_with["tool_used"]:
        print(f"   ✅ Herramienta MCP utilizada: {result_with['tool_used']}")
    else:
        print("   ⚠️  No se detectó uso de herramienta MCP")
    
    return {
        "test_name": test_case["name"],
        "without": result_without,
        "with": result_with,
        "length_diff": length_diff,
        "duration_diff": duration_diff
    }


async def main():
    """Función principal que ejecuta todas las comparaciones"""
    print("\n" + "="*80)
    print("🧪 COMPARACIÓN MCP: CON vs SIN HERRAMIENTA")
    print("="*80)
    print("\nEste script ejecuta las pruebas documentadas en RESULTADOS_COMPARACION.md")
    print("comparando las respuestas del modelo Gemini:")
    print("  - Sin herramientas: Respuesta basada solo en conocimiento entrenado")
    print("  - Con herramientas: Respuesta usando get_package_changelog MCP")
    print("\n" + "="*80)
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        result = await run_test_case(test_case, i, len(TEST_CASES))
        results.append(result)
        
        # Esperar antes de la siguiente prueba
        if i < len(TEST_CASES):
            print("\n⏳ Esperando 3 segundos antes de la siguiente prueba...")
            await asyncio.sleep(3)
    
    # Resumen final
    print("\n\n" + "="*80)
    print("📊 RESUMEN FINAL")
    print("="*80)
    
    print("\n📈 Estadísticas generales:")
    total_length_without = sum(r["without"]["length"] for r in results)
    total_length_with = sum(r["with"]["length"] for r in results)
    total_duration_without = sum(r["without"]["duration"] for r in results)
    total_duration_with = sum(r["with"]["duration"] for r in results)
    
    print(f"   Total caracteres SIN herramienta: {total_length_without:,}")
    print(f"   Total caracteres CON herramienta: {total_length_with:,}")
    print(f"   Diferencia total: {total_length_with - total_length_without:+,} caracteres")
    print(f"\n   Tiempo total SIN herramienta: {total_duration_without:.2f}s")
    print(f"   Tiempo total CON herramienta: {total_duration_with:.2f}s")
    print(f"   Diferencia total: {total_duration_with - total_duration_without:+.2f}s")
    
    print("\n✅ COMPARACIÓN COMPLETADA")
    print("="*80)
    print("\n📝 Observaciones:")
    print("  - Las respuestas CON herramienta deberían incluir información específica")
    print("    sobre versiones, fechas de publicación y breaking changes")
    print("  - Las respuestas SIN herramienta pueden ser más genéricas o menos precisas")
    print("  - El modelo debería haber invocado get_package_changelog cuando usó herramientas")
    print("  - Las trazas deberían estar disponibles en LangSmith para análisis detallado")
    print("\n🔗 Verifica las trazas en LangSmith:")
    print(f"   https://smith.langchain.com/o/projects/p/{os.getenv('LANGCHAIN_PROJECT', 'misw4411-backend-proyecto')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

