/**
 * @fileoverview useProcessingStatus Hook
 * 
 * Hook personalizado para monitorear el estado de procesamiento de documentos.
 * Realiza polling automático para verificar el progreso de tareas de carga de documentos
 * desde URLs y mantiene el estado actualizado en tiempo real.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import { useEffect, useState } from "react";

/**
 * Estado de procesamiento de una tarea
 * Representa el estado actual de una operación de carga de documentos
 */
export interface ProcessingStatus {
  id: string;                    // ID único del procesamiento
  success?: boolean;             // Indica si el procesamiento fue exitoso
  message?: string;              // Mensaje descriptivo del estado
  error?: string;                // Mensaje de error si ocurrió algún problema
  data?: any;                    // Datos adicionales del procesamiento
  warnings?: string[];           // Lista de advertencias generadas
  timestamp?: string;            // Marca de tiempo del último estado
  loading: boolean;              // Indica si está cargando el estado actual
}

/**
 * Hook para monitorear el estado de procesamiento de documentos
 * 
 * Funcionalidades principales:
 * - Polling automático de estados de procesamiento
 * - Gestión de múltiples tareas simultáneas
 * - Recuperación automática desde localStorage
 * - Manejo de errores de red
 * - Actualización en tiempo real del estado
 * 
 * @param baseUrl - URL base del backend
 * @param intervalMs - Intervalo de polling en milisegundos (por defecto: 5000)
 * @returns Objeto con estados de todas las tareas de procesamiento
 */
export function useProcessingStatus(
  baseUrl: string,
  intervalMs: number = 5000 // cada 5 segundos
) {
  const [statuses, setStatuses] = useState<Record<string, ProcessingStatus>>({});

  useEffect(() => {
    /**
     * Obtiene todos los IDs de procesamiento guardados en localStorage
     * Busca claves que empiecen con "processing_id_"
     */
    const keys = Object.keys(localStorage).filter((k) =>
      k.startsWith("processing_id_")
    );

    const ids = keys.map((k) => localStorage.getItem(k)!).filter(Boolean);

    if (ids.length === 0) return;

    /**
     * Función para obtener el estado de un procesamiento específico
     * 
     * @param id - ID del procesamiento a consultar
     */
    async function fetchStatus(id: string) {
      try {
        // Marcar como cargando
        setStatuses((prev) => ({
          ...prev,
          [id]: { ...(prev[id] || {}), loading: true },
        }));

        // Consultar estado en el backend
        const res = await fetch(`${baseUrl}/api/v1/documents/load-from-url/${id}`);
        const data = await res.json();

        // Actualizar estado con la respuesta
        setStatuses((prev) => ({
          ...prev,
          [id]: {
            id,
            success: data.success,
            message: data.message,
            error: data.error,
            data: data.data,
            warnings: data.warnings,
            timestamp: data.timestamp,
            loading: false,
          },
        }));
      } catch (err: any) {
        // Manejar errores de red
        setStatuses((prev) => ({
          ...prev,
          [id]: {
            id,
            success: false,
            message: "Error de red al consultar estado",
            error: err.message,
            loading: false,
          },
        }));
      }
    }

    // Ejecutar consulta inmediata para todos los IDs
    ids.forEach((id) => fetchStatus(id));

    // Configurar polling automático
    const interval = setInterval(() => {
      ids.forEach((id) => fetchStatus(id));
    }, intervalMs);

    // Limpiar intervalo al desmontar
    return () => clearInterval(interval);
  }, [baseUrl, intervalMs]);

  return statuses;
}
