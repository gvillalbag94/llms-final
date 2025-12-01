/**
 * @fileoverview Vite Environment Types
 * 
 * Declaraciones de tipos para variables de entorno de Vite.
 * Define las variables de entorno disponibles en la aplicación
 * y extiende los tipos de Vite para mejor integración con TypeScript.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

/// <reference types="vite/client" />

/**
 * Variables de entorno disponibles en la aplicación
 * Todas las variables deben tener el prefijo VITE_ para ser accesibles en el cliente
 */
interface ImportMetaEnv {
  readonly VITE_EMAILJS_SERVICE_ID: string    // ID del servicio de EmailJS
  readonly VITE_EMAILJS_TEMPLATE_ID: string  // ID de la plantilla de EmailJS
  readonly VITE_EMAILJS_PUBLIC_KEY: string   // Clave pública de EmailJS
}

/**
 * Interfaz extendida de ImportMeta para incluir variables de entorno
 * Proporciona acceso tipado a las variables de entorno a través de import.meta.env
 */
interface ImportMeta {
  readonly env: ImportMetaEnv
}
