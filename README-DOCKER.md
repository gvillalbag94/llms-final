# Docker Compose - Ejecución de los 3 Proyectos

Este archivo contiene las instrucciones para ejecutar los 3 proyectos (Backend RAG, Agent Backend y Frontend) usando Docker Compose desde la raíz del proyecto.

## Estructura de Servicios

- **rag-backend**: Backend principal (RAG) - Puerto 8000
- **agent-backend**: Backend de agentes - Puerto 8001
- **frontend**: Frontend React - Puerto 3000

## Requisitos Previos

1. Docker y Docker Compose instalados
2. Archivos `.env` configurados en cada proyecto:
   - `202515-MISW4411-Backend-Grupo21/.env`
   - `202515-MISW4411-Agent-Backend-Grupo21/app/.env`

## Configuración de Variables de Entorno

### Backend RAG (`202515-MISW4411-Backend-Grupo21/.env`)
Asegúrate de tener configuradas las variables necesarias, especialmente:
- `GOOGLE_API_KEY`: Tu API key de Google

### Agent Backend (`202515-MISW4411-Agent-Backend-Grupo21/app/.env`)
El `RAG_BASE_URL` se configura automáticamente en el docker-compose para usar el servicio `rag-backend`. Si necesitas cambiarlo, edita el docker-compose.yml.

## Ejecución

### Levantar todos los servicios

```bash
docker-compose up --build
```

### Levantar en segundo plano

```bash
docker-compose up -d --build
```

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Servicio específico
docker-compose logs -f rag-backend
docker-compose logs -f agent-backend
docker-compose logs -f frontend
```

### Detener los servicios

```bash
docker-compose down
```

### Detener y eliminar volúmenes

```bash
docker-compose down -v
```

## Acceso a los Servicios

Una vez levantados los servicios, puedes acceder a:

- **Frontend**: http://localhost:3000
- **Agent Backend API**: http://localhost:8001
- **RAG Backend API**: http://localhost:8000

## Verificación

### Verificar que los servicios están corriendo

```bash
docker-compose ps
```

### Verificar salud del RAG Backend

```bash
curl http://localhost:8000/api/v1/health
```

### Verificar Agent Backend

```bash
curl http://localhost:8001/docs
```

## Solución de Problemas

### Los servicios no se conectan entre sí

Asegúrate de que todos los servicios estén en la misma red Docker (`misw-network`). Esto se configura automáticamente en el docker-compose.yml.

### El Agent Backend no puede conectarse al RAG Backend

Verifica que:
1. El servicio `rag-backend` esté corriendo y saludable
2. La variable `RAG_BASE_URL` en el docker-compose esté configurada como `http://rag-backend:8000`
3. Ambos servicios estén en la misma red Docker

### El Frontend no puede conectarse al Agent Backend

El frontend se conecta desde el navegador del usuario, por lo que debe usar `http://localhost:8001`. Esto está configurado en el docker-compose mediante la variable `VITE_BACKEND_URL`.

### Reconstruir un servicio específico

```bash
docker-compose up --build rag-backend
docker-compose up --build agent-backend
docker-compose up --build frontend
```

## Notas

- El Agent Backend espera a que el RAG Backend esté saludable antes de iniciar (usando `depends_on` con `condition: service_healthy`)
- El Frontend se construye con la URL del backend configurada en tiempo de build
- Todos los servicios se reinician automáticamente si fallan (`restart: unless-stopped`)

