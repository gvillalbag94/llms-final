/**
 * @fileoverview NotificationContext
 * 
 * Contexto de React para el manejo global de notificaciones del sistema.
 * Proporciona un sistema centralizado para mostrar, actualizar y gestionar notificaciones
 * de diferentes tipos (éxito, error, advertencia, información, procesamiento).
 * Incluye funcionalidades de auto-cierre, seguimiento de estado y persistencia.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import { createContext, useContext, useState, useCallback, ReactNode } from 'react';

/**
 * Tipos de notificaciones disponibles en el sistema
 */
export type NotificationType = 'success' | 'error' | 'info' | 'warning' | 'processing';

/**
 * Interfaz para representar una notificación individual
 */
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: number;
  processingId?: string;
  autoClose?: boolean;
  duration?: number; // en milisegundos
}

/**
 * Interfaz para el contexto de notificaciones
 * Define todas las funciones y propiedades disponibles para gestionar notificaciones
 */
interface NotificationContextType {
  notifications: Notification[];
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => string;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  updateNotification: (id: string, updates: Partial<Notification>) => void;
  getProcessingNotification: (processingId: string) => Notification | undefined;
  hasUnreadNotifications: boolean;
  markAllAsRead: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

/**
 * Proveedor del contexto de notificaciones
 * 
 * Funcionalidades principales:
 * - Gestión del estado global de notificaciones
 * - Auto-cierre de notificaciones según configuración
 * - Seguimiento de notificaciones no leídas
 * - Actualización dinámica de notificaciones existentes
 * - Búsqueda de notificaciones por ID de procesamiento
 * 
 * @param children - Componentes hijos que tendrán acceso al contexto
 * @returns JSX.Element
 */
export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [hasUnreadNotifications, setHasUnreadNotifications] = useState(false);

  /**
   * Agrega una nueva notificación al sistema
   * 
   * @param notificationData - Datos de la notificación (sin id ni timestamp)
   * @returns ID único de la notificación creada
   */
  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'timestamp'>) => {
    const id = `notification-${Date.now()}-${Math.random()}`;
    const notification: Notification = {
      ...notificationData,
      id,
      timestamp: Date.now(),
      autoClose: notificationData.autoClose ?? (notificationData.type === 'success'),
      duration: notificationData.duration ?? 5000,
    };

    setNotifications(prev => [notification, ...prev]);
    setHasUnreadNotifications(true);

    // Auto-close si está configurado
    if (notification.autoClose) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration);
    }

    return id;
  }, []);

  /**
   * Elimina una notificación específica por su ID
   * 
   * @param id - ID de la notificación a eliminar
   */
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  /**
   * Elimina todas las notificaciones del sistema
   */
  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
    setHasUnreadNotifications(false);
  }, []);

  /**
   * Actualiza una notificación existente con nuevos datos
   * 
   * @param id - ID de la notificación a actualizar
   * @param updates - Datos parciales para actualizar la notificación
   */
  const updateNotification = useCallback((id: string, updates: Partial<Notification>) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, ...updates, timestamp: Date.now() }
          : notification
      )
    );
    
    if (updates.type === 'success' || updates.type === 'error') {
      setHasUnreadNotifications(true);
    }
  }, []);

  /**
   * Busca una notificación por su ID de procesamiento
   * 
   * @param processingId - ID del procesamiento asociado
   * @returns La notificación encontrada o undefined
   */
  const getProcessingNotification = useCallback((processingId: string) => {
    return notifications.find(n => n.processingId === processingId);
  }, [notifications]);

  /**
   * Marca todas las notificaciones como leídas
   */
  const markAllAsRead = useCallback(() => {
    setHasUnreadNotifications(false);
  }, []);

  const value: NotificationContextType = {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    updateNotification,
    getProcessingNotification,
    hasUnreadNotifications,
    markAllAsRead,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

/**
 * Hook personalizado para acceder al contexto de notificaciones
 * 
 * Funcionalidades principales:
 * - Proporciona acceso a todas las funciones de gestión de notificaciones
 * - Valida que el hook se use dentro del NotificationProvider
 * - Lanza error si se usa fuera del contexto apropiado
 * 
 * @returns Objeto con todas las funciones y estado del contexto de notificaciones
 * @throws Error si se usa fuera del NotificationProvider
 */
export function useNotifications() {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
}
