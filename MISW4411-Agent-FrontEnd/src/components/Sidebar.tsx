/**
 * @fileoverview Sidebar Component
 * 
 * Barra lateral deslizable con opciones de navegación y configuración.
 * Incluye enlaces a diferentes secciones de la aplicación y opciones de ayuda.
 * Utiliza animaciones de Framer Motion para transiciones suaves de entrada y salida.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MessageSquare, Settings, HelpCircle } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * Barra lateral de navegación
 * 
 * Funcionalidades principales:
 * - Panel deslizable desde la derecha
 * - Enlaces de navegación a diferentes secciones
 * - Botón de cierre con animación
 * - Overlay de fondo para cerrar al hacer clic fuera
 * - Animaciones suaves de entrada y salida
 * - Diseño responsivo y accesible
 * 
 * @param isOpen - Estado de apertura del sidebar
 * @param onClose - Función para cerrar el sidebar
 * @returns JSX.Element
 */
const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const sidebarVariants = {
    closed: {
      x: '100%',
      transition: {
        type: 'tween',
        duration: 0.3,
        ease: 'easeInOut'
      }
    },
    open: {
      x: 0,
      transition: {
        type: 'tween',
        duration: 0.3,
        ease: 'easeInOut'
      }
    }
  };

  const overlayVariants = {
    closed: { opacity: 0 },
    open: { opacity: 1 }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay */}
          <motion.div
            variants={overlayVariants}
            initial="closed"
            animate="open"
            exit="closed"
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          />

          {/* Sidebar */}
          <motion.div
            variants={sidebarVariants}
            initial="closed"
            animate="open"
            exit="closed"
            className="fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-50 lg:hidden overflow-y-auto border-l border-gray-200"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <div 
                  className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: '#342276' }}
                >
                  <span className="text-white font-bold text-sm">M</span>
                </div>
                <span className="text-lg font-bold" style={{ color: '#342276' }}>
                  MISW4411
                </span>
              </div>
              <motion.button
                onClick={onClose}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-10 h-10 rounded-lg flex items-center justify-center transition-colors hover:bg-gray-100"
              >
                <X className="w-5 h-5 text-gray-500" />
              </motion.button>
            </div>

            {/* Content */}
            <div className="p-6">
              <div className="space-y-4">
                <div className="flex items-center space-x-3 text-gray-700">
                  <MessageSquare className="w-5 h-5" style={{ color: '#342276' }} />
                  <span className="font-medium">Chat Principal</span>
                </div>
                
                <div className="flex items-center space-x-3 text-gray-700">
                  <Settings className="w-5 h-5" style={{ color: '#342276' }} />
                  <span className="font-medium">Configuración</span>
                </div>
                
                <div className="flex items-center space-x-3 text-gray-700">
                  <HelpCircle className="w-5 h-5" style={{ color: '#342276' }} />
                  <span className="font-medium">Ayuda</span>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-auto p-6 border-t border-gray-200">
              <div className="text-center">
                <p className="text-sm text-gray-600">
                  Curso MISW4411
                </p>
                <p className="text-xs text-gray-500">
                  Universidad de los Andes
                </p>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default Sidebar;