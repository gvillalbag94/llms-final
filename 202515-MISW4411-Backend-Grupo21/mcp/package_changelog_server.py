"""
Servidor MCP Personalizado - Package Changelog
==============================================

Este servidor MCP expone herramientas para consultar changelogs y breaking changes
de paquetes Python desde PyPI y sus repositorios.
"""

from mcp.server.fastmcp import FastMCP
import requests
import json
from typing import Optional

# Inicializa el servidor MCP
mcp = FastMCP("package-changelog")

# Cache simple para evitar múltiples consultas
_cache = {}


def get_pypi_info(package_name: str) -> Optional[dict]:
    """
    Obtiene información de un paquete desde PyPI API.
    """
    cache_key = f"pypi_info_{package_name}"
    if cache_key in _cache:
        return _cache[cache_key]
    
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            _cache[cache_key] = data
            return data
        return None
    except Exception as e:
        print(f"Error consultando PyPI: {e}")
        return None


def get_release_notes(package_name: str, version: str) -> Optional[str]:
    """
    Intenta obtener release notes desde el repositorio del paquete.
    """
    try:
        # Primero intentamos obtener info de PyPI
        pypi_info = get_pypi_info(package_name)
        if not pypi_info:
            return None
        
        # Buscar en los campos de release
        releases = pypi_info.get("releases", {})
        if version in releases:
            release_info = releases[version]
            if release_info:
                # Buscar en los campos de información del proyecto
                info = pypi_info.get("info", {})
                
                # Intentar obtener desde GitHub/GitLab si está disponible
                project_urls = info.get("project_urls", {}) or {}
                homepage = info.get("home_page", "")
                repo_url = project_urls.get("Repository") or project_urls.get("Source") or homepage
                
                if repo_url and "github.com" in repo_url:
                    # Intentar obtener desde GitHub releases
                    try:
                        # Extraer owner/repo de la URL
                        parts = repo_url.replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
                        if "/" in parts:
                            owner, repo = parts.split("/")[:2]
                            github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/v{version}"
                            # También intentar sin 'v'
                            for tag_version in [f"v{version}", version]:
                                github_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag_version}"
                                gh_response = requests.get(github_api_url, timeout=5)
                                if gh_response.status_code == 200:
                                    release_data = gh_response.json()
                                    return release_data.get("body", "")
                    except:
                        pass
        
        return None
    except Exception as e:
        print(f"Error obteniendo release notes: {e}")
        return None


@mcp.tool()
def get_package_changelog(
    package_name: str,
    from_version: str,
    to_version: str,
    ecosystem: str = "pypi"
) -> str:
    """
    Obtiene el changelog y breaking changes entre dos versiones específicas
    de un paquete Python.
    
    Esta herramienta consulta PyPI y repositorios (GitHub) para obtener
    información sobre cambios, breaking changes, nuevas características
    y guías de migración entre versiones.
    
    Args:
        package_name: Nombre del paquete (ej: "Django", "requests", "flask")
        from_version: Versión actual del paquete
        to_version: Versión objetivo a la que se quiere actualizar
        ecosystem: Ecosistema del paquete (actualmente solo "pypi" soportado)
    
    Returns:
        str: Texto estructurado con información sobre:
        - Breaking changes identificados
        - Nuevas características
        - Bug fixes
        - Deprecations
        - Migration guide si está disponible
        - Información de versiones intermedias relevantes
    """
    try:
        # Validar ecosistema
        if ecosystem.lower() != "pypi":
            return f"Error: Actualmente solo se soporta el ecosistema 'pypi'. Se recibió: {ecosystem}"
        
        # Obtener información del paquete desde PyPI
        pypi_info = get_pypi_info(package_name)
        if not pypi_info:
            return f"No se pudo encontrar información del paquete '{package_name}' en PyPI. Verifica que el nombre sea correcto."
        
        info = pypi_info.get("info", {})
        releases = pypi_info.get("releases", {})
        
        # Verificar que las versiones existan
        if from_version not in releases:
            return f"Error: La versión '{from_version}' no se encontró en PyPI para el paquete '{package_name}'."
        
        if to_version not in releases:
            return f"Error: La versión '{to_version}' no se encontró en PyPI para el paquete '{package_name}'."
        
        # Construir respuesta con información disponible
        result_parts = []
        result_parts.append(f"📦 Changelog: {package_name} {from_version} → {to_version}\n")
        result_parts.append("=" * 60 + "\n")
        
        # Información básica del paquete
        summary = info.get("summary", "")
        if summary:
            result_parts.append(f"Descripción: {summary}\n")
        
        # Fechas de lanzamiento
        from_release = releases.get(from_version, [])
        to_release = releases.get(to_version, [])
        
        if from_release:
            from_date = from_release[0].get("upload_time", "")[:10] if from_release else "N/A"
            result_parts.append(f"Versión origen ({from_version}): Publicada el {from_date}\n")
        
        if to_release:
            to_date = to_release[0].get("upload_time", "")[:10] if to_release else "N/A"
            result_parts.append(f"Versión destino ({to_version}): Publicada el {to_date}\n")
        
        result_parts.append("\n")
        
        # Intentar obtener release notes desde GitHub
        release_notes = get_release_notes(package_name, to_version)
        if release_notes:
            result_parts.append("📝 Release Notes:\n")
            result_parts.append("-" * 60 + "\n")
            result_parts.append(release_notes)
            result_parts.append("\n\n")
        
        # Información de versiones intermedias relevantes
        all_versions = sorted(releases.keys(), reverse=True)
        from_idx = all_versions.index(from_version) if from_version in all_versions else -1
        to_idx = all_versions.index(to_version) if to_version in all_versions else -1
        
        if from_idx >= 0 and to_idx >= 0:
            if from_idx > to_idx:  # Actualización hacia adelante
                intermediate_versions = all_versions[to_idx:from_idx]
                if len(intermediate_versions) > 1:
                    result_parts.append(f"⚠️  Nota: Hay {len(intermediate_versions) - 1} versión(es) intermedia(s) entre {from_version} y {to_version}.\n")
                    result_parts.append("Se recomienda revisar los changelogs de cada versión intermedia.\n\n")
        
        # Información de URLs útiles
        project_urls = info.get("project_urls", {}) or {}
        homepage = info.get("home_page", "")
        docs_url = project_urls.get("Documentation") or project_urls.get("Docs") or ""
        
        result_parts.append("🔗 Recursos adicionales:\n")
        if homepage:
            result_parts.append(f"  - Homepage: {homepage}\n")
        if docs_url:
            result_parts.append(f"  - Documentación: {docs_url}\n")
        
        # Buscar migration guide en project_urls
        for key, url in project_urls.items():
            if "migration" in key.lower() or "changelog" in key.lower() or "release" in key.lower():
                result_parts.append(f"  - {key}: {url}\n")
        
        # Advertencia sobre breaking changes
        result_parts.append("\n⚠️  IMPORTANTE:\n")
        result_parts.append("Esta herramienta proporciona información disponible públicamente.\n")
        result_parts.append("Para identificar breaking changes específicos, se recomienda:\n")
        result_parts.append("1. Revisar el changelog oficial del paquete\n")
        result_parts.append("2. Consultar la documentación de migración si está disponible\n")
        result_parts.append("3. Ejecutar tests exhaustivos después de la actualización\n")
        result_parts.append("4. Verificar dependencias compatibles\n")
        
        return "".join(result_parts)
    
    except Exception as e:
        return f"Error al obtener changelog: {str(e)}. Verifica que los nombres de paquete y versiones sean correctos."


