"""
Modelos Pydantic para la aplicación RAG

Este módulo centraliza todas las clases de modelos de datos utilizadas 
en los routers y servicios de la aplicación.
"""

# Importar todos los modelos para acceso fácil
from .ask import AskRequest, AskResponse, FuenteContexto
from .load_documents import (
    ChunkingConfig, 
    ProcessingOptions, 
    EmbeddingConfig,
    LoadFromUrlRequest,
    CollectionInfo,
    DocumentMetadata,
    ProcessedDocument,
    FailedDocument,
    ChunkingStatistics,
    EmbeddingStatistics,
    Warning,
    ResponseData,
    ProcessingSummary
)

__all__ = [
    # Ask models
    "AskRequest",
    "AskResponse", 
    "FuenteContexto",
    
    # Load documents models
    "ChunkingConfig",
    "ProcessingOptions",
    "EmbeddingConfig", 
    "LoadFromUrlRequest",
    "CollectionInfo",
    "DocumentMetadata",
    "ProcessedDocument",
    "FailedDocument",
    "ChunkingStatistics",
    "EmbeddingStatistics",
    "Warning",
    "ResponseData",
    "ProcessingSummary"
]
