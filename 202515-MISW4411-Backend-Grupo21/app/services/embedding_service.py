"""
Servicio de Embeddings para el Sistema RAG
==========================================

Este módulo implementa la funcionalidad de inicializar y proveer modelos de embeddings
para el almacenamiento y búsqueda semántica en el sistema RAG.

TAREAS SEMANA 2:
- Inicializar GoogleGenerativeAIEmbeddings con el modelo especificado
- Proveer el modelo para uso en RetrievalService (ChromaDB)
- Opcionalmente: implementar método para generar embeddings explícitamente (Uso de otra base de datos vectorial)

TUTORIAL:
- RAG paso a paso, parte 2: embeddings y base de datos vectorial
"""

import os
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar la API key de Google AI
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


class EmbeddingService:
    """
    Servicio para generar embeddings usando Google Generative AI.
    
    IMPLEMENTACIÓN REQUERIDA:
    - __init__: Inicializar el modelo de embeddings
    - get_embeddings_model: Retornar el modelo para uso externo
    """
    
    def __init__(self, model: str = "models/embedding-001"):
        """
        Inicializa el servicio de embeddings con el modelo de Google AI.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Guardar model en self.model_name
        - Inicializar self.embeddings_model con GoogleGenerativeAIEmbeddings
        
        NOTA: ChromaDB usará este modelo para generar embeddings automáticamente
        
        Args:
            model: Nombre del modelo de embeddings (ej: "models/embedding-001")
        """
        # Guardar el nombre del modelo
        self.model_name = model
        
        # Verificar que la API key esté configurada
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY no encontrada en variables de entorno. "
                "Por favor, configura tu API key en el archivo .env"
            )
        
        # Inicializar el modelo de embeddings de Google Generative AI
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=api_key
        )
        
        
    
    def get_embeddings_model(self) -> GoogleGenerativeAIEmbeddings:
        """
        Retorna el modelo de embeddings para uso externo.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Retornar self.embeddings_model
        
        NOTA: Este método es llamado por RetrievalService para crear el vector store
        
        Returns:
            Instancia del modelo de embeddings
        """
        return self.embeddings_model
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Genera embeddings para una lista de textos.
        
        MÉTODO ADICIONAL SEMANA 2:
        - Generar embeddings explícitamente para uso con otras bases de datos vectoriales
        - Útil para debugging y análisis de embeddings
        
        Args:
            texts: Lista de textos para generar embeddings
            
        Returns:
            Lista de vectores de embeddings (cada vector es una lista de floats)
        """
        try:
            embeddings = self.embeddings_model.embed_documents(texts)
            
            return embeddings
        except Exception as e:
            
            raise e
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Genera embedding para una consulta individual.
        
        MÉTODO ADICIONAL SEMANA 2:
        - Generar embedding para consultas de búsqueda
        - Útil para debugging y análisis de similitud
        
        Args:
            query: Texto de la consulta
            
        Returns:
            Vector de embedding (lista de floats)
        """
        try:
            embedding = self.embeddings_model.embed_query(query)
            
            return embedding
        except Exception as e:
            
            raise e