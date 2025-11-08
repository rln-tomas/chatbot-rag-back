# ChatBot RAG API

API backend para un chatbot RAG (Retrieval-Augmented Generation) construido con FastAPI, LangChain, Gemini y Pinecone.

## Características

- **Autenticación JWT**: Sistema completo de registro, login y gestión de tokens
- **Chat con RAG**: Respuestas basadas en documentos almacenados en vector store
- **Streaming**: Soporte para respuestas en tiempo real con Server-Sent Events
- **Web Scraping**: Sistema de scraping asíncrono con Celery
- **Vector Store**: Integración con Pinecone para búsqueda semántica
- **LLM**: Soporte para múltiples proveedores (Google Gemini y Ollama)

## Stack Tecnológico

- **Framework**: FastAPI 0.121.0
- **ORM**: SQLAlchemy 2.0.23 + Alembic
- **Base de datos**: MySQL 8.0
- **Cache/Queue**: Redis 7
- **Task Queue**: Celery 5.4.0
- **LLM**: Google Gemini o Ollama (via LangChain)
- **Vector Store**: Pinecone
- **Web Scraping**: LangChain WebBaseLoader

## Estructura del Proyecto

```
ChatBotRAGBack/
├── app/
│   ├── core/                    # Configuración global
│   │   ├── config.py           # Variables de entorno
│   │   ├── database.py         # Configuración SQLAlchemy
│   │   ├── security.py         # JWT y hashing
│   │   └── dependencies.py     # Dependencias FastAPI
│   ├── auth/                    # Módulo de autenticación
│   ├── chat/                    # Módulo de chat
│   ├── config_management/       # Gestión de URLs
│   ├── scraping/                # Scraping asíncrono
│   ├── langchain_app/           # LangChain components
│   ├── api/v1/                  # Agregador de routers
│   └── main.py                  # Aplicación principal
├── worker/                      # Celery worker
├── alembic/                     # Migraciones de DB
├── tests/                       # Tests
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Instalación

### Opción 1: Docker (Recomendado)

1. **Clonar el repositorio**

```bash
git clone <repository-url>
cd ChatBotRAGBack
```

2. **Configurar variables de entorno**

```bash
cp .env.example .env
```

Edita `.env` y configura:

- `JWT_SECRET_KEY`: Clave secreta para JWT
- `LLM_PROVIDER`: Proveedor de LLM ('gemini' o 'ollama')
- `GEMINI_API_KEY`: API key de Google Gemini (si usas Gemini)
- `OLLAMA_BASE_URL`: URL de Ollama (si usas Ollama, default: http://localhost:11434)
- `OLLAMA_MODEL`: Modelo de Ollama (si usas Ollama, default: llama3.2)
- `PINECONE_API_KEY`: API key de Pinecone
- `PINECONE_ENVIRONMENT`: Entorno de Pinecone
- `PINECONE_INDEX_NAME`: Nombre del índice

3. **Levantar servicios con Docker Compose**

```bash
docker-compose up -d
```

Esto iniciará:

- MySQL en puerto 3306
- Redis en puerto 6379
- **Ollama en puerto 11434** (servidor LLM local)
- API en puerto 8000
- Celery Worker
- Flower (monitoring) en puerto 5555

4. **Instalar modelo en Ollama** (si usas Ollama)

```bash
# Opción 1: Usar el script interactivo
./scripts/setup_ollama.sh

# Opción 2: Manual
docker exec chatbot_ollama ollama pull gpt-oss:20b
# o cualquier otro modelo que desees
```

**Nota:** Si vas a usar Gemini, puedes omitir este paso y configurar `LLM_PROVIDER=gemini` en tu `.env`.

5. **Crear migraciones iniciales**

```bash
docker-compose exec api alembic revision --autogenerate -m "Initial migration"
docker-compose exec api alembic upgrade head
```

6. **Verificar que la API está corriendo**

```bash
curl http://localhost:8000/health
```

### Opción 2: Instalación Local

1. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

4. **Iniciar MySQL y Redis localmente** (o usar Docker)

```bash
# MySQL
docker run -d -p 3306:3306 \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=chatbot_db \
  -e MYSQL_USER=chatbot_user \
  -e MYSQL_PASSWORD=chatbot_password \
  mysql:8.0

