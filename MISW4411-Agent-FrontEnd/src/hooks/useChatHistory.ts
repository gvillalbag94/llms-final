/**
 * @fileoverview useChatHistory Hook
 * 
 * Hook personalizado para gestionar el historial de conversación del chat.
 * Proporciona funcionalidades de persistencia en localStorage, límites de mensajes
 * y gestión del estado de la conversación con mensajes iniciales.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import { useState, useEffect } from 'react';

/**
 * Roles disponibles para los mensajes del chat
 */
export type ChatRole = "user" | "bot";

/**
 * Estructura de un mensaje del chat
 */
export type ChatMessage = { role: ChatRole; text: string; timestamp?: number };

const MAX_MESSAGES = 100; // Límite para evitar que localStorage crezca demasiado

/**
 * Opciones para el hook useChatHistory
 */
interface UseChatHistoryOptions {
  chatId: string;              // Identificador único para este chat
  initialMessage?: ChatMessage; // Mensaje inicial opcional
}

/**
 * Hook personalizado para gestionar el historial del chat
 * 
 * Funcionalidades principales:
 * - Persistencia automática en localStorage con identificadores únicos
 * - Límite de mensajes para optimizar rendimiento
 * - Mensaje inicial opcional
 * - Gestión de errores en operaciones de almacenamiento
 * - Funciones para agregar, limpiar y resetear mensajes
 * - Soporte para múltiples chats independientes
 * 
 * @param options - Opciones de configuración (chatId e initialMessage)
 * @returns Objeto con estado y funciones para gestionar el historial
 */
export function useChatHistory({ chatId, initialMessage }: UseChatHistoryOptions) {
  const CHAT_HISTORY_KEY = `chat_history_${chatId}`; // Clave única por chat
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  /**
   * Carga el historial desde localStorage al montar el componente
   * Maneja errores de parsing y establece mensaje inicial si es necesario
   */
  useEffect(() => {
    try {
      const stored = localStorage.getItem(CHAT_HISTORY_KEY);
      if (stored) {
        const parsedMessages = JSON.parse(stored) as ChatMessage[];
        setMessages(parsedMessages);
      } else if (initialMessage) {
        // Si no hay historial y se proporciona mensaje inicial
        setMessages([initialMessage]);
      }
    } catch (error) {
      console.error(`Error al cargar historial del chat [${chatId}]:`, error);
      if (initialMessage) {
        setMessages([initialMessage]);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chatId]); // Solo depende de chatId, CHAT_HISTORY_KEY se deriva de él

  /**
   * Guarda automáticamente el historial en localStorage cuando cambian los mensajes
   * Aplica límite de mensajes para optimizar el rendimiento
   */
  useEffect(() => {
    if (messages.length > 0) {
      try {
        // Limitar el número de mensajes para evitar que localStorage crezca demasiado
        const messagesToStore = messages.slice(-MAX_MESSAGES);
        localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(messagesToStore));
      } catch (error) {
        console.error(`Error al guardar historial del chat [${chatId}]:`, error);
      }
    }
  }, [messages, CHAT_HISTORY_KEY, chatId]);

  /**
   * Agrega un nuevo mensaje al historial
   * 
   * @param message - Datos del mensaje (sin timestamp, se agrega automáticamente)
   */
  const addMessage = (message: Omit<ChatMessage, 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      timestamp: Date.now()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  /**
   * Limpia todo el historial manteniendo el mensaje inicial si existe
   * Actualiza localStorage según corresponda
   */
  const clearHistory = () => {
    if (initialMessage) {
      setMessages([initialMessage]);
    } else {
      setMessages([]);
    }
    try {
      // Si hay mensaje inicial, guardarlo; si no, eliminar completamente
      if (initialMessage) {
        localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify([initialMessage]));
      } else {
        localStorage.removeItem(CHAT_HISTORY_KEY);
      }
    } catch (error) {
      console.error(`Error al limpiar historial del chat [${chatId}]:`, error);
    }
  };

  /**
   * Restablece el historial con un nuevo mensaje inicial
   * 
   * @param newInitialMessage - Nuevo mensaje inicial para el chat
   */
  const resetWithInitialMessage = (newInitialMessage: ChatMessage) => {
    setMessages([newInitialMessage]);
  };

  return {
    messages,                    // Array de mensajes del historial
    addMessage,                  // Función para agregar nuevos mensajes
    clearHistory,                // Función para limpiar el historial
    resetWithInitialMessage,     // Función para resetear con mensaje inicial
    hasMessages: messages.length > 0  // Indica si hay mensajes en el historial
  };
}
