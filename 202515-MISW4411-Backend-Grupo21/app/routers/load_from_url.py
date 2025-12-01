"""
Módulo de carga de documentos desde URL

Este módulo maneja la descarga y procesamiento asíncrono de documentos desde URLs externas.
Incluye configuración avanzada para chunking, embeddings y procesamiento en background.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional, List, Dict, Any, Union
import datetime
import time
import os
import re
import uuid
import asyncio
import json
import httpx

from app.services.load_documents_service import download_and_process_documents
from app.models.load_documents import (
    LoadFromUrlRequest, 
    LoadFromUrlResponse, 
    ResponseData,
    ProcessingSummary,
    CollectionInfo,
    DocumentMetadata,
    ProcessedDocument,
    FailedDocument,
    ChunkingStatistics,
    EmbeddingStatistics,
    Warning
)

# Router para endpoints de documentos
router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

# Directorio de descarga configurado por variable de entorno
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./docs")




# ==================== FUNCIONES AUXILIARES ====================

def validate_url_accessibility(payload: LoadFromUrlRequest):
    """
    Valida que la URL fuente sea accesible.
    
    Realiza una petición HTTP simple para verificar que la URL
    responde antes de iniciar el procesamiento completo.
    
    Args:
        payload: Request con la URL a validar
    
    Raises:
        HTTPException: Si la URL no es accesible
    """
    timeout = 2
    try:
        httpx.get(str(payload.source_url), timeout=timeout)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "SOURCE_URL_NOT_FOUND",
                    "message": "URL no encontrada",
                    "details": {
                        "field": "source_url",
                        "source_url": str(payload.source_url),
                        "reason": "La URL no es accesible",
                        "provided_value": str(payload.source_url)
                    },
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        )
    

def validate_parameters(payload: LoadFromUrlRequest):
    """
    Valida los parámetros del request según especificaciones.
    
    Verifica que todos los parámetros estén dentro de rangos válidos
    y sean consistentes entre sí.
    
    Args:
        payload: Request a validar
    
    Raises:
        HTTPException: Si algún parámetro es inválido
    """
    
    # Ejemplo de validación. Los parámetros pueden variar entre estrategias de chunkeo
    if (payload.chunking_config.chunk_overlap < 0 or 
        payload.chunking_config.chunk_overlap >= payload.chunking_config.chunk_size):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Parámetros de request inválidos",
                    "details": {
                        "field": "chunk_overlap",
                        "reason": "El overlap del chunk debe ser mayor o igual a 0 y menor que el tamaño del chunk",
                        "provided_value": payload.chunking_config.chunk_overlap,
                        "chunk_size": payload.chunking_config.chunk_size
                    },
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        )

# ==================== PROCESAMIENTO ASÍNCRONO ====================

async def process_documents(payload: LoadFromUrlRequest, processing_id: str, timestamp: str):
    """
    Función asíncrona que maneja el procesamiento completo de documentos.
    
    Esta función se ejecuta en background y maneja todo el flujo:
    descarga, procesamiento, chunking, embeddings y almacenamiento de resultados.
    
    Args:
        payload: Configuración completa del procesamiento
        processing_id: Identificador único del procesamiento
        timestamp: Timestamp de inicio del procesamiento
    """
    
    print(f"Procesando en background: {processing_id}")
    start_time = time.time()

    # Validación adicional de esquema URL
    if payload.source_url.scheme not in ["http", "https"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "URL debe iniciar con http o https"}
            )
            
    try:
        # Llamada al servicio completo de descarga y procesamiento RAG
        result_json = await download_and_process_documents(
            url=str(payload.source_url),
            collection_name=payload.collection_name,
            timeout_per_file=payload.processing_options.timeout_per_file_seconds,
            payload=payload,
        )
        
        # Agregar metadatos del procesamiento
        if result_json.get("data") is not None:
            result_json["data"]["processing_id"] = processing_id
            result_json["data"]["timestamp"] = timestamp
        else:
            # Si data es None, crear estructura mínima con metadatos
            result_json["processing_id"] = processing_id
            result_json["timestamp"] = timestamp
        
        # Persistencia de resultados exitosos
        os.makedirs("./logs", exist_ok=True)
        with open(f"./logs/{processing_id}.json", "w") as f:
            json.dump(result_json, f, indent=4)
        
    except Exception as e:
        # Manejo de errores con logging
        result_json = {
            "success": False,
            "message": "Error al procesar documentos",
            "data": None,
            "warnings": [],
            "processing_id": processing_id,
            "timestamp": timestamp, 
            "error": str(e)
        }
        os.makedirs("./logs", exist_ok=True)
        with open(f"./logs/{processing_id}.json", "w") as f:
            json.dump(result_json, f, indent=4)


# ==================== ENDPOINT PRINCIPAL ====================

@router.post("/load-from-url")
async def load_from_url(payload: LoadFromUrlRequest):
    """
    Endpoint principal para carga de documentos desde URL externa.
    
    Procesa automáticamente TODOS los documentos encontrados en la URL proporcionada
    de manera asíncrona, aplicando configuraciones de chunking, embeddings y opciones
    de procesamiento. Ya no requiere especificar el número de documentos esperados.
    
    **Comportamiento automático:**
    - Si la URL apunta a una carpeta: descarga todos los documentos de la carpeta
    - Si la URL apunta a un archivo: descarga solo ese archivo
    - Maneja automáticamente el conteo y procesamiento de documentos
    
    Inicia el procesamiento en background y retorna inmediatamente
    un processing_id para tracking del progreso.
    
    **Flujo del endpoint:**
    1. Validación de accesibilidad de URL
    2. Validación de parámetros
    3. Generación de processing_id único
    4. Inicio de tarea asíncrona en background
    5. Retorno inmediato con ID de seguimiento
    
    Args:
        payload: Configuración completa del procesamiento (sin document_count)
    
    Returns:
        dict: Respuesta inmediata con processing_id para tracking
    """

    # Generación de identificadores únicos
    processing_id = f"proc_{uuid.uuid4().hex[:12]}"
    timestamp = datetime.datetime.now().isoformat()

    # Validaciones previas al procesamiento
    validate_url_accessibility(payload)
    validate_parameters(payload)
    
    # Inicio de procesamiento en background (fire-and-forget)
    asyncio.create_task(process_documents(payload, processing_id, timestamp))

    # Respuesta inmediata al cliente
    return {
        "success": True,
        "message": "Procesamiento iniciado en background",
        "processing_id": processing_id,
        "timestamp": timestamp
    }