# Redis
docker run -d -p 6379:6379 redis:7-alpine
```

5. **Ejecutar migraciones**

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

6. **Iniciar la aplicación**

```bash
# Terminal 1: API
uvicorn app.main:app --reload --port 8000

# Terminal 2: Celery Worker
celery -A worker.celery_app worker --loglevel=info

# Terminal 3 (opcional): Flower
celery -A worker.celery_app flower --port=5555
```

## Uso de la API

### Documentación Interactiva

Una vez la API esté corriendo, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Principales

#### Autenticación

**Registro de usuario**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Usuario Test",
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Login**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

Respuesta:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### Configuración de URLs

**Crear configuración de URL**

```bash
curl -X POST "http://localhost:8000/api/v1/configs/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article"
  }'
```

**Listar configuraciones**

```bash
curl "http://localhost:8000/api/v1/configs/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Scraping

**Iniciar scraping**

```bash
curl -X POST "http://localhost:8000/api/v1/scraping/start" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config_id": 1
  }'
```

Respuesta:

```json
{
  "message": "Scraping job started successfully",
  "task_id": "abc-123-def",
  "config_id": 1,
  "status": "processing"
}
```

#### Chat

**Chat normal (no streaming)**

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué información tienes sobre el artículo?"
  }'
```

**Chat con streaming (SSE)**

```bash
curl -N "http://localhost:8000/api/v1/chat/stream" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Qué información tienes?"
  }'
```

**Ver conversaciones**

```bash
curl "http://localhost:8000/api/v1/chat/conversations" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Arquitectura

### Flujo de Autenticación

1. Usuario se registra o hace login
2. API genera JWT access token y refresh token
3. Cliente incluye access token en header `Authorization: Bearer TOKEN`
4. API valida token y extrae user_id

### Flujo de Scraping

1. Usuario crea una configuración con URL
2. Usuario dispara el scraping
3. API verifica que no hay jobs activos
4. Se crea una tarea Celery asíncrona
5. Worker:
   - Scrapea la URL con WebBaseLoader
   - Divide el contenido en chunks
   - Genera embeddings con Google
   - Guarda en Pinecone con metadata
6. Actualiza el estado de la configuración

### Flujo de Chat RAG

1. Usuario envía mensaje
2. API recupera historial de conversación
3. LangChain:
   - Busca documentos relevantes en Pinecone
   - Construye contexto con documentos recuperados
   - Genera respuesta con Gemini
4. Guarda mensaje de usuario y bot en BD
5. Retorna respuesta (normal o streaming)

## Monitoreo

### Flower (Celery Tasks)

Accede a http://localhost:5555 para ver:

- Tasks en ejecución
- Tasks completadas/fallidas
- Workers activos
- Estadísticas

### Logs

```bash
# API logs
docker-compose logs -f api

# Worker logs
docker-compose logs -f worker

# Todos los servicios
docker-compose logs -f
```

## Testing

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio pytest-cov

# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/
```

## Migraciones de Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

## Troubleshooting

### Error: "Configuration not found"

- Verifica que la configuración pertenezca al usuario autenticado
- Verifica que el config_id sea correcto

### Error: "You already have an active scraping job"

- Solo se permite un job de scraping activo por usuario
- Espera a que el job actual termine o falle
- Verifica el estado en Flower (http://localhost:5555)

### Error: "Invalid authentication credentials"

- Verifica que el token no haya expirado
- Genera un nuevo token con el endpoint de refresh
- Verifica que JWT_SECRET_KEY sea el mismo en todos los servicios

### Celery Worker no procesa tasks

- Verifica que Redis esté corriendo
- Verifica las variables CELERY_BROKER_URL y CELERY_RESULT_BACKEND
- Revisa logs del worker: `docker-compose logs worker`

## Variables de Entorno

| Variable            | Descripción                               | Ejemplo                                     |
| ------------------- | ----------------------------------------- | ------------------------------------------- |
| DATABASE_URL        | URL de conexión a MySQL                   | mysql+pymysql://user:pass@localhost:3306/db |
| JWT_SECRET_KEY      | Clave secreta para JWT                    | your-super-secret-key                       |
| JWT_ALGORITHM       | Algoritmo JWT                             | HS256                                       |
| LLM_PROVIDER        | Proveedor de LLM                          | gemini o ollama                             |
| GEMINI_API_KEY      | API key de Google Gemini (si usas Gemini) | AIza...                                     |
| OLLAMA_BASE_URL     | URL base de Ollama (si usas Ollama)       | http://localhost:11434                      |
| OLLAMA_MODEL        | Modelo de Ollama (si usas Ollama)         | llama3.2                                    |
| PINECONE_API_KEY    | API key de Pinecone                       | pcsk\_...                                   |
| PINECONE_INDEX_NAME | Nombre del índice                         | chatbot-rag-index                           |
| REDIS_URL           | URL de Redis                              | redis://localhost:6379/0                    |
| CELERY_BROKER_URL   | Broker de Celery                          | redis://localhost:6379/0                    |

## Configuración de LLM

Esta aplicación soporta dos proveedores de LLM:

### Opción 1: Google Gemini (Cloud)

Configura en tu `.env`:

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu-api-key-de-gemini
```

**Ventajas:**

- Sin necesidad de infraestructura local
- Modelos potentes y actualizados
- Baja latencia

**Desventajas:**

- Requiere API key de pago
- Costos por uso
- Requiere conexión a internet

### Opción 2: Ollama (Con Docker - Recomendado)

**Si ya tienes el proyecto con Docker Compose**, Ollama ya está incluido:

1. **El contenedor de Ollama se inicia automáticamente** con `docker-compose up -d`

2. **Instalar un modelo en el contenedor:**

```bash
# Opción 1: Script interactivo
./scripts/setup_ollama.sh

# Opción 2: Manual
docker exec chatbot_ollama ollama pull gpt-oss:20b
# Ver modelos instalados
docker exec chatbot_ollama ollama list
```

3. **Configurar en tu `.env`:**

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434  # Nombre del servicio en Docker
OLLAMA_MODEL=gpt-oss:20b
```

4. **Reiniciar el servicio API:**

```bash
docker-compose restart api
```

**Modelos recomendados por tamaño:**

- `llama3.2:1b` - Muy liviano (~1GB) - Ideal para pruebas
- `llama3.2:3b` - Liviano (~2GB) - Buen balance
- `llama3.2` - Estándar (~8GB) - Calidad superior
- `gpt-oss:20b` - Grande (~12GB) - Máxima calidad

### Opción 3: Ollama (Local sin Docker)

1. **Instalar Ollama:**

   - macOS/Linux: `curl -fsSL https://ollama.com/install.sh | sh`
   - Windows: Descarga desde https://ollama.com

2. **Descargar un modelo:**

```bash
ollama pull llama3.2
# o cualquier otro modelo: llama3.1, mistral, codellama, etc.
```

3. **Verificar que Ollama está corriendo:**

```bash
ollama list
```

4. **Configurar en tu `.env`:**

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434  # localhost si no usas Docker
OLLAMA_MODEL=llama3.2
```

**Ventajas de Ollama:**

- Totalmente gratis
- Sin límites de uso
- Privacidad total (datos no salen de tu máquina)
- Sin necesidad de conexión a internet (después de descargar el modelo)

**Desventajas:**

- Requiere recursos locales (GPU recomendada)
- Mayor latencia que servicios cloud
- Menor calidad que modelos top tier

### Cambiar de proveedor

Simplemente actualiza la variable `LLM_PROVIDER` en tu `.env` y reinicia la aplicación:

```bash
# Para usar Gemini
LLM_PROVIDER=gemini

# Para usar Ollama
LLM_PROVIDER=ollama
```

## Licencia

MIT

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.
