/**
 * @fileoverview RAG Types
 * 
 * Definiciones de tipos para el sistema RAG (Retrieval Augmented Generation).
 * Incluye tipos para respuestas de la API, mensajes de chat y configuraciones.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

/**
 * Tipos para la API del Chat y sistema RAG
 */

/**
 * Documento de contexto utilizado en respuestas RAG
 * Representa un fragmento de documento que se usó para generar la respuesta
 */
export interface ContextDoc {
  file_name: string;      // Nombre del archivo fuente
  page_number: number;    // Número de página donde se encontró el fragmento
  chunk_type: string;     // Tipo de chunk (párrafo, título, etc.)
  priority: number;       // Prioridad del fragmento en la respuesta
  snippet: string;        // Contenido del fragmento de texto
}

/**
 * Respuesta de la API de chat RAG
 * Contiene la respuesta generada y metadatos del procesamiento
 */
export interface AskResponse {
  answer: string;                 // Respuesta generada por el modelo
  files_consulted: string[];      // Lista de archivos consultados
  context_docs: ContextDoc[];     // Fragmentos de contexto utilizados
  response_time_sec: number;      // Tiempo de respuesta en segundos
}

/**
 * Solicitud a la API de chat RAG
 * Parámetros necesarios para realizar una consulta
 */
export interface AskRequest {
  question: string;        // Pregunta del usuario
  top_k: number;          // Número de documentos más relevantes a recuperar
  collection: string;     // Nombre de la colección de documentos
  force_rebuild: boolean; // Forzar reconstrucción del índice
}
