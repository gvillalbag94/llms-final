/**
 * @fileoverview Layout Component
 * 
 * Layout principal de la aplicación que estructura la interfaz general.
 * Incluye header, contenido principal y footer con animaciones de transición.
 * Proporciona la estructura base para todas las páginas de la aplicación.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import { ReactNode } from 'react'
import { motion } from 'framer-motion'

import Header from './Header'
import Footer from './Footer'

interface LayoutProps {
  children: ReactNode
  tab: 'rag' | 'specialized'
  setTab: (tab: 'rag' | 'specialized') => void
}

/**
 * Layout principal de la aplicación
 * 
 * Funcionalidades principales:
 * - Estructura general de la aplicación (header, main, footer)
 * - Manejo de pestañas y navegación
 * - Animaciones de transición para el contenido
 * - Diseño responsivo y consistente
 * - Variables CSS personalizadas para temas
 * - Z-index apropiado para elementos superpuestos
 * 
 * @param children - Contenido principal a renderizar
 * @param tab - Pestaña actualmente activa
 * @param setTab - Función para cambiar la pestaña activa
 * @returns JSX.Element
 */
const Layout = ({ children, tab, setTab }: LayoutProps) => {
  return (
    <div 
      className="min-h-screen relative overflow-x-hidden transition-all duration-300"
      style={{
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)'
      }}
    >
      {/* Header */}
      <Header tab={tab} setTab={setTab} />
      
      {/* Main Content */}
      <main className="relative z-10 pt-28">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
        >
          {children}
        </motion.div>
      </main>
      
      {/* Footer */}
      <Footer />
    </div>
  )
}

export default Layout
