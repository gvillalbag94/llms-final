"""
Servicio de descarga y procesamiento de documentos

Este módulo orquesta la descarga de documentos desde diferentes proveedores
de almacenamiento (Google Drive, etc.) y los organiza en colecciones locales.
Además, procesa los documentos para crear la base de datos vectorial RAG.
"""

import os
import time
import logging
from typing import Tuple, List, Dict, Any
from pathlib import Path
from app.services.google_drive import GoogleDriveProvider

logger = logging.getLogger(__name__)

# Directorio base para descargas configurado por variable de entorno
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./docs")


async def download_documents(
        url: str, 
        collection_name: str, 
        timeout_per_file: int = 300,
        credentials_path: str = "apikey.json",
        payload: Any = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Descarga documentos desde una URL a una colección local.
        
        Coordina la descarga de documentos usando el proveedor apropiado 
        (actualmente solo Google Drive) y los organiza en una colección local.
        
        **Tipos de URL soportadas:**
        - Carpeta de Google Drive: descarga todos los documentos de la carpeta
        - Archivo individual de Google Drive: descarga ese único archivo
        
        **Flujo de descarga:**
        1. Creación del directorio de colección
        2. Inicialización del proveedor de almacenamiento
        3. Listado de documentos disponibles (carpeta completa o archivo único)
        4. Descarga de todos los documentos encontrados
        5. Manejo individual de errores por documento
        6. Retorno de listas de éxitos y fallos
        
        Args:
            url: URL fuente (formatos soportados):
                - Carpeta: https://drive.google.com/drive/folders/FOLDER_ID
                - Archivo: https://drive.google.com/file/d/FILE_ID/view
            collection_name: Nombre de la colección destino
            timeout_per_file: Timeout por archivo en segundos (default: 300)
            credentials_path: Ruta al archivo de credenciales (default: "apikey.json")
            payload: Configuración de procesamiento para validación
        
        Returns:
            Tuple[List, List]: (documentos_exitosos, documentos_fallidos)
                - documentos_exitosos: Lista con metadatos de descargas exitosas
                - documentos_fallidos: Lista con información de errores
        """
        # === CONFIGURACIÓN DE DIRECTORIO ===
        collection_dir = os.path.join(DOWNLOAD_DIR, collection_name)
        os.makedirs(collection_dir, exist_ok=True)
        
        # === INICIALIZACIÓN DEL PROVEEDOR ===
        # Para este esqueleto solo se implementa Google Drive
        provider = GoogleDriveProvider(url, credentials_path)
        documents = provider.list_documents()
        
        # === INFORMACIÓN DE DOCUMENTOS ENCONTRADOS ===
        print(f"Documentos encontrados: {len(documents)}")
        
        # === INICIALIZACIÓN DE LISTAS DE RESULTADOS ===
        processed_docs = []
        failed_docs = []
        
        # === PROCESAMIENTO INDIVIDUAL DE DOCUMENTOS ===
        for doc in documents:
            doc_start_time = time.time()
            output_path = os.path.join(collection_dir, doc["name"])
            
            # Determinar URL de descarga apropiada
            # Si la URL original ya apunta a un archivo específico, usar esa
            # Si es una carpeta, agregar el nombre del archivo
            if "/file/d/" in url:
                doc_download_url = url  # URL de archivo individual
            else:
                doc_download_url = f"{url}/{doc['name']}"  # URL de carpeta + archivo
            
            try:
                print(f"Descargando: {doc['name']}")
                
                # Descarga usando el proveedor configurado
                download_result = provider.download_document(
                    doc["id"], 
                    output_path, 
                    timeout_seconds=timeout_per_file,
                    payload=payload
                )
                
                # === MANEJO DE RESULTADO DE DESCARGA ===
                if download_result == "":  # Descarga exitosa
                    file_stats = os.stat(output_path)
                    processed_docs.append({
                        "filename": doc["name"],
                        "file_path": output_path,
                        "file_size_bytes": file_stats.st_size,
                        "download_url": doc_download_url,
                        "processing_time_seconds": round(time.time() - doc_start_time, 2),
                        "doc_metadata": doc
                    })
                    print(f"Descargado: {doc['name']} ({file_stats.st_size} bytes)")
                else:
                    # Descarga fallida con información de error
                    failed_docs.append({
                        "filename": doc["name"],
                        "download_url": doc_download_url,
                        "error_message": str(download_result),
                        "processing_time_seconds": round(time.time() - doc_start_time, 2)
                    })
                    print(f"Error: {doc['name']} - {download_result}")
                    
            except Exception as e:
                # === MANEJO DE EXCEPCIONES ===
                failed_docs.append({
                    "filename": doc["name"],
                    "download_url": doc_download_url,
                    "error_message": str(e),
                    "processing_time_seconds": round(time.time() - doc_start_time, 2)
                })
                print(f"Excepción: {doc['name']} - {e}")
        
        # === RETORNO DE RESULTADOS ===
        return processed_docs, failed_docs


async def download_and_process_documents(
        url: str, 
        collection_name: str, 
        timeout_per_file: int = 300,
        credentials_path: str = "apikey.json",
        payload: Any = None
    ) -> Dict[str, Any]:
        """
        Descarga documentos y procesa completamente para RAG.
        
        Esta función orquesta todo el proceso:
        1. Descarga documentos
        2. Procesamiento de chunks con ChunkingService
        3. Generación de embeddings con EmbeddingService
        4. Creación de base de datos vectorial con RetrievalService
        
        Args:
            url: URL fuente de los documentos
            collection_name: Nombre de la colección destino
            timeout_per_file: Timeout por archivo en segundos
            credentials_path: Ruta al archivo de credenciales
            payload: Configuración de procesamiento (chunk_size, overlap, etc.)
        
        Returns:
            Dict con resultados completos del procesamiento
        """
        start_time = time.time()
        
        logger.info(f"Iniciando descarga y procesamiento RAG para colección: {collection_name}")
        
        # === STEP 1: DESCARGA DE DOCUMENTOS ===
        try:
            processed_docs, failed_docs = await download_documents(
                url=url,
                collection_name=collection_name,
                timeout_per_file=timeout_per_file,
                credentials_path=credentials_path,
                payload=payload
            )
            
            logger.info(f"Descarga completada. Exitosos: {len(processed_docs)}, Fallidos: {len(failed_docs)}")
            
        except Exception as e:
            logger.error(f"Error en descarga de documentos: {str(e)}")
            return {
                "success": False,
                "message": f"Error en descarga: {str(e)}",
                "data": None,
                "processing_time_sec": round(time.time() - start_time, 3)
            }
        
        # === STEP 2: PROCESAMIENTO RAG ===
        rag_success = False
        rag_error = None
        chunking_stats = {}
        embedding_stats = {}
        total_chunks = 0
        
        if processed_docs:  # Solo si hay documentos exitosamente descargados
            try:
                logger.info("Iniciando procesamiento RAG...")
                
                # Importar servicios RAG
                from app.services.chunking_service import ChunkingService, ChunkingStrategy
                from app.services.embedding_service import EmbeddingService
                from app.services.retrieval_service import RetrievalService
                
                # Configurar parámetros de chunking desde payload (optimizado para cuota limitada)
                chunk_size = 2000  # Chunks más grandes = menos embeddings requeridos
                chunk_overlap = 100  # Menos overlap para reducir total de chunks
                chunking_strategy = ChunkingStrategy.RECURSIVE_CHARACTER
                
                if payload and hasattr(payload, 'chunking_config'):
                    chunk_size = payload.chunking_config.chunk_size
                    chunk_overlap = payload.chunking_config.chunk_overlap
                    # Mapear el string de estrategia al enum
                    strategy_map = {
                        "recursive_character": ChunkingStrategy.RECURSIVE_CHARACTER,
                        "fixed_size": ChunkingStrategy.FIXED_SIZE,
                        "semantic": ChunkingStrategy.SEMANTIC,
                        "document_structure": ChunkingStrategy.DOCUMENT_STRUCTURE,
                        "linguistic_units": ChunkingStrategy.LINGUISTIC_UNITS
                    }
                    chunking_strategy = strategy_map.get(
                        payload.chunking_config.chunking_strategy, 
                        ChunkingStrategy.RECURSIVE_CHARACTER
                    )
                
                # Configurar modelo de embeddings desde payload
                embedding_model = "models/embedding-001"  # Default
                batch_size = 90  # Default para nivel gratuito de Google AI (100 RPM)
                
                if payload and hasattr(payload, 'embedding_config') and payload.embedding_config:
                    # Si el usuario especifica un modelo en embedding_config, usarlo
                    if hasattr(payload.embedding_config, 'model') and payload.embedding_config.model:
                        # Mapear modelos comunes a formato de Google
                        if "embedding" in payload.embedding_config.model.lower():
                            embedding_model = f"models/{payload.embedding_config.model}"
                        else:
                            embedding_model = "models/embedding-001"
                    
                    # Leer batch_size desde el payload
                    if hasattr(payload.embedding_config, 'batch_size') and payload.embedding_config.batch_size:
                        batch_size = payload.embedding_config.batch_size
                        logger.info(f"Batch size configurado desde frontend: {batch_size}")
                
                # Inicializar servicios
                chunking_service = ChunkingService(
                    strategy=chunking_strategy,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                embedding_service = EmbeddingService(model=embedding_model)
                
                logger.info(f"Procesando documentos con chunk_size={chunk_size}, overlap={chunk_overlap}, batch_size={batch_size}")
                
                # === CHUNKING ===
                chunks = chunking_service.process_collection(collection_name)
                total_chunks = len(chunks)
                
                logger.info(f"Chunking completado: {total_chunks} chunks generados")
                
                if chunks:
                    # Crear estadísticas de chunking
                    chunking_stats = chunking_service.get_chunking_statistics(chunks)
                    
                    # === VECTOR STORE CREATION ===
                    # RetrievalService es responsable de crear el vector store con embeddings
                    # Los estudiantes pueden usar ChromaDB, PgVector, u otra base vectorial
                    logger.info("Creando base de datos vectorial con embeddings...")
                    
                    # Inicializar servicio de retrieval
                    retrieval_service = RetrievalService()
                    
                    vector_success, embedding_stats = retrieval_service.create_vector_store(
                        documents=chunks,
                        collection_name=collection_name,
                        force_rebuild=True,
                        embedding_service=embedding_service,
                        batch_size=batch_size
                    )
                    
                    if vector_success:
                        rag_success = True
                        embedding_stats.update({
                            "vector_store_created": True
                        })
                        logger.info(f"Base de datos vectorial creada exitosamente: {total_chunks} embeddings")
                    else:
                        rag_error = "Error creando vector store"
                        logger.error(rag_error)
                        
                else:
                    rag_error = "No se pudieron procesar documentos para chunking"
                    logger.warning(rag_error)
                    
            except Exception as e:
                rag_error = f"Error en procesamiento RAG: {str(e)}"
                logger.error(rag_error)
        
        # === STEP 3: CALCULAR ESTADÍSTICAS ADICIONALES ===
        collection_path = f"./docs/{collection_name}"
        storage_size = 0
        if os.path.exists(collection_path):
            for root, dirs, files in os.walk(collection_path):
                for file in files:
                    storage_size += os.path.getsize(os.path.join(root, file))
        storage_size_mb = round(storage_size / (1024 * 1024), 2)
        
        # === STEP 4: COMPILAR RESULTADOS ===
        warnings = []
        if not rag_success and rag_error:
            warnings.append(f"RAG Warning: {rag_error}")
        
        processing_time = round(time.time() - start_time, 3)
        
        result = {
            "success": True,
            "message": "Documentos descargados y procesados exitosamente",
            "data": {
                "processing_summary": {
                    "rag_processing": rag_success,
                    "vector_store_created": rag_success,
                    "total_processing_time_sec": processing_time
                },
                "collection_info": {
                    "name": collection_name,
                    "documents_found": len(processed_docs) + len(failed_docs),
                    "documents_processed_successfully": len(processed_docs),
                    "documents_failed": len(failed_docs),
                    "documents_count_before": 0,
                    "documents_count_after": len(processed_docs),
                    "total_chunks_before": 0,
                    "total_chunks_after": total_chunks,
                    "storage_size_mb": storage_size_mb
                },
                "documents_processed": processed_docs,
                "failed_documents": failed_docs,
                "chunking_statistics": chunking_stats,
                "embedding_statistics": embedding_stats,
                "warnings": warnings
            }
        }
        
        logger.info(f"Procesamiento completo finalizado en {processing_time}s. RAG: {rag_success}")
        
        return result


async def validate_processing_with_rag(processing_id: str) -> Dict[str, Any]:
    """
    Valida el procesamiento y agrega información de estado RAG.
    
    Esta función lee el archivo de log del procesamiento y agrega
    información actualizada sobre el estado de la base de datos vectorial.
    
    Args:
        processing_id: Identificador único del procesamiento
    
    Returns:
        Datos completos del procesamiento con estado RAG actualizado
    
    Raises:
        FileNotFoundError: Si el processing_id no existe
        ValueError: Si el archivo JSON está corrupto
    """
    import json
    from pathlib import Path
    
    LOG_DIR = os.getenv("LOG_DIR", "./logs")
    log_dir = Path(LOG_DIR)
    
    # Leer archivo de log
    file_path = log_dir / f"{processing_id}.json"
    
    if not file_path.exists():
        raise FileNotFoundError(f"No existe {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        data = json.loads(content)
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Archivo JSON corrupto: {e}")
    
    # Agregar información de estado RAG si el procesamiento fue exitoso
    if data.get("success") and data.get("data"):
        collection_name = data["data"].get("collection_info", {}).get("name")
        
        if collection_name:
            logger.info(f"Agregando estado RAG actualizado para colección: {collection_name}")
            
            # Obtener estado RAG actualizado
            rag_status = get_rag_status(collection_name)
            
            # Agregar información RAG a la respuesta
            if "rag_status" not in data["data"]:
                data["data"]["rag_status"] = {}
            
            data["data"]["rag_status"].update(rag_status)
            
            # Agregar timestamp de validación
            data["data"]["rag_status"]["validated_at"] = time.time()
    
    return data


def get_rag_status(collection_name: str) -> Dict[str, Any]:
    """
    Obtiene el estado actual de la base de datos vectorial RAG.
    
    Args:
        collection_name: Nombre de la colección a verificar
    
    Returns:
        Diccionario con el estado RAG completo
    """
    try:
        # Importar servicio de retrieval
        from app.services.retrieval_service import RetrievalService
        
        retrieval_service = RetrievalService()
        
        # Obtener información de la colección RAG
        collection_info = retrieval_service.get_collection_info(collection_name)
        vector_store_exists = collection_info.get("exists", False)
        
        # Verificar documentos en la carpeta docs
        docs_path = f"./docs/{collection_name}"
        pdf_count = 0
        pdf_files = []
        
        if os.path.exists(docs_path):
            pdf_files = [f for f in os.listdir(docs_path) if f.endswith('.pdf')]
            pdf_count = len(pdf_files)
        
        # Verificar si el vector store está listo
        # El path específico depende de la implementación del estudiante (ChromaDB, PgVector, etc.)
        vector_store_path = collection_info.get("path", "")
        vector_store_ready = vector_store_exists and os.path.exists(vector_store_path) if vector_store_path else vector_store_exists
        
        rag_status = {
            "vector_store_exists": vector_store_exists,
            "vector_store_ready": vector_store_ready,
            "collection_name": collection_name,
            "vector_store_path": vector_store_path,
            "rag_ready": vector_store_ready,
            "document_count": collection_info.get("document_count", 0) if vector_store_exists else 0,
            "documents_in_collection": pdf_count,
            "pdf_files": pdf_files[:10]  # Limitar a primeros 10 para no saturar response
        }
        
        logger.info(f"Estado RAG para '{collection_name}': ready={rag_status['rag_ready']}, "
                   f"docs={pdf_count}, embeddings={rag_status['document_count']}")
        
        return rag_status
        
    except Exception as e:
        logger.error(f"Error verificando estado RAG: {str(e)}")
        return {
            "error": f"Error verificando estado RAG: {str(e)}",
            "vector_store_exists": False,
            "rag_ready": False,
            "collection_name": collection_name
        }
    