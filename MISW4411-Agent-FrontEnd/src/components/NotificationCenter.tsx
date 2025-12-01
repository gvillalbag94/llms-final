/**
 * @fileoverview NotificationCenter Component
 * 
 * Componente para mostrar y gestionar notificaciones del sistema.
 * Incluye un panel deslizable con notificaciones de diferentes tipos (éxito, error, advertencia, procesamiento).
 * Permite marcar como leídas, eliminar individuales y limpiar todas las notificaciones.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import React, { useState } from 'react';
import { useNotifications, type Notification, type NotificationType } from '../contexts/NotificationContext';

/**
 * Centro de notificaciones del sistema
 * 
 * Funcionalidades principales:
 * - Panel deslizable con lista de notificaciones
 * - Diferentes tipos de notificaciones (success, error, warning, processing)
 * - Indicador de notificaciones no leídas
 * - Botones para marcar como leídas y limpiar todas
 * - Animaciones suaves de entrada y salida
 * - Auto-cierre de notificaciones según configuración
 * 
 * @returns JSX.Element
 */
const NotificationCenter: React.FC = () => {
  const { 
    notifications, 
    removeNotification, 
    clearAllNotifications, 
    hasUnreadNotifications,
    markAllAsRead 
  } = useNotifications();
  
  const [isOpen, setIsOpen] = useState(false);

  const togglePanel = () => {
    const wasOpen = isOpen;
    setIsOpen(!isOpen);

    if (!wasOpen && hasUnreadNotifications) {
      markAllAsRead();
    }
  };

  const getIconForType = (type: NotificationType) => {
    switch (type) {
      case 'success':
        return (
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      case 'processing':
        return (
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-blue-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
        );
      case 'warning':
        return (
          <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
        );
      default:
        return (
          <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
    }
  };

  const formatTime = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    
    if (minutes < 1) return 'Ahora';
    if (minutes < 60) return `Hace ${minutes}m`;
    if (hours < 24) return `Hace ${hours}h`;
    return new Date(timestamp).toLocaleDateString();
  };

  const hasNotifications = notifications.length > 0;

  return (
    <>
      {/* Botón del notification center */}
      <div className="relative">
        <button
          onClick={togglePanel}
          className="relative p-2 text-white hover:bg-white/10 rounded-lg transition-colors duration-200"
          title="Notificaciones"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          

          {hasUnreadNotifications && (
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
          )}
        </button>
      </div>

      {/* Panel deslizable */}
      {isOpen && (
        <>
          {/* Overlay */}
          <div 
            className="fixed inset-0 bg-black/20 z-40"
            onClick={() => setIsOpen(false)}
          />
          
          {/* Panel */}
          <div className="fixed top-0 right-0 h-full w-96 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200" style={{ backgroundColor: '#342276' }}>
              <h3 className="text-lg font-semibold text-white">Notificaciones</h3>
              <div className="flex items-center gap-2">
                {hasNotifications && (
                  <button
                    onClick={clearAllNotifications}
                    className="text-sm text-white/80 hover:text-white px-2 py-1 rounded hover:bg-white/10"
                  >
                    Limpiar todo
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:bg-white/10 p-1 rounded"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Contenido */}
            <div className="flex-1 overflow-y-auto h-full pb-4">
              {hasNotifications ? (
                <div className="space-y-2 p-4">
                  {notifications.map((notification) => (
                    <NotificationItem
                      key={notification.id}
                      notification={notification}
                      onRemove={removeNotification}
                      formatTime={formatTime}
                      getIconForType={getIconForType}
                    />
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-500">
                  <svg className="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  <p className="text-sm font-medium">No hay notificaciones</p>
                  <p className="text-xs text-gray-400">Aparecerán aquí cuando tengas nuevas actualizaciones</p>
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
};

// Componente individual de notificación
const NotificationItem: React.FC<{
  notification: Notification;
  onRemove: (id: string) => void;
  formatTime: (timestamp: number) => string;
  getIconForType: (type: NotificationType) => React.ReactNode;
}> = ({ notification, onRemove, formatTime, getIconForType }) => {
  return (
    <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 hover:bg-gray-100 transition-colors duration-200">
      <div className="flex items-start gap-3">
        {getIconForType(notification.type)}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <h4 className="text-sm font-semibold text-gray-900 truncate">
              {notification.title}
            </h4>
            <button
              onClick={() => onRemove(notification.id)}
              className="text-gray-400 hover:text-gray-600 ml-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <p className="text-sm text-gray-600 mt-1 break-words">
            {notification.message}
          </p>
          {notification.processingId && (
            <p className="text-xs text-gray-500 mt-1 font-mono">
              ID: {notification.processingId}
            </p>
          )}
          <p className="text-xs text-gray-400 mt-2">
            {formatTime(notification.timestamp)}
          </p>
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter;
