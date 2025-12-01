# Documentación Completa del Proyecto - Grupo 21

## Información del Proyecto

**Curso**: MISW4411 - Construcción de Aplicaciones basadas en Grandes Modelos de Lenguaje  
**Institución**: Universidad de los Andes - Maestría en Ingeniería de Software  
**Año**: 2025-1  
**Grupo**: 21  
**Integrantes**:
- Gabriel Felipe Villalba Gil

---

## 📖 1. Descripción del Proyecto

### 1.1 Problema que Resuelve

Los desarrolladores de software frecuentemente necesitan consultar documentación oficial de lenguajes de programación, frameworks y librerías. Este proceso puede ser:

- **Lento**: Requiere navegar múltiples páginas web y documentos
- **Ineficiente**: La información está dispersa en diferentes fuentes
- **Complejo**: Encontrar información específica sobre versiones, breaking changes y migraciones requiere tiempo

### 1.2 Solución Propuesta

Hemos desarrollado un **Asistente Inteligente** que combina:

1. **Sistema RAG (Retrieval Augmented Generation)**: Para consultar documentación cargada previamente
2. **Agente Especializado con MCP**: Para consultar información en tiempo real sobre paquetes Python, changelogs y migraciones

### 1.3 Caso de Uso

**Escenario Principal**: Un desarrollador necesita:
- Consultar documentación técnica de Python, frameworks o librerías
- Obtener información sobre cambios entre versiones de paquetes
- Identificar breaking changes y guías de migración
- Acceder rápidamente a información específica sin navegar múltiples fuentes

**Servicios que Provee**:
- **Agente RAG**: Consultas sobre documentación cargada en el sistema
- **Agente Especializado**: Consultas sobre paquetes Python, changelogs y migraciones usando herramientas MCP

---

## 2. Arquitectura del Sistema

### 2.1 Arquitectura General

El sistema está compuesto por **tres componentes principales**:

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│              (React + TypeScript + Tailwind)                 │
│                    Puerto: 3000                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP/REST
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              AGENT BACKEND (FastAPI)                         │
│                    Puerto: 8001                              │
│  ┌──────────────────┐      ┌──────────────────┐           │
│  │   RAG Agent      │      │ Custom Agent      │           │
│  │  (LangGraph)     │      │  (LangGraph)      │           │
│  └────────┬─────────┘      └────────┬──────────┘           │
│           │                         │                       │
│           │ MCP                     │ MCP                   │
│  ┌────────▼─────────┐      ┌───────▼──────────┐           │
│  │  RAG MCP Server  │      │ Custom MCP Server│           │
│  └────────┬─────────┘      └───────┬──────────┘           │
└───────────┼────────────────────────┼───────────────────────┘
            │                        │
            │ HTTP                   │ HTTP/PyPI API
            │                        │
