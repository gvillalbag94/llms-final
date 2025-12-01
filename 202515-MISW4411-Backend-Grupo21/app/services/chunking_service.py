"""
Servicio de Chunking para el Sistema RAG
========================================

Este módulo implementa la funcionalidad de dividir documentos en fragmentos (chunks)
más pequeños y manejables para su procesamiento en el sistema RAG.

TAREAS SEMANA 2:
- Implementar al menos 2 estrategias de chunking de las 5 disponibles
- Seleccionar las estrategias según las necesidades de tu caso de uso
- Cargar documentos desde la colección
- Aplicar chunking a los documentos
- Retornar chunks con metadatos enriquecidos

TAREAS SEMANA 3:
- Implementar preprocesamiento de PDFs a Markdown usando markitdown
- Integrar el preprocesamiento antes del chunking

TUTORIALES:
- RAG paso a paso, parte 1: ingesta y estrategias de chunking
"""

from enum import Enum
import os
from typing import List, Dict, Any
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    NLTKTextSplitter,
    PythonCodeTextSplitter
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pypdf import PdfReader
import nltk

# Imports para preprocesamiento de PDFs (Semana 3)
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    print("⚠️ markitdown no disponible. Preprocesamiento de PDFs deshabilitado.")

# Cargar variables desde el archivo .env
load_dotenv()

# Asignar la clave de API a la variable de entorno que espera el SDK de Google
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


class ChunkingStrategy(str, Enum):
    """Estrategias de chunking disponibles"""
    RECURSIVE_CHARACTER = "recursive_character"
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    DOCUMENT_STRUCTURE = "document_structure"
    LINGUISTIC_UNITS = "linguistic_units"


class ChunkingService:
    """
    Servicio para segmentar documentos en chunks usando diferentes estrategias.
    
    IMPLEMENTACIÓN REQUERIDA:
    - __init__: Inicializar la estrategia de chunking seleccionada
    - Crear métodos para tus 2 estrategias de chunking elegidas (ej: _create_X_splitter)
    - _preprocess_pdf_to_markdown: Preprocesar PDFs con markitdown (Semana 3)
    - load_documents_from_collection: Cargar documentos aplicando preprocesamiento (Semana 3)
    - process_collection: Aplicar chunking a una colección completa
    """
    
    def __init__(
        self, 
        strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE_CHARACTER, #Ejemplo
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: List[str] = None
    ):
        """
        Inicializa el servicio de chunking con la estrategia seleccionada.
        
        TODO SEMANA 2:
        - Guardar los parámetros en self
        - Inicializar self.splitter según la estrategia elegida
        - Implementar métodos auxiliares para crear tus splitters
          (ej: _create_estrategia1_splitter, _create_estrategia2_splitter)
        
        Args:
            strategy: Estrategia de chunking a utilizar
            chunk_size: Tamaño máximo de cada chunk
            chunk_overlap: Solapamiento entre chunks
            separators: Lista de separadores (si tu estrategia lo requiere)

        Hint: En el tutorial y en el frontend se muestran ejemplos de que 
        Args son requeridos para la implementación de las estrategias de chunking.
        """
        # Guardar parámetros en self
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]
        
        # Inicializar el splitter según la estrategia elegida
        if strategy == ChunkingStrategy.RECURSIVE_CHARACTER:
            self.splitter = self._create_recursive_character_splitter()
        elif strategy == ChunkingStrategy.FIXED_SIZE:
            self.splitter = self._create_fixed_size_splitter()
        elif strategy == ChunkingStrategy.SEMANTIC:
            self.splitter = self._create_semantic_splitter()
        elif strategy == ChunkingStrategy.DOCUMENT_STRUCTURE:
            self.splitter = self._create_document_structure_splitter()
        elif strategy == ChunkingStrategy.LINGUISTIC_UNITS:
            self.splitter = self._create_linguistic_units_splitter()
        else:
            # Fallback a recursive character si la estrategia no está implementada
            self.splitter = self._create_recursive_character_splitter()
    
    # ===========================================
    # ESTRATEGIAS DE CHUNKING IMPLEMENTADAS
    # ===========================================
    
    def _create_recursive_character_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Crea un splitter de caracteres recursivos.
        
        Esta estrategia divide el texto usando una lista de separadores en orden de prioridad.
        Es ideal para documentos con estructura jerárquica (párrafos, líneas, palabras).
        """
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def _create_fixed_size_splitter(self) -> CharacterTextSplitter:
        """
        Crea un splitter de tamaño fijo.
        
        Esta estrategia divide el texto en chunks de tamaño exacto sin considerar
        la estructura del documento. Es útil cuando se necesita un control preciso del tamaño.
        """
        return CharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separator=" "  # Usar espacio como separador para garantizar división
        )
    
    def _create_semantic_splitter(self) -> SemanticChunker:
        """
        Crea un splitter semántico basado en embeddings.
        
        Esta estrategia divide el texto basándose en la similitud semántica entre oraciones.
        Requiere un modelo de embeddings para calcular la similitud.
        """
        # Inicializar embeddings de Google Gemini
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")  # En producción usar variable de entorno
        )
        
        return SemanticChunker(
            embeddings=embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=95
        )
    
    def _create_document_structure_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Crea un splitter basado en la estructura del documento.
        
        Esta estrategia divide el texto basándose en la estructura jerárquica del documento,
        usando separadores que respetan la organización del contenido.
        """
        # Separadores que respetan la estructura del documento
        structure_separators = [
            "\n\n",  # Párrafos
            "\n",    # Líneas
            ". ",    # Oraciones
            " ",     # Palabras
            ""       # Caracteres individuales
        ]
        
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=structure_separators,
            length_function=len,
            is_separator_regex=False
        )
    
    def _create_linguistic_units_splitter(self) -> NLTKTextSplitter:
        """
        Crea un splitter basado en unidades lingüísticas usando NLTK.
        
        Esta estrategia divide el texto en oraciones usando NLTK,
        respetando los límites naturales del lenguaje.
        """
        # Descargar los recursos necesarios de NLTK si no están disponibles
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab')
        
        return NLTKTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def _preprocess_pdf_to_markdown(self, pdf_path: Path) -> Path:
        """
        Convierte un archivo PDF a Markdown usando markitdown.
        
        Implementación SEMANA 3:
        - Importar markitdown (MarkItDown)
        - Convertir el PDF a texto Markdown
        - Guardar el .md en el mismo directorio que el PDF
        - Retornar ruta al .md si tiene éxito, o ruta al PDF si falla (fallback)
        - Manejar errores (ImportError, excepciones generales)
        
        NOTA: Este paso mejora la extracción de texto de PDFs.
        El preprocesamiento convierte PDFs complejos con tablas y estructuras
        a texto Markdown más limpio para mejores resultados de chunking.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Path: Ruta al archivo Markdown generado (o PDF original si falla)
        """
        # Si markitdown no está disponible, retornar PDF sin procesar
        if not MARKITDOWN_AVAILABLE:
            print(f"⚠️ markitdown no disponible. Saltando preprocesamiento de {pdf_path.name}")
            return pdf_path
        
        try:
            # Inicializar MarkItDown
            md = MarkItDown()
            
            # Convertir PDF a Markdown
            print(f"🔄 Preprocesando {pdf_path.name} a Markdown...")
            result = md.convert(str(pdf_path))
            
            # Crear ruta para el archivo Markdown
            md_path = pdf_path.parent / f"{pdf_path.stem}.md"
            
            # Guardar el contenido Markdown
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(result.text_content)
            
            print(f"✅ Preprocesamiento exitoso: {pdf_path.name} -> {md_path.name}")
            return md_path
            
        except ImportError as e:
            print(f"⚠️ Error de importación en markitdown: {e}. Usando PDF original.")
            return pdf_path
        except Exception as e:
            print(f"⚠️ Error en preprocesamiento de {pdf_path.name}: {str(e)}. Usando PDF original.")
            return pdf_path
    
    def load_documents_from_collection(self, collection_name: str) -> List[Document]:
        """
        Carga todos los documentos de una colección.
        
        TODO SEMANA 2:
        - Buscar archivos PDF en ./docs/{collection_name}
        - Extraer texto de cada PDF usando PdfReader
        - Crear objetos Document con page_content y metadata
        - Retornar lista de documentos
        
        TODO SEMANA 3:
        - Antes de cargar el PDF, llamar a _preprocess_pdf_to_markdown()
        - Si retorna un .md, cargar desde el Markdown
        - Si retorna un .pdf, usar PdfReader como fallback
        
        METADATA REQUERIDA:
        - source_file: Nombre del archivo
        - source_path: Ruta completa
        - file_size: Tamaño en bytes
        - preprocessed: True/False (Semana 3)
        
        Args:
            collection_name: Nombre de la colección
            
        Returns:
            Lista de objetos Document con contenido y metadatos
        """
        documents = []
        docs_path = Path(f"./docs/{collection_name}")
        
        # Verificar que el directorio existe
        if not docs_path.exists():
            print(f"Advertencia: El directorio {docs_path} no existe")
            return documents
        
        # Buscar archivos PDF en el directorio
        pdf_files = list(docs_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"Advertencia: No se encontraron archivos PDF en {docs_path}")
            return documents
        
        # Procesar cada archivo PDF
        for pdf_path in pdf_files:
            try:
                # SEMANA 3: Preprocesar PDF a Markdown si es posible
                processed_file = self._preprocess_pdf_to_markdown(pdf_path)
                is_preprocessed = processed_file.suffix == ".md"
                
                # Cargar contenido según el tipo de archivo
                if is_preprocessed:
                    # Cargar desde archivo Markdown
                    with open(processed_file, "r", encoding="utf-8") as f:
                        text_content = f.read()
                    
                    # Obtener tamaño del archivo original PDF
                    file_size = pdf_path.stat().st_size
                    source_file_name = pdf_path.name
                else:
                    # Fallback: cargar desde PDF usando PdfReader
                    reader = PdfReader(pdf_path)
                    text_content = ""
                    
                    # Concatenar texto de todas las páginas
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
                    
                    file_size = pdf_path.stat().st_size
                    source_file_name = pdf_path.name
                
                # Crear metadatos (SEMANA 3: incluir si fue preprocesado)
                metadata = {
                    "source_file": source_file_name,
                    "source_path": str(pdf_path.absolute()),
                    "file_size": file_size,
                    "preprocessed": is_preprocessed,  # Semana 3: True si fue preprocesado
                    "collection": collection_name
                }
                
                # Si no fue preprocesado, añadir total_pages
                if not is_preprocessed:
                    try:
                        reader = PdfReader(pdf_path)
                        metadata["total_pages"] = len(reader.pages)
                    except:
                        pass
                
                # Crear objeto Document
                document = Document(
                    page_content=text_content.strip(),
                    metadata=metadata
                )
                
                documents.append(document)
                status = "preprocesado" if is_preprocessed else "directo"
                print(f"Documento cargado ({status}): {source_file_name} ({len(text_content)} caracteres)")
                
            except Exception as e:
                print(f"Error al procesar {pdf_path.name}: {str(e)}")
                continue
        
        print(f"Total de documentos cargados: {len(documents)}")
        return documents
    
    def process_collection(self, collection_name: str) -> List[Document]:
        """
        Procesa una colección completa de documentos aplicando chunking.
        
        TODO SEMANA 2:
        - Llamar a load_documents_from_collection()
        - Para cada documento, aplicar self.splitter
        - Enriquecer cada chunk con metadata adicional:
          * source_file, chunk_index, total_chunks_in_doc
          * chunking_strategy, chunk_size
        - Retornar lista de chunks
        
        NOTA: Este método es llamado por load_documents_service.py
        
        Args:
            collection_name: Nombre de la colección a procesar
            
        Returns:
            Lista de chunks (objetos Document) con metadatos enriquecidos
        """
        # Cargar documentos de la colección
        documents = self.load_documents_from_collection(collection_name)
        
        if not documents:
            print(f"No se encontraron documentos en la colección: {collection_name}")
            return []
        
        all_chunks = []
        
        # Procesar cada documento
        for doc_idx, document in enumerate(documents):
            try:
                # Aplicar chunking al documento
                chunks = self.splitter.split_documents([document])
                
                # Enriquecer metadatos de cada chunk
                for chunk_idx, chunk in enumerate(chunks):
                    # Copiar metadatos originales
                    enriched_metadata = chunk.metadata.copy()
                    
                    # Agregar metadatos de chunking
                    enriched_metadata.update({
                        "chunk_index": chunk_idx,
                        "total_chunks_in_doc": len(chunks),
                        "document_index": doc_idx,
                        "chunking_strategy": self.strategy.value,
                        "chunk_size": len(chunk.page_content),
                        "chunk_overlap": self.chunk_overlap,
                        "original_doc_size": len(document.page_content)
                    })
                    
                    # Crear nuevo chunk con metadatos enriquecidos
                    enriched_chunk = Document(
                        page_content=chunk.page_content,
                        metadata=enriched_metadata
                    )
                    
                    all_chunks.append(enriched_chunk)
                
                print(f"Documento {doc_idx + 1}/{len(documents)} procesado: "
                      f"{document.metadata['source_file']} -> {len(chunks)} chunks")
                
            except Exception as e:
                print(f"Error al procesar documento {document.metadata.get('source_file', 'unknown')}: {str(e)}")
                continue
        
        print(f"Procesamiento completado: {len(all_chunks)} chunks generados de {len(documents)} documentos")
        return all_chunks
    
    def get_chunking_statistics(self, chunks: List[Document]) -> Dict[str, Any]:
        """
        Calcula estadísticas sobre los chunks generados.
        
        TODO SEMANA 2:
        - Calcular tamaño promedio, mínimo y máximo de chunks
        - Contar chunks con overlap
        - Calcular total de caracteres procesados
        
        Args:
            chunks: Lista de chunks procesados
            
        Returns:
            Diccionario con estadísticas de chunking
        """
        if not chunks:
            return {
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "chunks_with_overlap": 0,
                "total_characters_processed": 0,
                "total_chunks": 0,
                "chunking_strategy": self.strategy.value
            }
        
        # Calcular tamaños de chunks
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        
        # Estadísticas básicas
        avg_chunk_size = sum(chunk_sizes) / len(chunk_sizes)
        min_chunk_size = min(chunk_sizes)
        max_chunk_size = max(chunk_sizes)
        
        # Contar chunks con overlap (aquellos que no son el primer chunk de su documento)
        chunks_with_overlap = sum(1 for chunk in chunks if chunk.metadata.get("chunk_index", 0) > 0)
        
        # Total de caracteres procesados
        total_characters_processed = sum(chunk_sizes)
        
        # Estadísticas adicionales útiles
        total_chunks = len(chunks)
        
        # Contar documentos únicos
        unique_documents = len(set(chunk.metadata.get("source_file", "") for chunk in chunks))
        
        # Calcular distribución de tamaños
        size_distribution = {
            "small_chunks": sum(1 for size in chunk_sizes if size < self.chunk_size * 0.5),
            "medium_chunks": sum(1 for size in chunk_sizes if self.chunk_size * 0.5 <= size < self.chunk_size * 1.5),
            "large_chunks": sum(1 for size in chunk_sizes if size >= self.chunk_size * 1.5)
        }
        
        return {
            "avg_chunk_size": round(avg_chunk_size, 2),
            "min_chunk_size": min_chunk_size,
            "max_chunk_size": max_chunk_size,
            "chunks_with_overlap": chunks_with_overlap,
            "total_characters_processed": total_characters_processed,
            "total_chunks": total_chunks,
            "unique_documents": unique_documents,
            "chunking_strategy": self.strategy.value,
            "chunk_size_config": self.chunk_size,
            "chunk_overlap_config": self.chunk_overlap,
            "size_distribution": size_distribution,
            "overlap_percentage": round((chunks_with_overlap / total_chunks) * 100, 2) if total_chunks > 0 else 0
        }