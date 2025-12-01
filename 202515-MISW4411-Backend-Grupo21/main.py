"""
Módulo principal de la aplicación FastAPI

Este módulo configura y lanza la aplicación FastAPI principal,
integrando todos los routers y configurando middleware para CORS.
"""

# ==================== CARGAR VARIABLES DE ENTORNO ====================
# IMPORTANTE: Debe ser lo primero para que las credenciales estén disponibles
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# ==================== CONFIGURACIÓN GIT PYTHON ====================
# Silenciar error de Git cuando no está disponible (no es necesario para descargar modelos)
# Esto es necesario porque sentence-transformers y langchain-huggingface pueden intentar
# usar GitPython para descargar modelos, pero Git no es requerido realmente
if "GIT_PYTHON_REFRESH" not in os.environ:
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"

# ==================== CONFIGURACIÓN GRPC ====================
# Silenciar advertencias de gRPC/ALTS (solo aplica en GCP)
# Estas advertencias aparecen cuando se usan bibliotecas de Google Cloud fuera de GCP
if "GRPC_VERBOSITY" not in os.environ:
    os.environ["GRPC_VERBOSITY"] = "ERROR"  # Solo mostrar errores, no warnings

# Verificar que GOOGLE_API_KEY esté configurada
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️ WARNING: GOOGLE_API_KEY no encontrada en variables de entorno")
    print("   Por favor, configura tu API key en el archivo .env")
else:
    print("✅ GOOGLE_API_KEY cargada correctamente")

# ==================== IMPORTS DE FASTAPI ====================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.load_from_url import router as load_from_url_router
from app.routers.ask import router as ask_router
from app.routers.health import router as health_router
from app.routers.validate_load import router as validate_load_router

# ==================== CONFIGURACIÓN DE LA APLICACIÓN ====================

# Instancia principal de FastAPI
app = FastAPI()

# Orígenes permitidos para CORS (desarrollo local)
# En desarrollo, permitir todos los orígenes para facilitar el testing
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://34.63.36.192",
    "http://34.63.36.192:80",
    "http://136.114.46.3:3000",
    "http://186.87.10.33:3000",
]

# Permitir todos los orígenes en desarrollo (para testing)
# NOTA: Si ALLOW_ALL_ORIGINS=True, no se puede usar allow_credentials=True
# En producción, usar solo ALLOWED_ORIGINS específicos
ALLOW_ALL_ORIGINS = os.getenv("ALLOW_ALL_ORIGINS", "true").lower() == "true"

# ==================== CONFIGURACIÓN DE MIDDLEWARE ====================

# Middleware CORS para permitir peticiones desde frontend
# Si se permite todo, no usar credentials (restricción del navegador)
if ALLOW_ALL_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # No compatible con allow_origins=["*"]
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,  # Solo con orígenes específicos
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# ==================== INTEGRACIÓN DE ROUTERS ====================

# Incluir todos los routers del sistema
app.include_router(load_from_url_router)
app.include_router(ask_router)
app.include_router(health_router)
app.include_router(validate_load_router)

# ==================== ENDPOINTS PRINCIPALES ====================

@app.get("/")
def read_root():
    """
    Endpoint raíz de la API.
    
    Proporciona un mensaje de bienvenida y confirma que la API
    está funcionando correctamente.
    
    Returns:
        dict: Mensaje de bienvenida con información básica
    """
    return {"message": "Bienvenido a la API de carga de documentos"}


@app.get("/api/v1/routes")
def list_routes():
    """
    Lista todas las rutas disponibles en la API.
    
    Útil para debugging y verificar qué endpoints están disponibles.
    
    Returns:
        dict: Lista de rutas con métodos HTTP y paths
    """
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = list(route.methods)
            if 'HEAD' in methods:
                methods.remove('HEAD')
            if 'OPTIONS' in methods:
                methods.remove('OPTIONS')
            routes.append({
                "path": route.path,
                "methods": methods,
                "name": getattr(route, 'name', 'N/A')
            })
    return {
        "total_routes": len(routes),
        "routes": routes
    }


# ==================== EVENTOS DE APLICACIÓN ====================

@app.on_event("startup")
async def startup_event():
    """
    Evento de inicio de la aplicación.
    
    Se ejecuta cuando la aplicación FastAPI se inicia y muestra
    información de debug sobre las rutas registradas y configuración CORS.
    """
    print("🚀 Servidor iniciado")
    print("🌐 Configuración CORS:")
    if ALLOW_ALL_ORIGINS:
        print("  ✅ Permitir todos los orígenes (ALLOW_ALL_ORIGINS=True)")
        print("  ⚠️  Credentials deshabilitadas (requerido para allow_origins=['*'])")
    else:
        print(f"  ✅ Orígenes permitidos: {', '.join(ALLOWED_ORIGINS)}")
        print("  ✅ Credentials habilitadas")
    print("📋 Rutas registradas:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"  {methods}: {route.path}")