┌───────────▼────────────────────────▼───────────────────────┐
│              RAG BACKEND (FastAPI)                        │
│                    Puerto: 8000                            │
│  ┌──────────────────────────────────────────┐            │
│  │  Services:                                │            │
│  │  - Chunking Service                       │            │
│  │  - Embedding Service                      │            │
│  │  - Retrieval Service                      │            │
│  │  - Generation Service                    │            │
│  └──────────────────────────────────────────┘            │
│  ┌──────────────────────────────────────────┐            │
│  │  ChromaDB Vector Store                    │            │
│  │  (Base de datos vectorial)                │            │
│  └──────────────────────────────────────────┘            │
└───────────────────────────────────────────────────────────┘
```

### 2.2 Componentes Principales

#### **Frontend (React + TypeScript)**
- **Tecnología**: React 18, TypeScript, Tailwind CSS
- **Funcionalidad**: Interfaz de usuario para interactuar con ambos agentes
- **Características**:
  - Chat interactivo para Agente RAG
  - Chat interactivo para Agente Especializado
  - Panel de metadatos con información de consultas
  - Diseño responsivo

#### **Agent Backend (FastAPI)**
- **Tecnología**: FastAPI, LangGraph, MCP (Model Context Protocol)
- **Funcionalidad**: Orquestación de agentes inteligentes
- **Componentes**:
  - **RAG Agent**: Flujo lineal que consulta el sistema RAG externo
  - **Custom Agent**: Flujo ReAct cíclico con múltiples herramientas

#### **RAG Backend (FastAPI)**
- **Tecnología**: FastAPI, LangChain, ChromaDB, Google Gemini
- **Funcionalidad**: Sistema RAG completo para procesamiento de documentos
- **Componentes**:
  - **Chunking Service**: Fragmentación de documentos
  - **Embedding Service**: Generación de vectores
  - **Retrieval Service**: Búsqueda semántica y reranking
  - **Generation Service**: Generación de respuestas y query rewriting

---

## 🔧 3. Decisiones de Ingeniería

### 3.1 Estrategia de Chunking

**Estrategia Principal**: `RecursiveCharacterTextSplitter`

**Justificación**:
- **Respeto a la estructura**: Divide el texto usando separadores jerárquicos (`\n\n`, `\n`, ` `, ``)
- **Mantiene contexto**: El overlap de 200 caracteres preserva información entre chunks
- **Flexibilidad**: Se adapta a diferentes tipos de documentos (PDFs, markdown, texto plano)

**Parámetros Configurados**:
- `chunk_size`: 1000 caracteres
- `chunk_overlap`: 200 caracteres
- `separators`: `["\n\n", "\n", " ", ""]`

**Estrategias Adicionales Implementadas**:
1. **Semantic Chunking**: Basado en embeddings para agrupar contenido semánticamente similar
2. **Fixed Size Chunking**: Para control preciso del tamaño
3. **Document Structure Chunking**: Respeta la estructura jerárquica del documento
4. **Linguistic Units Chunking**: Usa NLTK para dividir en oraciones

**Impacto en la Calidad del Retrieval**:
-  Mejora la precisión al mantener párrafos completos
-  Reduce fragmentación de conceptos relacionados
-  Facilita la recuperación de contexto relevante

### 3.2 Técnicas de Re-ranking

**Modelo Utilizado**: `cross-encoder/ms-marco-MiniLM-L-6-v2`

**Justificación**:
- **Cross-Encoder**: Evalúa la relevancia considerando tanto la query como el documento simultáneamente
- **Especializado en Reranking**: Entrenado específicamente para tareas de reranking en MS MARCO
- **Eficiencia**: Modelo ligero que balancea calidad y velocidad

**Implementación**:
```python
# Lazy loading del modelo
reranker_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Calcular scores de relevancia
pairs = [(query, doc.page_content) for doc in documents]
scores = reranker_model.predict(pairs)

# Reordenar por score descendente
documents.sort(key=lambda d: d.metadata.get("rerank_score", 0), reverse=True)
```

**Beneficios Observados**:
-  Mejora la precisión del top-k: documentos más relevantes aparecen primero
-  Reduce ruido: documentos menos relevantes se desplazan hacia abajo
-  Aumenta la calidad de las respuestas generadas

**Comparación con Resultados sin Re-ranking**:
- **Sin reranking**: Los resultados dependen únicamente de la similitud coseno de embeddings
- **Con reranking**: Los resultados se reordenan considerando la relevancia semántica específica de la query

### 3.3 Query / Prompt Rewriting

**Técnica Implementada**: Query Expansion + Refinement

**Justificación**:
- **Expansión de términos**: Añade sinónimos y términos relacionados
- **Refinamiento**: Reformula consultas vagas para hacerlas más específicas
- **Mejora de recuperación**: Consultas mejoradas recuperan documentos más relevantes

**Implementación**:
```python
def rewrite_query(self, question: str) -> str:
    # Prompt para expansión y refinamiento
    rewrite_prompt = ChatPromptTemplate.from_template("""
    Eres un experto en reformulación de consultas para sistemas de búsqueda.
    
    INSTRUCCIONES:
    1. Expande la consulta con términos relacionados y sinónimos
    2. Reformula para que sea más específica y enfocada
    3. Mantén el significado original
    4. Retorna ÚNICAMENTE la consulta reescrita
    """)
    
    # Usar LLM para reescribir
    response = self.llm.invoke(rewrite_prompt.invoke({"question": question}))
    return response.content.strip()
