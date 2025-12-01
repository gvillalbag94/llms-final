# 🌐  Documentación del API

El API REST está compuesto por **4 endpoints principales**:

## Health Check

**Endpoint**: `GET /api/v1/health`

**Descripción**: Verificación del estado del sistema.

**Request**: Sin parámetros

**Response**:

```json
{
  "status": "healthy",
  "success": true,
  "timestamp": "2025-10-30T10:15:30.123456",
  "service": "API"
}
```

---

## Load Documents

**Endpoint**: `POST /api/v1/documents/load-from-url`

**Descripción**: Carga documentos desde una URL de Google Drive y los procesa asíncronamente.

**Request Body**:

```json
{
  "source_url": "https://drive.google.com/drive/folders/...",
  "collection_name": "test_coleccion",
  "chunking_config": {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "chunking_strategy": "recursive_character"
  },
  "processing_options": {
    "file_extensions": ["pdf", "txt", "docx"],
    "max_file_size_mb": 50,
    "timeout_per_file_seconds": 300
  },
  "embedding_config": {
    "model": "embedding-001",
    "batch_size": 100
  }
}
```

**Atributos principales**:

- `source_url` (requerido): URL de Google Drive donde están los documentos
- `collection_name` (requerido): Nombre de la ruta de la colección donde quedan almacenados los documentos
- `chunking_config` (requerido): Configuración para fragmentación de documentos: Tamaño, overlap (Opcional, depende de la estrategia), estrategia
- `processing_options` (opcional): Opciones de procesamiento de archivos: file_extensions (Base, depende de los documentos que se quieran procesar)
- `embedding_config` (opcional): Configuración del modelo de embeddings

**Response**:

```json
{
  "success": true,
  "message": "Procesamiento iniciado en background",
  "processing_id": "proc_b8ae8dbda5f9",
  "timestamp": "2025-10-30T10:15:30.123456"
}
```

---

## Validate Load

**Endpoint**: `GET /api/v1/documents/load-from-url/{processing_id}`

**Descripción**: Consulta el estado y resultados de un procesamiento de documentos.

**Parameters**:

- `processing_id` (path): ID del procesamiento a consultar

**Response**:

```json
{
  "success": true,
  "message": "Documentos cargados y procesados exitosamente",
  "data": {
    "collection_info": {
      "name": "test_coleccion",
      "documents_found": 5,
      "documents_processed_successfully": 5,
      "documents_failed": 0,
      "total_chunks_before": 0,
      "total_chunks_after": 25,
      "storage_size_mb": 150
    },
    "documents_processed": [...],
    "failed_documents": [],
    "chunking_statistics": {...},
    "embedding_statistics": {...},
    "processing_id": "proc_b8ae8dbda5f9",
    "timestamp": "2025-10-30T10:20:45.789123"
  }
}
```
**Atributos de respuesta**:

- `success`: Indica si el procesamiento fue exitoso
- `message`: Mensaje descriptivo del resultado
- `data`: Objeto con toda la información del procesamiento
  - `collection_info`: Información de la colección procesada
    - `name`: Nombre de la colección
    - `documents_found`: Total de documentos encontrados
    - `documents_processed_successfully`: Documentos procesados exitosamente
    - `documents_failed`: Número de documentos que fallaron
    - `total_chunks_before`: Chunks existentes antes del procesamiento
    - `total_chunks_after`: Chunks totales después del procesamiento
    - `storage_size_mb`: Tamaño de almacenamiento en MB
  - `documents_processed`: Lista de documentos procesados exitosamente con metadatos
  - `failed_documents`: Lista de documentos que fallaron con información de error
  - `chunking_statistics`: Estadísticas del proceso de fragmentación
  - `embedding_statistics`: Estadísticas del proceso de embeddings
  - `processing_id`: ID único del procesamiento
  - `timestamp`: Marca de tiempo del procesamiento

---

## Ask Questions

**Endpoint**: `POST /api/v1/ask`

**Descripción**: Realiza consultas inteligentes al sistema RAG sobre documentos cargados.

**Request Body**:

```json
{
  "question": "¿Cuáles son los puntos principales del contrato?",
  "top_k": 5,
  "collection": "test_coleccion",
  "force_rebuild": false,
  "use_reranking": false,
  "use_query_rewriting": false
}
```

**Atributos**:

- `question` (requerido): La pregunta a responder
- `top_k` (opcional, default: 5): Número de documentos relevantes a recuperar
- `collection` (opcional): Nombre de la colección a consultar
- `force_rebuild` (opcional, default: false): Forzar reconstrucción del índice
- `use_reranking` (opcional, default: false): **⚠️ Solo Semana 3** - Aplicar reordenamiento por relevancia
- `use_query_rewriting` (opcional, default: false): **⚠️ Solo Semana 3** - Aplicar reescritura de consulta

**⚠️ Importante sobre atributos avanzados**:

- `use_reranking` y `use_query_rewriting` están diseñados para **Semana 3**
- **No incluya** estos atributos en Semana 1 y 2
- Cuando `use_reranking=true`, los `context_docs` incluirán `rerank_score`

**Response**:

```json
{
  "question": "¿Cuáles son los puntos principales del contrato?",
  "final_query": "principales cláusulas términos condiciones contrato",
  "answer": "Los puntos principales del contrato incluyen...",
  "collection": "test_coleccion",
  "files_consulted": ["contrato_1.pdf", "contrato_2.pdf"],
  "context_docs": [
    {
      "file_name": "contrato_1.pdf",
      "page_number": 3,
      "chunk_type": "text",
      "priority": "high",
      "snippet": "Las condiciones principales del contrato...",
      "rerank_score": 0.85
    }
  ],
  "reranker_used": true,
  "query_rewriting_used": true,
  "response_time_sec": 2.45
}
```

**Atributos de respuesta**:

- `question`: Pregunta original
- `final_query`: Consulta final (es reescrita en Semana 3)
- `answer`: Respuesta generada por el sistema RAG
- `collection`: Colección utilizada
- `files_consulted`: Lista de archivos consultados
- `context_docs`: Fragmentos específicos utilizados como contexto
- `reranker_used`: Indica si se aplicó reranking (Semana 3)
- `query_rewriting_used`: Indica si se aplicó query rewriting (Semana 3)
- `response_time_sec`: Tiempo de procesamiento en segundos
