/**
 * @fileoverview Main Entry Point
 * 
 * Punto de entrada principal de la aplicación React.
 * Configura el renderizado de la aplicación, proveedores de contexto
 * y configuraciones iniciales del tema y DOM.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { HelmetProvider } from 'react-helmet-async'

import App from './App.tsx'
import './styles/index.css'

/**
 * Configuración inicial del tema
 * Establece el modo claro como predeterminado y elimina cualquier clase de modo oscuro
 */
document.documentElement.classList.add('light')
document.documentElement.classList.remove('dark')

/**
 * Renderizado de la aplicación React
 * 
 * Configuración:
 * - React.StrictMode: Habilita verificaciones adicionales en desarrollo
 * - HelmetProvider: Permite gestión dinámica de metadatos HTML
 * - App: Componente principal de la aplicación
 */
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HelmetProvider>
      <App />
    </HelmetProvider>
  </React.StrictMode>,
) 