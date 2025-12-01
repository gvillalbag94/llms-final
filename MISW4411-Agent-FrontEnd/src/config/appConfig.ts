// ========================================
// CONFIGURACIÓN DE LA APLICACIÓN
// ========================================
// Archivo para que los estudiantes modifiquen

export const APP_CONFIG = {
  // ========== INFORMACIÓN DEL PROYECTO ==========
  // Cambiar por el nombre de su proyecto o grupo
  PROJECT_NAME: "Asistente Inteligente MISW4411",
  
  // Número del grupo (opcional)
  GROUP_NUMBER: "Grupo 21", // Ejemplo: "Grupo 5" o null
  
  // Nombre(s) del/los estudiante(s) (opcional)
  STUDENT_NAMES: null, // Ejemplo: "Seneca Uniandes - Aura Uniandes" o null
  
  // ========== DESCRIPCIÓN ==========
  DESCRIPTION: "Herramienta que ayuda a los desarrolladores a consultar de manera más ágil la documentación oficial de lenguajes de programación, frameworks y librerías",
  
  // ========== CONFIGURACIÓN DEL CHAT ==========
  // Mensaje inicial del bot
  INITIAL_BOT_MESSAGE: "¡Hola! 👋\n\nSomos el **Grupo 21** y te damos la bienvenida a nuestro chatbot.\n\nEste chatbot es una herramienta diseñada para ayudarte a consultar de manera más ágil la **documentación oficial de lenguajes de programación, frameworks y librerías**. Puedes hacerme preguntas sobre cualquier tecnología y te ayudaré a encontrar la información que necesitas de forma rápida y precisa.\n\n¿En qué puedo ayudarte hoy?",
  
  // Placeholder del input
  INPUT_PLACEHOLDER: "Escribe tu pregunta para el RAG...",
  
  // ========== CONFIGURACIÓN DE AGENTES ==========
  // Título del Agente RAG
  AGENT_RAG_TITLE: "Agente RAG MISW4411",
  
  // Título del Agente Especializado
  AGENT_SPECIALIZED_TITLE: "Agente Especializado MISW4411",
  
  // Placeholder del input para Agente Especializado
  AGENT_SPECIALIZED_INPUT_PLACEHOLDER: "Información para la tarea a realizar...",
  
  // ========== CONFIGURACIÓN DEL BACKEND ==========
  // URL del backend (puede ser configurada mediante variable de entorno VITE_BACKEND_URL)
  BACKEND_URL: import.meta.env.VITE_BACKEND_URL || "http://localhost:8001",
  
  // Endpoints de la API
  RAG_ENDPOINT: "/ask_rag",
  CUSTOM_ENDPOINT: "/ask_custom",
  
};

// ========================================
// FUNCIONES AUXILIARES
// ========================================
// No modificar estas funciones

/**
 * Genera el título completo de la aplicación
 * Incluye nombre del proyecto, grupo y estudiantes si están definidos
 */
export const getFullTitle = (): string => {
  let title = APP_CONFIG.PROJECT_NAME;
  
  if (APP_CONFIG.GROUP_NUMBER) {
    title += ` - ${APP_CONFIG.GROUP_NUMBER}`;
  }
  
  if (APP_CONFIG.STUDENT_NAMES) {
    title += ` - ${APP_CONFIG.STUDENT_NAMES}`;
  }
  
  return title;
};

/**
 * Genera la URL completa del endpoint RAG
 */
export const getRAGUrl = (): string => {
  return `${APP_CONFIG.BACKEND_URL}${APP_CONFIG.RAG_ENDPOINT}`;
};

/**
 * Genera la URL completa del endpoint Custom/Especializado
 */
export const getCustomUrl = (): string => {
  return `${APP_CONFIG.BACKEND_URL}${APP_CONFIG.CUSTOM_ENDPOINT}`;
};

/**
 * Genera el cuerpo de la petición al backend según FRONTEND_INTEGRATION.md
 * Ambos endpoints esperan el mismo formato: { "question": "..." }
 */
export const createRequestBody = (question: string) => {
  return {
    question
  };
};
