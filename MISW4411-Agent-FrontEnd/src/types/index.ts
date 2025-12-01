/**
 * @fileoverview Tipos Básicos de la Aplicación
 * 
 * Definiciones de tipos fundamentales para la aplicación.
 * Incluye tipos para servicios, animaciones, componentes UI y estados de carga.
 * Este archivo centraliza los tipos más comunes utilizados en toda la aplicación.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

/**
 * Tipos básicos de servicios
 */

/**
 * Interfaz para servicios de la aplicación
 * Define la estructura de un servicio con sus propiedades básicas
 */
export interface Service {
  id: string          // Identificador único del servicio
  title: string       // Título del servicio
  description: string  // Descripción del servicio
  icon: string        // Nombre o ruta del icono
  color: string       // Color asociado al servicio
}

/**
 * Tipos de animación
 */

/**
 * Configuración para animaciones
 * Define parámetros para controlar el comportamiento de las animaciones
 */
export interface AnimationConfig {
  duration: number                                    // Duración en milisegundos
  delay: number                                       // Retraso inicial en milisegundos
  easing: string                                      // Función de suavizado
  direction?: 'up' | 'down' | 'left' | 'right'       // Dirección de la animación
}

/**
 * Tipos de componentes UI
 */

/**
 * Props para componentes de botón
 * Define las propiedades estándar para botones en la aplicación
 */
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline'  // Variante visual del botón
  size?: 'sm' | 'md' | 'lg'                                // Tamaño del botón
  disabled?: boolean                                        // Estado deshabilitado
  loading?: boolean                                         // Estado de carga
  children: React.ReactNode                                 // Contenido del botón
  onClick?: () => void                                      // Función de clic
  type?: 'button' | 'submit' | 'reset'                     // Tipo de botón HTML
  className?: string                                        // Clases CSS adicionales
}

/**
 * Estados de carga
 */

/**
 * Estados posibles para operaciones asíncronas
 * Define los diferentes estados que puede tener una operación de carga
 */
export type LoadingState = 'idle' | 'loading' | 'success' | 'error' 