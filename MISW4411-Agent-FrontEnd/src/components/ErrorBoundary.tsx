/**
 * @fileoverview ErrorBoundary Component
 * 
 * Componente de clase para capturar errores de JavaScript en cualquier parte del árbol de componentes.
 * Muestra una interfaz de error amigable al usuario cuando ocurre un error no manejado.
 * Incluye opciones para recargar la página y reportar el error.
 * 
 * @author Universidad de los Andes
 * @version 1.0.0
 */

import { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
  errorInfo?: ErrorInfo
}

/**
 * Error Boundary para capturar errores de React
 * 
 * Funcionalidades principales:
 * - Captura errores de JavaScript en el árbol de componentes
 * - Muestra interfaz de error amigable al usuario
 * - Botón para recargar la aplicación
 * - Información detallada del error en modo desarrollo
 * - Logging de errores para debugging
 * - Prevención de crashes completos de la aplicación
 * 
 * @param children - Componentes hijos a proteger
 * @returns JSX.Element
 */
class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({ error, errorInfo })
  }

  private handleReload = () => {
    window.location.reload()
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div 
          className="min-h-screen flex items-center justify-center p-4"
          style={{ backgroundColor: 'var(--bg-primary)' }}
        >
          <div className="max-w-md w-full text-center">
            <div className="mb-8">
              <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-10 h-10 text-red-500" />
              </div>
              <h1 
                className="text-2xl font-bold mb-2"
                style={{ color: 'var(--text-primary)' }}
              >
                Error en la aplicación
              </h1>
              <p 
                className="mb-6"
                style={{ color: 'var(--text-secondary)' }}
              >
                Ha ocurrido un error inesperado. Intenta recargar la página.
              </p>
            </div>

            <div className="space-y-4">
              <button
                onClick={this.handleReload}
                className="w-full px-6 py-3 text-white font-semibold rounded-lg transition-all duration-300 inline-flex items-center justify-center"
                style={{ backgroundColor: '#342276' }}
                onMouseEnter={(e) => {
                  const target = e.target as HTMLButtonElement;
                  target.style.backgroundColor = '#2d1d65';
                }}
                onMouseLeave={(e) => {
                  const target = e.target as HTMLButtonElement;
                  target.style.backgroundColor = '#342276';
                }}
              >
                <RefreshCw className="w-5 h-5 mr-2" />
                Recargar Página
              </button>
            </div>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-8 text-left">
                <summary 
                  className="cursor-pointer text-sm hover:opacity-80"
                  style={{ color: 'var(--text-secondary)' }}
                >
                  Ver detalles del error (solo desarrollo)
                </summary>
                <div 
                  className="mt-4 p-4 rounded-lg text-xs overflow-auto border border-red-200 bg-red-50"
                >
                  <pre className="text-red-700">{this.state.error.toString()}</pre>
                  <pre className="mt-2 text-red-600">{this.state.errorInfo?.componentStack}</pre>
                </div>
              </details>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary