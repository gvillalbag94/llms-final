"""
Modelos para el sistema RAG de consultas

Define las estructuras de datos para las consultas al sistema RAG,
incluyendo peticiones, respuestas y metadatos de contexto.
"""

from pydantic import BaseModel
from typing import Optional, List


class AskRequest(BaseModel):
    """
    Modelo para validar las peticiones de consulta al sistema RAG.
    
    Este modelo define la estructura de datos que los estudiantes deben enviar
    cuando quieren hacer una pregunta al sistema de documentos.
    
    Atributos:
        question (str): La pregunta que se quiere responder. Campo obligatorio.
        top_k (int, optional): Número máximo de documentos relevantes a recuperar.
                              Por defecto: 5. Rango recomendado: 3-10.
        collection (str, optional): Nombre de la colección de documentos a consultar.
                                   Si no se especifica, usa 'default'.
        force_rebuild (bool, optional): Si True, reconstruye el índice de búsqueda.
                                       Por defecto: False. Usar solo si es necesario.
        use_reranking (bool, optional): Si True, aplica reranking a los resultados.
                                       Por defecto: False. Mejora la relevancia pero añade latencia.
                                       Cuando se activa, automáticamente se incluyen los scores de reranking.
        use_query_rewriting (bool, optional): Si True, aplica reescritura de consulta.
                                             Por defecto: False. Mejora la comprensión de la consulta.
    """
    question: str
    top_k: Optional[int] = 5
    collection: Optional[str] = None
    force_rebuild: Optional[bool] = False
    use_reranking: Optional[bool] = False
    use_query_rewriting: Optional[bool] = False


class FuenteContexto(BaseModel):
    """
    Modelo que representa una fuente de información utilizada para generar la respuesta.
    
    Cada objeto de este tipo contiene metadatos sobre un fragmento de documento
    que fue relevante para responder la pregunta del usuario.
    
    Atributos:
        file_name (str, optional): Nombre del archivo fuente del fragmento.
        page_number (int, optional): Número de página dentro del documento.
        chunk_type (str, optional): Tipo de fragmento (ej: 'text', 'table', 'header').
        priority (str, optional): Prioridad de relevancia ('high', 'medium', 'low').
        snippet (str, optional): Fragmento de texto extraído del documento (preview).
        content (str, optional): Contenido completo del chunk (para RAGAS).
        rerank_score (float, optional): Score de reranking CrossEncoder.
                                       Se incluye automáticamente cuando use_reranking=True.
                                       None si no se usó reranking.
    """
    file_name: Optional[str] = None
    page_number: Optional[int] = None
    chunk_type: Optional[str] = None
    priority: Optional[str] = None
    snippet: Optional[str] = None
    content: Optional[str] = None
    rerank_score: Optional[float] = None


class AskResponse(BaseModel):
    """
    Modelo de respuesta que retorna el sistema RAG después de procesar una consulta.
    
    Esta clase estructura toda la información que el sistema devuelve al usuario,
    incluyendo la respuesta generada y metadatos sobre el proceso de búsqueda.
    
    Atributos:
        question (str): La pregunta original que se procesó.
        final_query (str): La consulta final después del query rewriting (si se aplicó).
                          Si no se usa rewriting, será igual a question.
        answer (str): La respuesta generada por el sistema RAG.
        collection (str): Nombre de la colección de documentos utilizada.
        files_consulted (List[str]): Lista de nombres de archivos consultados.
        context_docs (List[FuenteContexto]): Fragmentos específicos utilizados como contexto.
        reranker_used (bool): Indica si se utilizó reordenamiento de resultados.
        query_rewriting_used (bool): Indica si se aplicó reescritura de consulta.
        response_time_sec (float): Tiempo total de procesamiento en segundos.
    """
    question: str
    final_query: str
    answer: str
    collection: str
    files_consulted: List[str] = []
    context_docs: List[FuenteContexto] = []
    reranker_used: bool = False
    query_rewriting_used: bool = False
    response_time_sec: float
