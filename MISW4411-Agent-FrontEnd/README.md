# 202515 MISW4411 Agent Frontend Template

Plantilla de interfaz web React + TypeScript para el curso **Construcción de Aplicaciones basadas en Grandes Modelos de Lenguaje (MISW4411)** de la **Maestría en Ingeniería de Software – Universidad de los Andes**.

## Tabla de Contenido

- [Descripción](#descripción)
- [Características](#características)
- [Inicio Rápido](#inicio-rápido)
- [Personalización](#personalización)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Integración con API](#integración-con-api)
- [Solución de Problemas](#solución-de-problemas)
- [Implementación Personalizada](#implementación-personalizada)

## Descripción

Este template proporciona una interfaz web completa y funcional para interactuar con el backend de su proyecto 2 sobre Agentes RAG y Agente Especializado, haciendo uso del protocolo MCP

**Objetivo principal**: Facilitar la creación de videos de demostración para las entregas del curso, proporcionando una interfaz profesional y lista para usar.

## Características

- **React 18 + TypeScript** - Desarrollo moderno y tipado estático
- **Tailwind CSS** - Diseño elegante y responsivo
- **Interfaz adaptativa** - Funciona en desktop, tablet y móvil
- **Configuración sencilla** - Un solo archivo para personalizar todo
- **Panel de metadatos** - Información detallada sobre consultas RAG
- **Soporte Markdown** - Renderizado de respuestas complejas
- **Lista para usar** - Configuración mínima requerida

## Inicio Rápido

### 1. Fork del repositorio

```bash
# 1. Crear fork desde GitHub
# Ve a: https://github.com/MISW4411-Aplicaciones-basadas-en-LLMs/202515-MISW4411-Agent-Frontend-Template
# Haz clic en "Fork" en la esquina superior derecha
# Esto creará una copia en su cuenta de GitHub

# 2. Clonar SU fork (no el original)
git clone https://github.com/MISW4411-Aplicaciones-basadas-en-LLMs/202515-MISW4411-Agent-Frontend-Template.git
cd 202515-MISW4411-Agent-Frontend-Template
```

### 2. Instalar dependencias

```bash
npm install
```

### 3. Configurar el proyecto

Editar el archivo `src/config/appConfig.ts` con la información de su grupo:

```typescript
export const APP_CONFIG = {
  // ========== INFORMACIÓN DE SU PROYECTO ==========
  PROJECT_NAME: "Asistente RAG Grupo X",
  GROUP_NUMBER: "Grupo X", 
  STUDENT_NAMES: "Estudiante A - Estudiante B",
  
  // ========== DESCRIPCIÓN ==========
  DESCRIPTION: "Describa su sistema RAG aquí",
  
  // ========== CONFIGURACIÓN DEL BACKEND ==========
  BACKEND_URL: "http://localhost:8000",      // URL de su API
  RAG_ENDPOINT: "/ask_rag",                  // Endpoint del Agente RAG
  CUSTOM_ENDPOINT: "/ask_custom",            // Endpoint del Agente Especializado
};
```

### 4. Ejecutar el proyecto

```bash
npm run dev
```

Abrir [http://localhost:3000](http://localhost:3000) en el navegador.

## Personalización

### Configuración Principal

Todo el comportamiento del frontend se controla desde `src/config/appConfig.ts`:

```typescript
export const APP_CONFIG = {
  // ========== INFORMACIÓN DEL PROYECTO ==========
  PROJECT_NAME: "Nombre de su proyecto",    // Aparece en el título principal
  GROUP_NUMBER: "Grupo X",                  // Opcional: número de grupo
  STUDENT_NAMES: "Nombre A - Nombre B",     // Opcional: integrantes del equipo
  
  // ========== DESCRIPCIÓN ==========
  DESCRIPTION: "Descripción de su sistema", // Subtítulo explicativo
  
  // ========== CONFIGURACIÓN DEL CHAT ==========
  INITIAL_BOT_MESSAGE: "Mensaje inicial del bot",
  INPUT_PLACEHOLDER: "Placeholder del input de texto",
  
  // ========== CONFIGURACIÓN DEL BACKEND ==========
  BACKEND_URL: "http://localhost:8000",     // URL base de su API (Docker container)
  RAG_ENDPOINT: "/ask_rag",                 // Endpoint del Agente RAG
  CUSTOM_ENDPOINT: "/ask_custom",           // Endpoint del Agente Especializado
};
```

### Personalización Avanzada

Si desean hacer cambios más profundos:

- **Estilos**: Modificar archivos en `src/styles/`
- **Componentes**: Editar componentes en `src/components/`
- **Tipos**: Actualizar interfaces en `src/types/`

## Estructura del Proyecto

```
src/
├── components/              # Componentes React
│   ├── ChatRAG.tsx         # 💬 Interfaz del Agente RAG
│   ├── ChatSpecialized.tsx # 🤖 Interfaz del Agente Especializado
│   ├── Header.tsx          # 🔝 Barra de navegación
│   ├── Footer.tsx          # 👇 Pie de página institucional
│   ├── Layout.tsx          # 📐 Layout general de la aplicación
│   └── NotificationCenter.tsx  # 🔔 Centro de notificaciones
├── config/
│   └── appConfig.ts        # ⚙️ CONFIGURACIÓN PRINCIPAL - EDITAR AQUÍ
├── types/
│   └── rag.ts              # 🔧 Tipos TypeScript para API
├── hooks/                  # 🎣 Custom hooks React
├── contexts/               # 📦 Contextos de React
├── styles/                 # 🎨 Estilos y configuración CSS
├── App.tsx                 # 🚀 Componente raíz
└── main.tsx                # 🏁 Punto de entrada de la aplicación
```

## Integración con API

### Estructura de la Petición

El frontend envía peticiones POST a dos endpoints diferentes según el agente:

#### Agente RAG (`/ask_rag`)

```typescript
// Petición enviada al Agente RAG
{
  "question": "Pregunta del usuario"
}
```

#### Agente Especializado (`/ask_custom`)

```typescript
// Petición enviada al Agente Especializado
{
  "question": "Pregunta del usuario"
}
```

Ambos endpoints esperan el mismo formato de petición según `FRONTEND_INTEGRATION.md`

### Estructura de la Respuesta

#### Respuesta del Agente RAG (`/ask_rag`)

```typescript
// Respuesta esperada del Agente RAG
{
  "answer": "Respuesta generada por el modelo"
}
```

**Nota**: El Agente RAG puede incluir campos adicionales opcionales como `files_consulted`, `context_docs`, y `response_time_sec` que serán mostrados en el panel de metadatos si están disponibles.

#### Respuesta del Agente Especializado (`/ask_custom`)

```typescript
// Respuesta esperada del Agente Especializado
{
  "answer": "Respuesta generada por el modelo"
}
```

Ambos endpoints devuelven el mismo formato básico de respuesta según `FRONTEND_INTEGRATION.md`

## Solución de Problemas

### ❌ Error de CORS

```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solución**: Configurar CORS en su backend FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ❌ Backend no responde

**Verificar**:

1. ✅ El backend está ejecutándose en la URL configurada (por defecto `http://localhost:8000`)
2. ✅ La `BACKEND_URL` en `appConfig.ts` es correcta
3. ✅ Los endpoints `/ask_rag` y `/ask_custom` existen y funcionan
4. ✅ El backend devuelve JSON válido con el campo `answer`
5. ✅ No hay errores en la consola del backend

### ❌ Error 404 - Endpoint not found

**Solución**:

1. Verificar que el backend tiene implementados los endpoints `/ask_rag` y `/ask_custom`
2. Confirmar que el contenedor Docker del backend está corriendo
3. Verificar los logs del backend con `docker-compose logs -f app`

### ❌ Error 422 - Validation Error

**Posibles causas**:

- Estructura de petición incorrecta
- Campos requeridos faltantes
- Tipos de datos incorrectos

**Verificar**: Que su backend acepta la estructura de datos descrita en [Integración con API](#integración-con-api).

## Implementación Personalizada

Esta plantilla está diseñada para ser funcional sin modificaciones, pero **no es restrictiva**. Si su grupo prefiere una implementación diferente del frontend, pueden:

### Opciones alternativas

1. **Usar este template**: Configurar solo `appConfig.ts` (recomendado)
2. **Modificar componentes**: Personalizar la interfaz según sus necesidades

### Consideraciones importantes

- **Tiempo de desarrollo**: Una implementación personalizada requiere tiempo adicional que podría ser mejor invertido en el backend
- **Enfoque del curso**: El objetivo es dominar los conceptos de LLMs, no desarrollo frontend
- **Videos de entrega**: Esta plantilla ya proporciona una interfaz profesional para demostraciones

### Recomendación

Sugerimos usar esta plantilla con configuración mínima para maximizar el tiempo disponible para los aspectos centrales del curso relacionados con Grandes Modelos de Lenguaje.

---

**🎓 Curso**: MISW4411 - Construcción de Aplicaciones basadas en Grandes Modelos de Lenguaje
**🏛️ Universidad**: Universidad de los Andes - Maestría en Ingeniería de Software
**📅 Año**: 2025
