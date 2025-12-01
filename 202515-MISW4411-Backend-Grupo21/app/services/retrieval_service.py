"""
Servicio de Retrieval para el Sistema RAG
==========================================

Este módulo implementa la funcionalidad de almacenamiento y recuperación de documentos
usando una base de datos vectorial ChromaDB.

TAREAS SEMANA 2:
- Crear vector store con ChromaDB
- Implementar similarity_search para recuperar documentos relevantes
- Opcionalmente: crear retrievers configurables

TAREAS SEMANA 3:
- Implementar reranking de documentos recuperados (método rerank_documents)
- El reranking mejora la relevancia de los documentos usando modelos cross-encoder

TUTORIALES:
- RAG paso a paso, parte 2: embeddings y base de datos vectorial
- RAG paso a paso, parte 3: recuperación y generación de respuestas
- Reranking con LangChain
"""

import os
import shutil
import time
from typing import List, Dict, Any, Tuple, Optional

# Configurar GitPython antes de importar sentence-transformers
# Esto evita errores cuando Git no está disponible (no es necesario para descargar modelos)
if "GIT_PYTHON_REFRESH" not in os.environ:
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"

from langchain_core.documents import Document
from langchain_chroma import Chroma
from app.services.embedding_service import EmbeddingService

# Imports para reranking (Semana 3)
try:
    from sentence_transformers import CrossEncoder
    RERANKING_AVAILABLE = True
except ImportError:
    RERANKING_AVAILABLE = False
    print("⚠️ sentence-transformers no disponible. Reranking deshabilitado.")


