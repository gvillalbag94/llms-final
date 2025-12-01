"""
Configuración de pytest para todos los tests del proyecto

Este módulo define fixtures globales y configuración base para
todos los tests de la aplicación FastAPI. Proporciona clientes
de prueba tanto síncronos como asíncronos.
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Agregar el directorio raíz al PYTHONPATH para importar main
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from main import app

# ==================== CONFIGURACIÓN DE TESTS ASÍNCRONOS ====================

@pytest.fixture(scope="session")
def event_loop():
    """
    Fixture que crea un event loop para toda la sesión de tests.
    
    Necesario para ejecutar tests asíncronos con pytest-asyncio.
    Crea un nuevo event loop al inicio de la sesión y lo limpia al final.
    
    Returns:
        asyncio.AbstractEventLoop: Event loop configurado para tests
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== FIXTURES DE CLIENTES DE PRUEBA ====================

@pytest.fixture
def client():
    """
    Cliente de prueba síncrono para FastAPI.
    
    Proporciona un cliente HTTP síncrono que permite hacer peticiones
    a la aplicación FastAPI sin necesidad de ejecutar un servidor real.
    
    Returns:
        TestClient: Cliente síncrono configurado con la aplicación
    """
    return TestClient(app)


@pytest.fixture
async def async_client():
    """
    Cliente de prueba asíncrono para FastAPI.
    
    Proporciona un cliente HTTP asíncrono para tests que requieren
    operaciones asíncronas o para probar endpoints async específicos.
    
    Yields:
        AsyncClient: Cliente asíncrono configurado con la aplicación
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ==================== CONFIGURACIÓN DE URLS ====================

# URL base para los tests
BASE_URL = "http://localhost:8000"

@pytest.fixture
def base_url():
    """
    URL base del servidor para tests.
    
    Proporciona la URL base configurada para hacer peticiones
    a endpoints específicos en los tests.
    
    Returns:
        str: URL base del servidor (default: http://localhost:8000)
    """
    return BASE_URL
