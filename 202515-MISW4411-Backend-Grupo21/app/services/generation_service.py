"""
Servicio de Generación para el Sistema RAG
==========================================

Este módulo implementa la funcionalidad de generar respuestas usando LLMs
basándose en el contexto recuperado del sistema RAG.

TAREAS SEMANA 2:
- Inicializar LLM (ChatGoogleGenerativeAI)
- Crear prompt template para RAG
- Implementar generación de respuestas con contexto recuperado
- Implementar evaluación con RAGAS

TAREAS SEMANA 3:
- Implementar query rewriting (reescritura de consultas)

TUTORIALES:
- RAG paso a paso, parte 3: recuperación y generación de respuestas
- Reescritura de consultas
"""

import os
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar la API key de Google AI
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")


class GenerationService:
    """
    Servicio para generar respuestas usando Google Gemini con contexto RAG.
    
    IMPLEMENTACIÓN REQUERIDA (SEMANA 2):
    - __init__: Inicializar LLM y prompt template
    - generate_response: Generar respuesta con contexto
    - evaluate_with_ragas: Evaluar sistema con métricas RAGAS
    
    IMPLEMENTACIÓN REQUERIDA (SEMANA 3):
    - rewrite_query: Reescribir consultas para mejorar recuperación
    """
    
    def __init__(
        self, 
        model: str = "gemini-2.5-pro",
        temperature: float = 0.1,
        max_tokens: int = 4000
    ):
        """
        Inicializa el servicio de generación con Google Gemini.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Inicializar self.llm con ChatGoogleGenerativeAI
        - Crear self.prompt con ChatPromptTemplate.from_template()
        - El prompt debe tener placeholders: {question} y {context}
        
        RECOMENDACIONES PARA EL PROMPT:
        - Instruir al modelo a responder solo con el contexto proporcionado
        - Indicar qué hacer si no tiene información suficiente
        - Mantener respuestas concisas
        
        Args:
            model: Nombre del modelo de Google AI
            temperature: Temperatura para generación (0-1)
            max_tokens: Número máximo de tokens en respuesta
        """
        # Verificar que la API key esté configurada
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY no encontrada en variables de entorno. "
                "Por favor, configura tu API key en el archivo .env"
            )
        
        # Inicializar el modelo de generación de Google Generative AI
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=api_key
        )
        
        # Crear prompt template para RAG
        self.prompt = ChatPromptTemplate.from_template("""
Eres un asistente experto que responde preguntas basándote únicamente en el contexto proporcionado.

CONTEXTO:
{context}

PREGUNTA: {question}

INSTRUCCIONES:
1. Responde la pregunta usando SOLO la información del contexto proporcionado
2. Si el contexto no contiene información suficiente para responder, di claramente "No tengo información suficiente en el contexto proporcionado para responder esta pregunta"
3. Mantén tu respuesta concisa y precisa
4. Si hay múltiples fuentes en el contexto, puedes mencionar que la información proviene de diferentes fuentes
5. No inventes información que no esté en el contexto

RESPUESTA:
""")
    
    
    def generate_response(
        self, 
        question: str, 
        retrieved_docs: List[Document]
    ) -> Dict[str, Any]:
        """
        Genera una respuesta usando el contexto recuperado.
        
        IMPLEMENTACIÓN COMPLETADA SEMANA 2:
        - Preparar contexto: concatenar retrieved_docs.page_content
        - Construir mensaje con self.prompt.invoke({question, context})
        - Generar respuesta con self.llm.invoke(messages)
        - Extraer archivos consultados de los metadatos
        - Retornar diccionario con:
          * "answer": texto de la respuesta
          * "sources": lista de archivos consultados
          * "context": documentos recuperados
        
        NOTA: Este método es llamado por ask.py después de recuperar documentos
        
        Args:
            question: Pregunta del usuario
            retrieved_docs: Documentos recuperados del vector store
            
        Returns:
            Dict con answer, sources y context
        """
        try:
            if not retrieved_docs:
                return {
                    "answer": "No tengo información suficiente en la base de datos para responder a esta pregunta.",
                    "sources": [],
                    "context": []
                }
            
            # Preparar contexto concatenando el contenido de los documentos
            context_parts = []
            for doc in retrieved_docs:
                # Limpiar el contenido del documento
                cleaned_content = doc.page_content.replace('\n \n', ' ').replace('\n', ' ').strip()
                # Eliminar espacios múltiples
                cleaned_content = ' '.join(cleaned_content.split())
                context_parts.append(cleaned_content)
            
            context = "\n\n".join(context_parts)
            
            # Construir mensaje con el prompt
            messages = self.prompt.invoke({
                "question": question,
                "context": context
            })
            
            # Generar respuesta con el LLM
            response = self.llm.invoke(messages)
            answer = response.content.strip()
            
            # Extraer archivos consultados de los metadatos
            sources = list(set(doc.metadata.get("source_file", "unknown") for doc in retrieved_docs))
            
            
            return {
                "answer": answer,
                "sources": sources,
                "context": retrieved_docs
            }
            
        except Exception as e:
            return {
                "answer": f"Error generando respuesta: {str(e)}",
                "sources": [],
                "context": retrieved_docs
            }
    
    def evaluate_with_ragas(
        self, 
        dataset: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evalúa el sistema RAG usando métricas RAGAS.
        
        TODO SEMANA 2:
        - Configurar LLM y embeddings para evaluación
        - Definir métricas: faithfulness, answer_relevancy, context_precision, context_recall
        - Convertir dataset a formato RAGAS (Dataset.from_dict)
        - Ejecutar evaluate() con dataset y métricas
        - Retornar resultados
        
        DATASET FORMAT:
        [
          {
            "question": "...",
            "answer": "...",
            "contexts": ["...", "..."],
            "ground_truth": "..."
          },
          ...
        ]
    
        
        Args:
            dataset: Lista de ejemplos con question, answer, contexts, ground_truth
            
        Returns:
            Resultados de la evaluación RAGAS
        """
        # TODO SEMANA 2: Implementar evaluación con RAGAS
        pass
    
    def rewrite_query(self, question: str) -> str:
        """
        Reescribe la consulta del usuario para mejorar la recuperación de documentos.
        
        Implementación SEMANA 3:
        - Usa estrategia de Query Expansion y Refinement
        - Crea un prompt de sistema para reescribir la consulta
        - Usa el LLM para generar la consulta mejorada
        - Retorna consulta reescrita
        - Si falla, retorna question original (fallback)
        
        ESTRATEGIA IMPLEMENTADA:
        - Query Expansion + Refinement: Expande con términos relacionados y reformula
        
        NOTA: Este método es llamado por ask.py antes de recuperar documentos
        cuando el parámetro use_query_rewriting=True
        
        Args:
            question: Consulta original del usuario
            
        Returns:
            str: Consulta reescrita y mejorada
        """
        try:
            # Crear prompt para query rewriting usando Query Expansion
            rewrite_prompt = ChatPromptTemplate.from_template("""
Eres un experto en reformulación de consultas para sistemas de búsqueda de información.

Tu tarea es reescribir la consulta del usuario para mejorar la recuperación de documentos
relevantes en un sistema RAG.

CONSULTA ORIGINAL: {question}

INSTRUCCIONES:
1. Expande la consulta con términos relacionados y sinónimos relevantes
2. Reformula la consulta para que sea más específica y enfocada
3. Mantén el significado original de la consulta
4. Asegúrate de que la consulta reescrita sea clara y completa
5. Si la consulta es vaga, hazla más específica
6. Retorna ÚNICAMENTE la consulta reescrita, sin explicaciones adicionales

CONSULTA REESCRITA:
""")
            
            # Invocar el LLM para reescribir la consulta
            messages = rewrite_prompt.invoke({"question": question})
            response = self.llm.invoke(messages)
            rewritten_query = response.content.strip()
            
            # Validar que la consulta reescrita tiene sentido
            if rewritten_query and len(rewritten_query) > 10:
                return rewritten_query
            else:
                print("⚠️ Query rewriting falló: consulta reescrita demasiado corta o vacía")
                return question
                
        except Exception as e:
            print(f"⚠️ Error en query rewriting: {str(e)}. Usando consulta original.")
            return question