```

**Cómo Aporta Claridad**:
-  Consultas vagas se vuelven específicas: "Python" → "Python programación sintaxis características"
-  Consultas ambiguas se clarifican: "cómo usar" → "cómo utilizar implementar ejemplo código"
-  Mejora la recuperación de documentos técnicos

### 3.4 Selección de Herramientas (MCP)

**Herramientas Integradas**:

#### **RAG Agent - Herramienta `ask`**:
- **Propósito**: Consultar el sistema RAG externo
- **Por qué como tool**: Permite al agente decidir cuándo consultar el RAG, manteniendo el flujo flexible

#### **Custom Agent - Herramientas**:
1. **`ask_rag`**: Consulta al sistema RAG (reutilización)
2. **`get_package_changelog`**: Obtiene changelogs entre versiones de paquetes Python
3. **`get_package_info`**: Obtiene información general de paquetes Python

**Por qué se definieron como Tools y no como parte del Prompt**:
-  **Modularidad**: Cada herramienta es independiente y reutilizable
-  **Decisión dinámica**: El LLM decide qué herramienta usar según el contexto
-  **Extensibilidad**: Fácil agregar nuevas herramientas sin modificar el prompt
-  **Separación de responsabilidades**: El LLM razona, las tools ejecutan

### 3.5 Implementación del Agente en LangGraph

#### **RAG Agent - Grafo Lineal**

**Estructura**:
```
Entry Point → [ask] → [llm] → END
```

**Nodos**:
1. **`ask`**: Invoca herramienta MCP `ask()` para consultar RAG
2. **`llm`**: Genera respuesta formateada usando el contexto recuperado

**Estado**:
```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    question: str
    rag_response: str
    final_answer: str
```

**Características**:
- Flujo determinístico (sin ramificaciones)
- No usa `bind_tools` (herramienta específica recibida como parámetro)

#### **Custom Agent - Grafo ReAct Cíclico**

**Estructura**:
```
Entry Point → [agent] ──┐
                        │
                        ├─→ [tools] ──┐
                        │            │
                        └────────────┘
                        (ciclo hasta completar)
```

**Nodos**:
1. **`agent`**: LLM razona y decide qué hacer (puede usar tools o responder)
2. **`tools`**: Ejecuta herramientas solicitadas por el LLM

**Aristas Condicionales**:
```python
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    if last_message.tool_calls:
        return "tools"  # Continuar con herramientas
    else:
        return "end"    # Terminar (respuesta final)
