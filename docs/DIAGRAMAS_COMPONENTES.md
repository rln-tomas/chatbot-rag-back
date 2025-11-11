# Diagramas de Componentes - ChatBotRAG Backend

## Diagrama de Arquitectura General

```mermaid
flowchart TB
    subgraph Client["<<Cliente>>"]
        WebApp[Aplicación Web/Mobile]
    end

    subgraph APILayer["<<API Layer>>"]
        FastAPI[FastAPI Application]
        AuthRouter[Auth Router]
        ChatRouter[Chat Router]
        ConfigRouter[Config Router]
        ScrapingRouter[Scraping Router]
    end

    subgraph ServiceLayer["<<Service Layer>>"]
        AuthService[Auth Service]
        ChatService[Chat Service]
        ConfigService[Config Service]
    end

    subgraph RepoLayer["<<Repository Layer>>"]
        UserRepo[User Repository]
        ConvRepo[Conversation Repository]
        MsgRepo[Message Repository]
        ConfigRepo[Configuration Repository]
    end

    subgraph RAGLayer["<<RAG Components>>"]
        RAGChain[RAG Chain]
        LLMFactory[LLM Factory]
        EmbFactory[Embeddings Factory]
        VectorStore[Pinecone Vectorstore]
    end

    subgraph CoreLayer["<<Core Infrastructure>>"]
        Database[Database Engine]
        Security[Security Utils]
        Settings[Settings Config]
    end

    subgraph WorkerLayer["<<Background Workers>>"]
        CeleryApp[Celery Application]
        ScrapingTask[Scraping Task]
        WebScraper[Web Scraper]
    end

    subgraph DataLayer["<<Data Storage>>"]
        MySQL[(MySQL Database)]
        Redis[(Redis Cache)]
    end

    subgraph ExternalServices["<<External Services>>"]
        Pinecone[(Pinecone Vector DB)]
        Gemini[Google Gemini API]
        Ollama[Ollama API]
        Jina[Jina AI API]
    end

    WebApp -->|HTTPS/JSON| FastAPI

    FastAPI --> AuthRouter
    FastAPI --> ChatRouter
    FastAPI --> ConfigRouter
    FastAPI --> ScrapingRouter

    AuthRouter --> AuthService
    ChatRouter --> ChatService
    ConfigRouter --> ConfigService
    ScrapingRouter --> CeleryApp

    AuthService --> UserRepo
    AuthService --> Security
    ChatService --> ConvRepo
    ChatService --> MsgRepo
    ChatService --> RAGChain
    ConfigService --> ConfigRepo

    UserRepo --> Database
    ConvRepo --> Database
    MsgRepo --> Database
    ConfigRepo --> Database

    RAGChain --> LLMFactory
    RAGChain --> EmbFactory
    RAGChain --> VectorStore

    Database --> MySQL
    CeleryApp --> Redis
    ScrapingTask --> Redis

    CeleryApp --> ScrapingTask
    ScrapingTask --> WebScraper
    ScrapingTask --> EmbFactory
    ScrapingTask --> VectorStore
    ScrapingTask --> Database

    VectorStore --> Pinecone
    LLMFactory --> Gemini
    LLMFactory --> Ollama
    EmbFactory --> Gemini
    EmbFactory --> Ollama
    EmbFactory --> Jina

    Settings -.configura.-> Database
    Settings -.configura.-> Security
    Settings -.configura.-> LLMFactory
    Settings -.configura.-> EmbFactory
```

---

## Diagrama de Módulos

```mermaid
flowchart LR
    subgraph AuthModule["Módulo de Autenticación"]
        direction TB
        AR[Auth Router]
        AS[Auth Service]
        UR[User Repository]
        UM[User Model]

        AR --> AS
        AS --> UR
        UR -.usa.-> UM
    end

    subgraph ChatModule["Módulo de Chat"]
        direction TB
        CR[Chat Router]
        CS[Chat Service]
        CVR[Conversation Repository]
        MR[Message Repository]
        CVM[Conversation Model]
        MM[Message Model]

        CR --> CS
        CS --> CVR
        CS --> MR
        CVR -.usa.-> CVM
        MR -.usa.-> MM
    end

    subgraph ConfigModule["Módulo de Configuración"]
        direction TB
        CFR[Config Router]
        CFS[Config Service]
        CFRepo[Config Repository]
        CFM[Configuration Model]

        CFR --> CFS
        CFS --> CFRepo
        CFRepo -.usa.-> CFM
    end

    subgraph ScrapingModule["Módulo de Scraping"]
        direction TB
        SR[Scraping Router]
        CA[Celery App]
        ST[Scraping Task]
        WS[Web Scraper]

        SR --> CA
        CA --> ST
        ST --> WS
    end

    subgraph RAGModule["Módulo RAG"]
        direction TB
        RC[RAG Chain]
        LF[LLM Factory]
        EF[Embeddings Factory]
        VS[Vectorstore Client]

        RC --> LF
        RC --> EF
        RC --> VS
    end

    subgraph CoreModule["Módulo Core"]
        direction TB
        DB[Database Engine]
        SEC[Security Utils]
        CFG[Settings]
        DEP[Dependencies]
    end

    ChatModule --> RAGModule
    AuthModule --> CoreModule
    ChatModule --> CoreModule
    ConfigModule --> CoreModule
    ScrapingModule --> RAGModule
    ScrapingModule --> CoreModule
```