@mcp.tool()
def get_package_info(package_name: str, ecosystem: str = "pypi") -> str:
    """
    Obtiene información general sobre un paquete, incluyendo versiones disponibles,
    descripción y enlaces útiles.
    
    Args:
        package_name: Nombre del paquete
        ecosystem: Ecosistema del paquete (actualmente solo "pypi")
    
    Returns:
        str: Información estructurada del paquete
    """
    try:
        if ecosystem.lower() != "pypi":
            return f"Error: Actualmente solo se soporta el ecosistema 'pypi'."
        
        pypi_info = get_pypi_info(package_name)
        if not pypi_info:
            return f"No se pudo encontrar el paquete '{package_name}' en PyPI."
        
        info = pypi_info.get("info", {})
        releases = pypi_info.get("releases", {})
        
        result_parts = []
        result_parts.append(f"📦 Información del paquete: {package_name}\n")
        result_parts.append("=" * 60 + "\n")
        
        # Información básica
        if info.get("summary"):
            result_parts.append(f"Descripción: {info['summary']}\n")
        
        if info.get("author"):
            result_parts.append(f"Autor: {info['author']}\n")
        
        # Versiones disponibles
        all_versions = sorted(releases.keys(), reverse=True)
        latest_version = all_versions[0] if all_versions else "N/A"
        result_parts.append(f"\nÚltima versión: {latest_version}\n")
        result_parts.append(f"Total de versiones disponibles: {len(all_versions)}\n")
        
        # Mostrar últimas 10 versiones
        if len(all_versions) > 0:
            result_parts.append(f"\nÚltimas 10 versiones:\n")
            for v in all_versions[:10]:
                release_data = releases.get(v, [])
                date = release_data[0].get("upload_time", "")[:10] if release_data else "N/A"
                result_parts.append(f"  - {v} (publicada: {date})\n")
        
        # URLs útiles
        project_urls = info.get("project_urls", {}) or {}
        homepage = info.get("home_page", "")
        
        if homepage or project_urls:
            result_parts.append("\n🔗 Enlaces:\n")
            if homepage:
                result_parts.append(f"  - Homepage: {homepage}\n")
            for key, url in project_urls.items():
                result_parts.append(f"  - {key}: {url}\n")
        
        return "".join(result_parts)
    
    except Exception as e:
        return f"Error al obtener información del paquete: {str(e)}"


# Ejecución del servidor MCP
if __name__ == "__main__":
    mcp.run(transport="stdio")

