"""
Modelos para el sistema de carga de documentos

Define las estructuras de datos para la carga, procesamiento y validación
de documentos desde URLs externas, incluyendo configuraciones y estadísticas.
"""

from pydantic import BaseModel, Field, HttpUrl, validator, ConfigDict
from typing import Optional, List, Dict, Any, Literal


class ChunkingConfig(BaseModel):
    """
    Configuración para la fragmentación de documentos.
    
    Define cómo se dividen los documentos en fragmentos más pequeños
    para optimizar la búsqueda y el procesamiento.
    """
    model_config = ConfigDict(extra="allow")
    
    chunk_size: Optional[int] = Field(1000, ge=100, le=5000)
    chunk_overlap: Optional[int] = Field(200, ge=0)
    chunking_strategy: Literal["recursive_character", "fixed_size", "semantic", "document_structure", "linguistic_units"] = Field("recursive_character")
    separators: Optional[List[str]] = Field(["\n\n", "\n", " ", ""])
    keep_separator: Optional[bool] = Field(True)
    strip_whitespace: Optional[bool] = Field(True)
    length_function: Optional[Literal["character_count", "token_count"]] = Field("character_count")

    @validator('chunk_overlap')
    def validate_chunk_overlap(cls, v, values):
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError('chunk_overlap debe ser menor que chunk_size')
        return v


class ProcessingOptions(BaseModel):
    """
    Opciones de procesamiento para documentos descargados.
    
    Controla qué tipos de archivos procesar y cómo manejarlos.
    """
    file_extensions: List[str] = Field(["pdf", "txt", "docx"])
    max_file_size_mb: int = Field(50, ge=1, le=1000)
    extract_metadata: bool = Field(True)
    preserve_formatting: bool = Field(False)
    timeout_per_file_seconds: int = Field(300, ge=30, le=3600)


class EmbeddingConfig(BaseModel):
    """
    Configuración para la generación de embeddings.
    
    Define el modelo y parámetros para crear representaciones vectoriales
    de los fragmentos de texto.
    
    Parámetros importantes:
    - model: Modelo de embeddings (default: "embedding-001" de Google AI)
    - batch_size: Chunks por batch (default: 90 para nivel gratuito)
                 Ajustar según límite de RPM de tu API key:
                 * Free Tier: 80-90 (límite 100 RPM)
                 * Nivel 1: hasta 1,500
                 * Nivel 2: hasta 2,000
    - retry_attempts: Intentos de reintento en caso de error
    """
    model: str = Field("embedding-001", description="Modelo de embeddings de Google AI")
    batch_size: int = Field(90, ge=1, le=1000, description="Chunks por batch (ajustar según RPM)")
    retry_attempts: int = Field(3, ge=1, le=10, description="Intentos de reintento")


class LoadFromUrlRequest(BaseModel):
    """
    Modelo principal para solicitudes de carga de documentos desde URL.
    
    Encapsula toda la configuración necesaria para descargar y procesar
    documentos de manera asíncrona. El sistema descarga automáticamente
    todos los documentos encontrados en la URL proporcionada.
    
    Atributos:
        source_url: URL donde se encuentran los documentos
        collection_name: Nombre identificador de la colección
        chunking_config: Configuración de fragmentación
        processing_options: Opciones de procesamiento (opcional)
        embedding_config: Configuración de embeddings (opcional)
    """
    source_url: HttpUrl = Field(..., description="URL donde se encuentran los documentos (carpeta o archivo individual)")
    collection_name: str = Field(..., min_length=1, description="Nombre de la colección")
    chunking_config: ChunkingConfig = Field(..., description="Configuración de fragmentación")
    processing_options: Optional[ProcessingOptions] = Field(ProcessingOptions())
    embedding_config: Optional[EmbeddingConfig] = Field(EmbeddingConfig())

    @validator('collection_name')
    def validate_collection_name(cls, v):
        import re
        v = v.strip()
        if not v:
            raise ValueError('collection_name no puede estar vacío')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('collection_name solo puede contener letras, números, guiones y guiones bajos')
        return v


class ProcessingSummary(BaseModel):
    """Resumen estadístico del procesamiento de documentos."""
    documents_found: int
    documents_loaded: int
    documents_failed: int
    total_chunks_created: int
    total_processing_time_seconds: float


class CollectionInfo(BaseModel):
    """Información sobre la colección de documentos."""
    name: str
    documents_count_before: int
    documents_count_after: int
    total_chunks_before: int
    total_chunks_after: int
    storage_size_mb: float


class DocumentMetadata(BaseModel):
    """Metadatos extraídos de documentos procesados."""
    pages: Optional[int] = None
    author: Optional[str] = None
    creation_date: Optional[str] = None
    file_type: str
    lines: Optional[int] = None
    encoding: Optional[str] = None


class ProcessedDocument(BaseModel):
    """Información detallada de un documento procesado exitosamente."""
    filename: str
    file_size_bytes: int
    download_url: str
    processing_status: str
    chunks_created: int
    processing_time_seconds: float
    metadata: DocumentMetadata


class FailedDocument(BaseModel):
    """Información sobre documentos que fallaron en el procesamiento."""
    filename: str
    download_url: str
    error_code: str
    error_message: str
    processing_time_seconds: float


class ChunkingStatistics(BaseModel):
    """Estadísticas sobre la fragmentación de documentos."""
    avg_chunk_size: float
    min_chunk_size: int
    max_chunk_size: int
    chunks_with_overlap: int
    total_characters_processed: int


class EmbeddingStatistics(BaseModel):
    """Estadísticas sobre la generación de embeddings."""
    model_config = {"protected_namespaces": ()}
    
    model_used: str
    total_embeddings_generated: int
    batch_processing_time_seconds: float
    embedding_dimensions: int
    failed_embeddings: int


class Warning(BaseModel):
    """Advertencias generadas durante el procesamiento."""
    code: str
    message: str
    affected_documents: List[str]
    recommendation: str


class ResponseData(BaseModel):
    """Datos completos de respuesta del procesamiento."""
    processing_summary: ProcessingSummary
    collection_info: CollectionInfo
    documents_processed: List[ProcessedDocument]
    failed_documents: List[FailedDocument]
    chunking_statistics: ChunkingStatistics
    embedding_statistics: EmbeddingStatistics


class LoadFromUrlResponse(BaseModel):
    """
    Respuesta completa del endpoint de carga de documentos.
    
    Incluye toda la información sobre el procesamiento realizado,
    estadísticas y posibles advertencias.
    """
    success: bool
    message: str
    data: ResponseData
    warnings: List[Warning]
    processing_id: str
    timestamp: str