---

## Diagrama de Capas

```mermaid
flowchart TD
    subgraph Presentation["Capa de Presentación"]
        R1[Auth Router<br/>POST /register<br/>POST /login<br/>GET /me]
        R2[Chat Router<br/>POST /chat<br/>GET /conversations]
        R3[Config Router<br/>POST /configs<br/>GET /configs]
        R4[Scraping Router<br/>POST /scraping/start]
    end

    subgraph Business["Capa de Negocio"]
        S1[Auth Service<br/>register<br/>login<br/>authenticate]
        S2[Chat Service<br/>process_chat<br/>get_conversations<br/>save_message]
        S3[Config Service<br/>create_config<br/>list_configs<br/>update_status]
    end

    subgraph DataAccess["Capa de Acceso a Datos"]
        Repo1[User Repository<br/>CRUD operations]
        Repo2[Conversation Repository<br/>CRUD operations]
        Repo3[Message Repository<br/>CRUD operations]
        Repo4[Config Repository<br/>CRUD operations]
    end

    subgraph Domain["Capa de Dominio"]
        M1[User<br/>id, email, password<br/>created_at]
        M2[Conversation<br/>id, user_id, title<br/>messages]
        M3[Message<br/>id, content<br/>is_user_message]
        M4[Configuration<br/>id, url, status<br/>error_message]
    end

    subgraph Integration["Capa de Integración"]
        I1[RAG Chain<br/>Orchestration]
        I2[LLM Provider<br/>Gemini/Ollama]
        I3[Embeddings<br/>Gemini/Ollama/Jina]
        I4[Vectorstore<br/>Pinecone Client]
    end

    subgraph Infrastructure["Capa de Infraestructura"]
        Inf1[Database<br/>SQLAlchemy]
        Inf2[Security<br/>JWT/bcrypt]
        Inf3[Settings<br/>Environment Config]
    end

    R1 --> S1
    R2 --> S2
    R3 --> S3

    S1 --> Repo1
    S2 --> Repo2
    S2 --> Repo3
    S2 --> I1
    S3 --> Repo4

    Repo1 --> M1
    Repo2 --> M2
    Repo3 --> M3
    Repo4 --> M4

    Repo1 --> Inf1
    Repo2 --> Inf1
    Repo3 --> Inf1
    Repo4 --> Inf1

    I1 --> I2
    I1 --> I3
    I1 --> I4

    S1 --> Inf2
```

---

## Diagrama Detallado de Componentes

```mermaid
flowchart TB
    User([Usuario])

    subgraph API["FastAPI Backend"]
        Main[main.py<br/>FastAPI App]

        subgraph Routers["Routers"]
            AuthR{{Auth Router}}
            ChatR{{Chat Router}}
            ConfigR{{Config Router}}
            ScrapeR{{Scraping Router}}
        end

        subgraph Services["Services"]
            AuthS[Auth Service]
            ChatS[Chat Service]
            ConfigS[Config Service]
        end

        subgraph Repos["Repositories"]
            UserRep[(User Repo)]
            ConvRep[(Conv Repo)]
            MsgRep[(Msg Repo)]
            CfgRep[(Config Repo)]
        end

        subgraph RAG["RAG Pipeline"]
            Chain{RAG Chain}
            LLM[LLM<br/>Gemini/Ollama]
            Emb[Embeddings<br/>Jina/Gemini/Ollama]
            Vec[Vectorstore<br/>Pinecone]
        end

        subgraph Core["Core"]
            DB[Database]
            Sec[Security]
        end
    end

    subgraph Worker["Celery Worker"]
        Celery[Celery App]
        Task[Scraping Task]
        Scraper[Web Scraper]
    end

    subgraph External["Servicios Externos"]
        MySQL[(MySQL)]
        Redis[(Redis)]
        Pinecone[(Pinecone)]
        APIs[APIs Externas<br/>Gemini/Ollama/Jina]
    end

    User -->|HTTP Request| Main
    Main --> AuthR & ChatR & ConfigR & ScrapeR

    AuthR --> AuthS
    ChatR --> ChatS
    ConfigR --> ConfigS
    ScrapeR --> Celery

    AuthS --> UserRep
    AuthS --> Sec
    ChatS --> ConvRep & MsgRep
    ChatS --> Chain
    ConfigS --> CfgRep

    UserRep & ConvRep & MsgRep & CfgRep --> DB

    Chain --> LLM & Emb & Vec

    Celery --> Task --> Scraper
    Task --> Emb & Vec & DB

    DB --> MySQL
    Celery -.-> Redis
    Vec --> Pinecone
    LLM & Emb --> APIs
```

