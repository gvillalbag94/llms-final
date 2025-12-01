"""
Configuración del servidor MCP
===============================

Este archivo configura la conexión al servidor MCP personalizado de Package Changelog.

El servidor package_changelog_server proporciona herramientas para consultar
changelogs y breaking changes de paquetes Python en tiempo real.
"""

from mcp import StdioServerParameters
from dotenv import load_dotenv
import os
import platform

# Cargar las variables de entorno del archivo .env
load_dotenv()

# Cargar la clave de API en la variable usada por el SDK
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Determinar la ruta correcta según el sistema operativo
if platform.system() == "Windows":
    # Para Windows: la ruta es env\Scripts\python.exe
    python_path = "env\\Scripts\\python.exe"
else:
    # Para macOS/Linux: la ruta es env/bin/python
    python_path = "env/bin/python"

# Configuración del servidor MCP a usar
# Se ejecuta el servidor personalizado de changelog de paquetes
SERVER_PARAMS = StdioServerParameters(
    command=python_path,
    args=["mcp/package_changelog_server.py"]
)