```

**Lógica de Decisión**:
- Si el LLM solicita tools → va a nodo `tools`
- Si el LLM responde directamente → termina (END)
- Después de ejecutar tools → vuelve a `agent` para continuar razonando

**Uso de Memoria Persistente**:
- El estado `messages` mantiene todo el historial de la conversación
- Incluye: mensajes del usuario, respuestas del LLM, resultados de tools
- Permite al LLM razonar sobre resultados previos

**Ciclos de Retroalimentación**:
- El agente puede ejecutar múltiples herramientas en secuencia
- Cada resultado de tool se agrega al estado
- El LLM analiza resultados y decide siguientes pasos
- El ciclo continúa hasta que el LLM decide que tiene suficiente información

---

##  4. Análisis Crítico de la Solución

### 4.1 Ventajas del Producto

1. **Acceso Rápido a Documentación**: Los desarrolladores pueden consultar información técnica sin navegar múltiples fuentes
2. **Información sobre Migraciones**: El agente especializado ayuda a identificar breaking changes y guías de migración
3. **Interfaz Intuitiva**: Chat conversacional fácil de usar
4. **Arquitectura Modular**: Fácil agregar nuevas herramientas y funcionalidades

### 4.2 Limitaciones Técnicas y Funcionales

1. **Dependencia de Documentos Cargados**: El RAG solo puede responder sobre documentos previamente cargados
2. **Limitado a Python**: Las herramientas MCP actualmente solo soportan paquetes Python (PyPI)
3. **Latencia**: El reranking y query rewriting aumentan el tiempo de respuesta
4. **Costo de LLM**: Cada consulta consume tokens del modelo Gemini

### 4.3 Riesgos o Restricciones Identificadas

1. **Rate Limits de Google AI**: 
   - Free tier: 100 requests/minuto para embeddings
   - Puede limitar el procesamiento de grandes colecciones

2. **Calidad de Chunking**:
   - Documentos mal estructurados pueden generar chunks de baja calidad
   - PDFs complejos pueden requerir preprocesamiento adicional

3. **Precisión del RAG**:
   - Depende de la calidad de los embeddings
   - Puede recuperar documentos no relevantes si la query es ambigua

### 4.4 ¿Qué Falta para Llevar el Sistema a Producción?

#### **Seguridad**:
-  **Autenticación**: No hay sistema de autenticación de usuarios
-  **Autorización**: No hay control de acceso a colecciones
-  **Protección de Endpoints**: Endpoints expuestos sin rate limiting
-  **Recomendación**: Implementar JWT, OAuth2, o API keys

#### **HITL (Human In The Loop)**:
-  **Supervisión de Respuestas**: No hay mecanismo para que usuarios reporten respuestas incorrectas
-  **Validación de Documentos**: No hay revisión humana antes de cargar documentos
-  **Recomendación**: Implementar sistema de feedback y moderación

#### **Costos**:
-  **Consumo de LLM**: Cada consulta genera costos (Gemini API)
-  **Almacenamiento**: ChromaDB crece con cada colección
-  **Infraestructura**: VM en GCP tiene costos mensuales
-  **Optimizaciones Futuras**:
  - Cache de respuestas frecuentes
  - Batch processing para embeddings
  - Compresión de vectores

#### **Funcionalidades No Implementadas**:
-  **Búsqueda Multi-colección**: No se puede consultar múltiples colecciones simultáneamente
-  **Historial de Conversaciones**: No se persiste el historial de consultas
-  **Exportación de Resultados**: No se pueden exportar respuestas o documentos consultados
-  **Búsqueda Avanzada**: No hay filtros por fecha, autor, tipo de documento

#### **Ajustes Técnicos para Robustecer el Sistema**:
-  **Manejo de Errores**: Mejorar mensajes de error y recuperación
-  **Logging y Monitoreo**: Implementar sistema de logs estructurado
-  **Tests Automatizados**: Aumentar cobertura de tests
-  **Documentación de API**: Completar documentación OpenAPI/Swagger

#### **Escalabilidad y Refinamiento**:
-  **Escalabilidad Horizontal**: Actualmente no soporta múltiples instancias
-  **Carga de Documentos Grandes**: Puede fallar con colecciones muy grandes
-  **Recomendaciones**:
  - Implementar load balancing
  - Procesamiento asíncrono mejorado
  - Base de datos distribuida (ChromaDB cluster)

### 4.5 Niveles de Confiabilidad del Sistema

#### **1. Precisión de Retrieval**:
- **Estrategia de Evaluación**: RAGAS (métricas: faithfulness, answer_relevancy, context_precision, context_recall)
- **Nivel Actual**: Medio-Alto (depende de la calidad de los documentos)
- **Mejoras**: Implementar evaluación continua con dataset de prueba

#### **2. Disponibilidad del Sistema**:
- **Estrategia de Evaluación**: Health checks y monitoreo de uptime
- **Nivel Actual**: Medio (depende de la VM de GCP)
- **Mejoras**: Implementar auto-restart, health checks más robustos

#### **3. Calidad de Respuestas Generadas**:
- **Estrategia de Evaluación**: Evaluación manual y feedback de usuarios
- **Nivel Actual**: Medio (respuestas dependen del contexto recuperado)
- **Mejoras**: Implementar sistema de feedback y fine-tuning de prompts

---

##  5. Instrucciones de Ejecución

### 5.1 Requisitos Previos

- Docker Desktop instalado y corriendo
- Google API Key (para Gemini)
- Acceso a GCP (para despliegue en producción)

### 5.2 Ejecución Local

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd llms-final
```

2. **Configurar variables de entorno**:
   - Crear `202515-MISW4411-Backend-Grupo21/.env` con `GOOGLE_API_KEY`
   - Crear `202515-MISW4411-Agent-Backend-Grupo21/app/.env` con `GOOGLE_API_KEY` y `RAG_BASE_URL`

3. **Levantar servicios con Docker Compose**:
```bash
docker-compose up --build
```

4. **Acceder a la aplicación**:
   - Frontend: http://localhost:3000
   - RAG Backend: http://localhost:8000
   - Agent Backend: http://localhost:8001





