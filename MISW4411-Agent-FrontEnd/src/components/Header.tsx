/**
 * @fileoverview Header Component
 * 
 * Cabecera principal de la aplicación con navegación entre pestañas.
 * Incluye el título de la aplicación, botones de navegación y el centro de notificaciones.
 * Utiliza animaciones de Framer Motion para transiciones suaves.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import { motion } from 'framer-motion';
import { HelpCircle } from 'lucide-react';
import NotificationCenter from './NotificationCenter';

type HeaderProps = {
  tab: 'rag' | 'specialized';
  setTab: (tab: 'rag' | 'specialized') => void;
};

/**
 * Cabecera de la aplicación
 * 
 * Funcionalidades principales:
 * - Navegación entre pestañas (Agente RAG y Agente Especializado)
 * - Título dinámico de la aplicación
 * - Centro de notificaciones integrado
 * - Diseño responsivo y fijo en la parte superior
 * - Animaciones de entrada y transiciones suaves
 * - Estilo consistente con la identidad visual del proyecto
 * 
 * @param tab - Pestaña actualmente activa
 * @param setTab - Función para cambiar la pestaña activa
 * @returns JSX.Element
 */
const Header = ({ tab, setTab }: HeaderProps) => {
  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
      style={{
        backgroundColor: '#342276',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      }}
    >
      <div className="container-custom">
        <div className="flex items-center justify-between h-20 lg:h-24">
          {/* Logo Izquierdo */}
          <div className="flex items-center gap-4">
            <img 
              src="/assets/MisoLogo.png" 
              alt="MISO Logo" 
              className="h-12 md:h-14 lg:h-16 object-contain"
            />

            {/* Botones de tabs */}
            <nav className="flex gap-2">
              {/* Agente RAG con tooltip */}
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setTab('rag')}
                  className={`px-3 py-1.5 rounded text-sm font-medium ${
                    tab === 'rag'
                      ? 'bg-white text-[#342276]'
                      : 'bg-[#2d1d65] text-white hover:bg-[#261854]'
                  }`}
                >
                  Agente RAG
                </button>
                <div className="relative group">
                  <HelpCircle 
                    className="w-4 h-4 text-white cursor-help" 
                  />
                  <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 px-3 py-1.5 bg-gray-900 text-white text-xs rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                    Agente Semana 6
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 border-4 border-transparent border-b-gray-900"></div>
                  </div>
                </div>
              </div>

              {/* Agente Especializado con tooltip */}
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setTab('specialized')}
                  className={`px-3 py-1.5 rounded text-sm font-medium ${
                    tab === 'specialized'
                      ? 'bg-white text-[#342276]'
                      : 'bg-[#2d1d65] text-white hover:bg-[#261854]'
                  }`}
                >
                  Agente Especializado
                </button>
                <div className="relative group">
                  <HelpCircle 
                    className="w-4 h-4 text-white cursor-help" 
                  />
                  <div className="absolute left-1/2 -translate-x-1/2 top-full mt-2 px-3 py-1.5 bg-gray-900 text-white text-xs rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-50">
                    Agente Semana 7
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 border-4 border-transparent border-b-gray-900"></div>
                  </div>
                </div>
              </div>
            </nav>
          </div>

          {/* Logo Derecho y Notificaciones */}
          <div className="flex items-center gap-4">
            <NotificationCenter />
            <img 
              src="/assets/UniandesDISCLogo.png" 
              alt="Universidad de los Andes Facultad Logo" 
              className="h-12 md:h-14 lg:h-16 object-contain"
            />
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