class RetrievalService:
    """
    Servicio para almacenar y recuperar documentos usando ChromaDB.
    
    IMPLEMENTACIÓN REQUERIDA (SEMANA 2):
    - __init__: Inicializar el servicio
    - create_vector_store: Crear base de datos vectorial con chunks
    - get_vector_store: Obtener un vector store existente
    - similarity_search: Buscar documentos similares a una consulta
    
    IMPLEMENTACIÓN REQUERIDA (SEMANA 3):
    - rerank_documents: Reordenar documentos por relevancia usando cross-encoder
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Inicializa el servicio de retrieval.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Guardar persist_directory
        - Inicializar cache de vector stores (diccionario)
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 3:
        - Inicializar modelo de reranking bajo demanda (lazy loading)
        
        Args:
            persist_directory: Directorio donde se almacenará ChromaDB
        """
        self.persist_directory = persist_directory
        self.vector_stores_cache = {}  # Cache para vector stores existentes
        self.reranker_model = None  # Se inicializa bajo demanda
            
    def create_vector_store(
        self,
        documents: List[Document],
        collection_name: str,
        force_rebuild: bool = True,
        embedding_service: EmbeddingService = None,
        batch_size: int = 90
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Crea una base de datos vectorial ChromaDB con los documentos proporcionados.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Obtener el modelo de embeddings desde embedding_service
        - Si force_rebuild, eliminar colección anterior
        - Crear Chroma vector store con:
          * collection_name
          * embedding_function (del embedding_service)
          * persist_directory específico para la colección
        - Extraer texts, metadatas e ids de los documentos
        - Agregar documents al vector store con add_texts()
        - Guardar en cache
        - Retornar (True, embedding_stats) si éxito, (False, error_dict) si falla
        
        IMPORTANTE - RATE LIMITING:
        - Google AI Free Tier: 100 requests/minuto
        - Procesar en batches de ~90 chunks
        - Esperar 65 segundos entre batches
        - Ver documentación adicional sobre límites de cuota
        
        Args:
            documents: Lista de chunks a almacenar
            collection_name: Nombre de la colección
            force_rebuild: Si True, elimina la colección existente
            embedding_service: Servicio de embeddings
            batch_size: Chunks por batch (default: 90 para free tier)
            
        Returns:
            Tuple[bool, Dict]: (éxito, estadísticas_o_error)
        """
        try:
            
            # Validar entrada
            if not documents:
                return False, {"error": "No se proporcionaron documentos para procesar"}
            
            if not embedding_service:
                return False, {"error": "EmbeddingService es requerido"}
            
            # Obtener el modelo de embeddings
            embeddings_model = embedding_service.get_embeddings_model()
            
            # Directorio específico para esta colección
            collection_directory = os.path.join(self.persist_directory, collection_name)
            
            # Si force_rebuild, eliminar colección anterior
            if force_rebuild and os.path.exists(collection_directory):
                shutil.rmtree(collection_directory)
            
            # Crear directorio si no existe
            os.makedirs(collection_directory, exist_ok=True)
            
            # Crear Chroma vector store
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings_model,
                persist_directory=collection_directory
            )
            
            # Extraer datos de los documentos
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            ids = [f"{doc.metadata.get('source_file', 'doc')}_{i}" for i, doc in enumerate(documents)]
            
            
            # Procesar en batches para respetar rate limits
            total_batches = (len(texts) + batch_size - 1) // batch_size
            print(f"🔄 Procesando en {total_batches} batches de máximo {batch_size} documentos")
            
            for batch_idx in range(0, len(texts), batch_size):
                batch_texts = texts[batch_idx:batch_idx + batch_size]
                batch_metadatas = metadatas[batch_idx:batch_idx + batch_size]
                batch_ids = ids[batch_idx:batch_idx + batch_size]
                
                batch_num = (batch_idx // batch_size) + 1
                
                # Agregar batch al vector store
                vector_store.add_texts(
                    texts=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                
                # Esperar entre batches para respetar rate limits (excepto en el último batch)
                if batch_num < total_batches:
                    print(f"   ⏳ Esperando 65 segundos para respetar rate limits...")
                    time.sleep(65)
            
            # Guardar en cache
            self.vector_stores_cache[collection_name] = vector_store
            
            # Estadísticas de éxito
            stats = {
                "collection_name": collection_name,
                "total_documents": len(documents),
                "total_batches": total_batches,
                "batch_size": batch_size,
                "persist_directory": collection_directory,
                "unique_sources": len(set(doc.metadata.get('source_file', 'unknown') for doc in documents)),
                "avg_chunk_size": sum(len(text) for text in texts) // len(texts),
                "total_characters": sum(len(text) for text in texts)
            }
            
            return True, stats
            
        except Exception as e:
            import traceback
            error_msg = f"Error creando vector store: {str(e)}"
            error_traceback = traceback.format_exc()
            print(f"❌ {error_msg}")
            print(f"Traceback completo:\n{error_traceback}")
            return False, {"error": error_msg, "traceback": error_traceback}
    
    def get_vector_store(
        self, 
        collection_name: str, 
        embedding_service: EmbeddingService = None
    ) -> Optional[Chroma]:
        """
        Obtiene un vector store existente.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Verificar cache primero
        - Si no está en cache, verificar si existe en disco
        - Si existe, cargar con Chroma() y guardar en cache
        - Retornar vector store o None
        
        Args:
            collection_name: Nombre de la colección
            embedding_service: Servicio de embeddings
            
        Returns:
            Instancia de Chroma o None si no existe
        """
        try:
            # Verificar cache primero
            if collection_name in self.vector_stores_cache:
                return self.vector_stores_cache[collection_name]
            
            # Verificar si existe en disco
            collection_directory = os.path.join(self.persist_directory, collection_name)
            
            if not os.path.exists(collection_directory):
                return None
            
            # Verificar que hay archivos de ChromaDB
            chroma_files = [f for f in os.listdir(collection_directory) if f.endswith('.parquet') or f.endswith('.sqlite3')]
            if not chroma_files:
                return None
            
            # Cargar vector store desde disco
            if not embedding_service:
                return None
            
            embeddings_model = embedding_service.get_embeddings_model()
            
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings_model,
                persist_directory=collection_directory
            )
            
            # Guardar en cache
            self.vector_stores_cache[collection_name] = vector_store
            
            return vector_store
            
        except Exception as e:
            return None
    
    def similarity_search(
        self, 
        query: str, 
        collection_name: str = "default",
        k: int = 3,
        embedding_service: EmbeddingService = None
    ) -> List[Document]:
        """
        Busca documentos similares a la consulta.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Obtener vector_store con get_vector_store()
        - Usar vector_store.similarity_search(query, k=k)
        - Retornar lista de documentos relevantes
        
        NOTA: Este método es llamado por ask.py para recuperar contexto
        
        Args:
            query: Consulta del usuario
            collection_name: Nombre de la colección
            k: Número de documentos a recuperar
            embedding_service: Servicio de embeddings
            
        Returns:
            Lista de documentos relevantes (objetos Document)
        """
        try:
            
            # Obtener vector store
            vector_store = self.get_vector_store(collection_name, embedding_service)
            
            if not vector_store:
                return []
            
            # Realizar búsqueda semántica
            results = vector_store.similarity_search(query, k=k)
            
            
            # Mostrar preview de resultados
            for i, doc in enumerate(results):
                source_file = doc.metadata.get('source_file', 'unknown')
                preview = doc.page_content[:100].replace('\n', ' ')
                print(f"   {i+1}. {source_file}: '{preview}...'")
            
            return results
            
        except Exception as e:
            return []
    
    def test_vector_store(
        self, 
        collection_name: str = "default",
        queries: List[str] = None,
        embedding_service: EmbeddingService = None
    ) -> Dict[str, Any]:
        """
        Realiza consultas de prueba sobre una colección vectorial para verificar su funcionalidad.
        
        MÉTODO ADICIONAL SEMANA 2:
        - Ejecuta búsquedas semánticas de prueba
        - Muestra resultados para validación
        - Útil para debugging y verificación del sistema
        
        Args:
            collection_name: Nombre de la colección a probar
            queries: Lista de consultas de prueba (opcional)
            embedding_service: Servicio de embeddings
            
        Returns:
            Diccionario con resultados de las pruebas
        """
        if queries is None:
            queries = [
                "¿Qué es la inteligencia artificial?",
                "¿Cómo funciona el machine learning?",
                "¿Qué son las APIs REST?",
                "¿Cómo funciona JWT?"
            ]
        
        results = {}
        
        for i, query in enumerate(queries):
            
            # Realizar búsqueda
            docs = self.similarity_search(
                query=query,
                collection_name=collection_name,
                k=3,
                embedding_service=embedding_service
            )
            
            if docs:
                results[query] = []
                for j, doc in enumerate(docs):
                    source_file = doc.metadata.get('source_file', 'unknown')
                    preview = doc.page_content[:150].replace('\n', ' ')
                    
                    result_info = {
                        "rank": j + 1,
                        "source_file": source_file,
                        "preview": preview,
                        "chunk_size": len(doc.page_content),
                        "metadata": doc.metadata
                    }
                    results[query].append(result_info)
                    
                    print(f"   {j+1}. {source_file}: '{preview}...'")
            else:
                results[query] = []
        
        
        return results
    
    def rerank_documents(
        self, 
        query: str, 
        documents: List[Document], 
        top_n: int = 5
    ) -> List[Document]:
        """
        Reordena documentos recuperados usando un modelo de reranking.
        
        Implementación SEMANA 3:
        - Usa CrossEncoder de sentence-transformers para calcular relevancia
        - Crea pares (query, doc.page_content) para cada documento
        - Calcula scores de relevancia con el modelo
        - Ordena documentos por score (descendente)
        - Añade 'rerank_score' a doc.metadata de cada documento
        - Retorna top_n documentos reordenados
        
        Modelo utilizado:
        - cross-encoder/ms-marco-MiniLM-L-6-v2 (modelo cross-encoder especializado en reranking)
        
        NOTA: Este método es llamado por ask.py después de similarity_search
        cuando el parámetro use_reranking=True
        
        Args:
            query: Consulta del usuario
            documents: Lista de documentos del similarity_search
            top_n: Número de documentos a retornar
            
        Returns:
            List[Document]: Documentos reordenados con 'rerank_score' en metadata
        """
        # Si reranking no está disponible, retornar sin reordenar
        if not RERANKING_AVAILABLE or not documents:
            # Simular scores de 0.5 para documentos sin reranking disponible
            for doc in documents:
                if "rerank_score" not in doc.metadata:
                    doc.metadata["rerank_score"] = 0.5
            return documents[:top_n]
        
        try:
            # Inicializar el modelo bajo demanda (lazy loading)
            if self.reranker_model is None:
                print("📊 Inicializando modelo de reranking...")
                try:
                    # Intentar cargar el modelo con timeout implícito
                    self.reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
                    print("✅ Modelo de reranking inicializado")
                except Exception as init_error:
                    print(f"⚠️ Error inicializando modelo de reranking: {str(init_error)}")
                    print("⚠️ Retornando documentos sin reordenar debido a error de inicialización")
                    # Si falla la inicialización, retornar sin reordenar
                    for doc in documents:
                        if "rerank_score" not in doc.metadata:
                            doc.metadata["rerank_score"] = 0.5
                    return documents[:top_n]
            
            # Preparar pares (query, doc_content) para scoring
            pairs = [(query, doc.page_content) for doc in documents]
            
            # Calcular scores de relevancia
            print(f"🔄 Calculando scores de relevancia para {len(documents)} documentos...")
            scores = self.reranker_model.predict(pairs)
            
            # Añadir scores a los metadatos de los documentos
            for doc, score in zip(documents, scores):
                doc.metadata["rerank_score"] = float(score)
            
            # Ordenar documentos por rerank_score descendente
            documents.sort(key=lambda d: d.metadata.get("rerank_score", 0), reverse=True)
            
            # Retornar top_n documentos con mejor score
            top_docs = documents[:top_n]
            
            print(f"✅ Reranking completado. Top {len(top_docs)} documentos seleccionados.")
            print(f"   Scores: {[doc.metadata.get('rerank_score', 0) for doc in top_docs]}")
            
            return top_docs
            
        except Exception as e:
            print(f"⚠️ Error en reranking: {str(e)}. Retornando documentos sin reordenar.")
            # En caso de error, retornar documentos originales sin reordenar
            for doc in documents:
                if "rerank_score" not in doc.metadata:
                    doc.metadata["rerank_score"] = 0.5
            return documents[:top_n]
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Obtiene información sobre una colección.
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Dict con información de la colección (exists, path, document_count)
        """
        try:
            collection_directory = os.path.join(self.persist_directory, collection_name)
            
            # Verificar si existe
            exists = os.path.exists(collection_directory)
            
            if not exists:
                return {
                    "exists": False,
                    "path": "",
                    "document_count": 0
                }
            
            # Verificar archivos ChromaDB
            chroma_files = [f for f in os.listdir(collection_directory) if f.endswith('.parquet') or f.endswith('.sqlite3')]
            
            if not chroma_files:
                return {
                    "exists": False,
                    "path": collection_directory,
                    "document_count": 0
                }
            
            # Intentar obtener el conteo de documentos
            document_count = 0
            try:
                from app.services.embedding_service import EmbeddingService
                embedding_service = EmbeddingService()
                vector_store = self.get_vector_store(collection_name, embedding_service)
                if vector_store:
                    document_count = vector_store._collection.count()
            except Exception as e:
                # Si no se puede obtener el conteo, usar 0
                pass
            
            return {
                "exists": True,
                "path": collection_directory,
                "document_count": document_count
            }
            
        except Exception as e:
            return {
                "exists": False,
                "path": "",
                "document_count": 0
            }