---

## Diagrama de Alto Nivel

```mermaid
flowchart LR
    subgraph Frontend
        Client[Cliente Web/Mobile]
    end

    subgraph Backend["FastAPI Application"]
        API[API Gateway<br/>FastAPI]
        Auth[Authentication<br/>Module]
        Chat[Chat<br/>Module]
        Config[Configuration<br/>Module]
        Scraping[Scraping<br/>Module]
        RAG[RAG<br/>Module]
        Core[Core<br/>Module]
    end

    subgraph Workers["Background Processing"]
        Celery[Celery<br/>Workers]
    end

    subgraph Storage["Almacenamiento"]
        MySQL[(MySQL<br/>DB)]
        Redis[(Redis<br/>Queue)]
        Pinecone[(Pinecone<br/>Vectors)]
    end

    subgraph AI["Servicios IA"]
        LLMs[LLM Services<br/>Gemini/Ollama]
        Embeddings[Embedding Services<br/>Jina/Gemini/Ollama]
    end

    Client <-->|REST API| API

    API --> Auth
    API --> Chat
    API --> Config
    API --> Scraping

    Auth --> Core
    Chat --> Core
    Chat --> RAG
    Config --> Core
    Scraping --> Celery

    RAG --> LLMs
    RAG --> Embeddings
    RAG --> Pinecone

    Core --> MySQL
    Celery --> Redis
    Celery --> RAG
    Celery --> MySQL
```

---

## Descripción de Componentes

### API Layer
- **FastAPI Application**: Punto de entrada principal, maneja CORS y middleware
- **Auth Router**: Endpoints de autenticación (/register, /login, /refresh)
- **Chat Router**: Endpoints de chat (/chat, /conversations)
- **Config Router**: Endpoints de configuración (/configs)
- **Scraping Router**: Endpoints de scraping (/scraping/start)

### Service Layer
- **Auth Service**: Lógica de negocio para autenticación y manejo de usuarios
- **Chat Service**: Lógica de negocio para chat y gestión de conversaciones
- **Config Service**: Lógica de negocio para configuraciones de scraping

### Repository Layer
- **User Repository**: Acceso a datos de usuarios
- **Conversation Repository**: Acceso a datos de conversaciones
- **Message Repository**: Acceso a datos de mensajes
- **Config Repository**: Acceso a datos de configuraciones

### RAG Components
- **RAG Chain**: Orquestación del pipeline de RAG (Retrieve + Generate)
- **LLM Factory**: Factory para proveedores de LLM (Gemini/Ollama)
- **Embeddings Factory**: Factory para proveedores de embeddings (Jina/Gemini/Ollama)
- **Vectorstore**: Cliente de Pinecone para búsqueda vectorial

### Core Infrastructure
- **Database Engine**: Motor SQLAlchemy con pooling de conexiones
- **Security Utils**: Utilidades de JWT y hashing de contraseñas (bcrypt)
- **Settings**: Configuración de la aplicación via variables de entorno

### Background Workers
- **Celery App**: Aplicación Celery para tareas asíncronas
- **Scraping Task**: Tarea de scraping, embedding y almacenamiento
- **Web Scraper**: Scraper recursivo BFS con chunking de texto

### External Services
- **MySQL**: Base de datos relacional para datos estructurados
- **Redis**: Message broker y backend de resultados para Celery
- **Pinecone**: Base de datos vectorial para búsqueda semántica
- **Gemini/Ollama/Jina**: Proveedores de LLM y embeddings
