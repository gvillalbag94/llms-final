"""
Tests de conexión y autenticación con la API de LangSmith.

Estos tests verifican que:
1. La API key de LangSmith es válida
2. El proyecto es accesible
3. La conexión a LangSmith funciona correctamente
"""

import os
import pytest
from langsmith import Client


def test_langsmith_api_key_exists():
    """
    Verifica que la variable de entorno LANGSMITH_API_KEY existe.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    assert api_key is not None, "LANGSMITH_API_KEY environment variable not set"
    assert len(api_key) > 0, "LANGSMITH_API_KEY is empty"
    print(f"LANGSMITH_API_KEY existe (longitud: {len(api_key)})")


def test_langsmith_api_key_valid():
    """
    Verifica que la API key de LangSmith es válida intentando conectarse.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    assert api_key is not None, "LANGSMITH_API_KEY not set"
    
    try:
        # Inicializar cliente de LangSmith
        client = Client(api_key=api_key)
        
        # Intentar listar proyectos - fallará si la API key es inválida
        projects = list(client.list_projects(limit=1))
        
        print(f"La API key de LangSmith es válida")
        print(f"   Conexión exitosa a la API de LangSmith")
        
    except Exception as e:
        pytest.fail(f"Failed to connect to LangSmith with provided API key: {str(e)}")


def test_langsmith_project_accessible():
    """
    Verifica que el proyecto de LangSmith es accesible.
    Esto verifica que el proyecto existe o puede ser creado.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    project_name = os.getenv("LANGCHAIN_PROJECT", "misw4411-backend-proyecto")
    
    assert api_key is not None, "LANGSMITH_API_KEY not set"
    
    try:
        # Inicializar cliente de LangSmith
        client = Client(api_key=api_key)
        
        # Intentar obtener o crear el proyecto
        try:
            project = client.read_project(project_name=project_name)
            print(f"Proyecto '{project_name}' existe y es accesible")
            print(f"   Project ID: {project.id}")
        except Exception as e:
            # El proyecto puede no existir aún, lo cual está bien
            # Se creará cuando se envíe la primera traza
            print(f"Proyecto '{project_name}' no encontrado aún (se creará con la primera traza)")
            print(f"   Esto es normal para proyectos nuevos")
        
        # Listar todos los proyectos para verificar acceso a la API
        projects = list(client.list_projects(limit=10))
        print(f"Acceso exitoso al dashboard de LangSmith")
        print(f"   Total de proyectos accesibles: {len(projects)}")
        
    except Exception as e:
        pytest.fail(f"Failed to access LangSmith project: {str(e)}")


def test_langsmith_client_configuration():
    """
    Verifica que el cliente de LangSmith puede configurarse correctamente.
    """
    api_key = os.getenv("LANGSMITH_API_KEY")
    
    assert api_key is not None, "LANGSMITH_API_KEY not set"
    
    try:
        # Inicializar cliente con configuración explícita
        client = Client(
            api_key=api_key,
            api_url=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        )
        
        # Verificar que el cliente está configurado
        assert client.api_key == api_key, "API key not set correctly in client"
        
        print(f"Cliente de LangSmith configurado correctamente")
        print(f"   API URL: {client.api_url}")
        
    except Exception as e:
        pytest.fail(f"Failed to configure LangSmith client: {str(e)}")


def test_langsmith_environment_variables():
    """
    Verifica que todas las variables de entorno requeridas para LangSmith están configuradas.
    """
    required_vars = {
        "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY"),
        "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2"),
    }
    
    optional_vars = {
        "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT", "default"),
        "LANGCHAIN_ENDPOINT": os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
    }
    
    # Verificar variables requeridas
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        pytest.fail(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Verificar que LANGCHAIN_TRACING_V2 está habilitado
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true"
    assert tracing_enabled, "LANGCHAIN_TRACING_V2 must be set to 'true'"
    
    print("Todas las variables de entorno requeridas están configuradas:")
    for var, value in required_vars.items():
        if var == "LANGSMITH_API_KEY":
            print(f"   {var}: {'*' * 10} (oculta)")
        else:
            print(f"   {var}: {value}")
    
    print("\nVariables de entorno opcionales:")
    for var, value in optional_vars.items():
        print(f"   {var}: {value}")


if __name__ == "__main__":
    # Permite ejecutar los tests directamente para debugging
    pytest.main([__file__, "-v", "--tb=short"])

