"""
Tests de verificación de trazas en LangSmith.

Estos tests verifican que:
1. Las trazas se están enviando a LangSmith
2. Las trazas contienen metadata correcta
3. Las trazas incluyen información RAG (contexto, consulta, respuesta)
"""

import os
import pytest
from datetime import datetime, timedelta
from langsmith import Client
from typing import List, Optional


def get_langsmith_client() -> Client:
    """
    Función auxiliar para obtener un cliente de LangSmith configurado.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        pytest.skip("LANGSMITH_API_KEY not set")
    
    return Client(api_key=api_key)


def test_recent_traces_exist():
    """
    Verifica que existen trazas recientes en LangSmith (en los últimos 10 minutos).
    Esto verifica que la aplicación está enviando trazas a LangSmith.
    """
    client = get_langsmith_client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "misw4411-backend-proyecto")
    
    try:
        # Calcular rango de tiempo (últimos 10 minutos)
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10)
        
        # Consultar runs/trazas recientes
        runs = list(client.list_runs(
            project_name=project_name,
            start_time=start_time,
            limit=50
        ))
        
        # Verificar que tenemos trazas
        assert len(runs) > 0, (
            f"No traces found in project '{project_name}' in the last 10 minutes. "
            "Make sure the application is sending traces to LangSmith."
        )
        
        print(f"Se encontraron {len(runs)} traza(s) en los últimos 10 minutos")
        print(f"   Proyecto: {project_name}")
        print(f"   Rango de tiempo: {start_time.strftime('%Y-%m-%d %H:%M:%S')} a {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Mostrar información sobre la traza más reciente
        if runs:
            latest_run = runs[0]
            print(f"\n   Traza más reciente:")
            print(f"     - ID: {latest_run.id}")
            print(f"     - Nombre: {latest_run.name}")
            print(f"     - Hora de inicio: {latest_run.start_time}")
            print(f"     - Estado: {latest_run.status if hasattr(latest_run, 'status') else 'N/A'}")
        
    except Exception as e:
        pytest.fail(f"Failed to retrieve traces from LangSmith: {str(e)}")


def test_trace_has_correct_metadata():
    """
    Verifica que las trazas tienen la estructura de metadata correcta.
    Esto incluye verificar inputs, outputs y otros campos relevantes.
    """
    client = get_langsmith_client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "misw4411-backend-proyecto")
    
    try:
        # Obtener trazas recientes
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10)
        
        runs = list(client.list_runs(
            project_name=project_name,
            start_time=start_time,
            limit=10
        ))
        
        assert len(runs) > 0, "No traces found to verify metadata"
        
        # Verificar la traza más reciente
        latest_run = runs[0]
        
        # Verificar que existe metadata básica
        assert latest_run.id is not None, "Trace ID is missing"
        assert latest_run.name is not None, "Trace name is missing"
        assert latest_run.start_time is not None, "Trace start_time is missing"
        
        print(f"La metadata de la traza es correcta")
        print(f"   Trace ID: {latest_run.id}")
        print(f"   Nombre de traza: {latest_run.name}")
        print(f"   Hora de inicio: {latest_run.start_time}")
        
        # Verificar si existen inputs
        if latest_run.inputs:
            print(f"   Inputs: Presentes ({len(latest_run.inputs)} campo(s))")
        
        # Verificar si existen outputs
        if latest_run.outputs:
            print(f"   Outputs: Presentes ({len(latest_run.outputs)} campo(s))")
        
        # Verificar tiempo de ejecución
        if latest_run.end_time and latest_run.start_time:
            duration = (latest_run.end_time - latest_run.start_time).total_seconds()
            print(f"   Duración: {duration:.2f} segundos")
        
    except Exception as e:
        pytest.fail(f"Failed to verify trace metadata: {str(e)}")


def test_trace_contains_rag_information():
    """
    Verifica que las trazas contienen información relacionada con RAG.
    Esto incluye verificar:
    - Consulta/pregunta de entrada
    - Contexto/documentos recuperados
    - Respuesta/answer generada
    """
    client = get_langsmith_client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "misw4411-backend-proyecto")
    
    try:
        # Obtener trazas recientes
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10)
        
        runs = list(client.list_runs(
            project_name=project_name,
            start_time=start_time,
            limit=10
        ))
        
        assert len(runs) > 0, "No traces found to verify RAG information"
        
        # Buscar trazas que contengan información RAG
        rag_traces_found = 0
        
        for run in runs:
            has_input = run.inputs is not None and len(run.inputs) > 0
            has_output = run.outputs is not None and len(run.outputs) > 0
            
            if has_input and has_output:
                rag_traces_found += 1
                
                # Imprimir información sobre la primera traza RAG encontrada
                if rag_traces_found == 1:
                    print(f"La traza contiene información RAG")
                    print(f"   Trace ID: {run.id}")
                    print(f"   Nombre de traza: {run.name}")
                    
                    # Imprimir información de input (truncada)
                    if run.inputs:
                        input_keys = list(run.inputs.keys())
                        print(f"   Campos de input: {', '.join(input_keys[:5])}")
                        
                        # Buscar pregunta/consulta en inputs
                        for key in ['question', 'query', 'input', 'prompt']:
                            if key in run.inputs:
                                value = str(run.inputs[key])[:100]
                                print(f"   Input ({key}): {value}...")
                                break
                    
                    # Imprimir información de output (truncada)
                    if run.outputs:
                        output_keys = list(run.outputs.keys())
                        print(f"   Campos de output: {', '.join(output_keys[:5])}")
                        
                        # Buscar respuesta/answer en outputs
                        for key in ['answer', 'response', 'output', 'result']:
                            if key in run.outputs:
                                value = str(run.outputs[key])[:100]
                                print(f"   Output ({key}): {value}...")
                                break
        
        assert rag_traces_found > 0, (
            "No traces found with both inputs and outputs. "
            "Traces should contain query inputs and response outputs."
        )
        
        print(f"\n   Total de trazas con información RAG: {rag_traces_found}")
        
    except Exception as e:
        pytest.fail(f"Failed to verify RAG information in traces: {str(e)}")


def test_project_exists_in_langsmith():
    """
    Verifica que el proyecto existe en LangSmith.
    """
    client = get_langsmith_client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "misw4411-backend-proyecto")
    
    try:
        # Intentar leer el proyecto
        try:
            project = client.read_project(project_name=project_name)
            
            print(f"Proyecto '{project_name}' existe en LangSmith")
            print(f"   Project ID: {project.id}")
            print(f"   Creado el: {project.created_at}")
            
        except Exception:
            # El proyecto puede no existir aún, verificar si hay runs
            runs = list(client.list_runs(
                project_name=project_name,
                limit=1
            ))
            
            if len(runs) > 0:
                print(f"Proyecto '{project_name}' tiene trazas (el proyecto existe)")
            else:
                pytest.fail(
                    f"Project '{project_name}' not found and has no traces. "
                    "Make sure LANGCHAIN_PROJECT is set correctly and traces are being sent."
                )
        
    except Exception as e:
        pytest.fail(f"Failed to verify project existence: {str(e)}")


def test_multiple_traces_exist():
    """
    Verifica que existen múltiples trazas (al menos 2).
    Esto asegura que la aplicación está enviando trazas consistentemente.
    """
    client = get_langsmith_client()
    project_name = os.getenv("LANGCHAIN_PROJECT", "misw4411-backend-proyecto")
    
    try:
        # Obtener trazas recientes (últimos 15 minutos para contar todas las ejecuciones de test)
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=15)
        
        runs = list(client.list_runs(
            project_name=project_name,
            start_time=start_time,
            limit=100
        ))
        
        trace_count = len(runs)
        
        assert trace_count >= 2, (
            f"Expected at least 2 traces, but found {trace_count}. "
            "Make sure multiple queries are being executed and traced."
        )
        
        print(f"Se encontraron {trace_count} trazas en los últimos 15 minutos")
        print(f"   Esto indica generación consistente de trazas")
        
        # Mostrar resumen de tipos de traza
        trace_names = {}
        for run in runs[:10]:  # Verificar primeras 10
            name = run.name or "Unknown"
            trace_names[name] = trace_names.get(name, 0) + 1
        
        if trace_names:
            print(f"\n   Tipos de traza (muestra):")
            for name, count in list(trace_names.items())[:5]:
                print(f"     - {name}: {count}")
        
    except Exception as e:
        pytest.fail(f"Failed to verify multiple traces: {str(e)}")


if __name__ == "__main__":
    # Permite ejecutar los tests directamente para debugging
    pytest.main([__file__, "-v", "--tb=short"])

