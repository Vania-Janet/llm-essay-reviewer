# System Architecture

## Overview

The Essay Evaluator system follows a modular, layered architecture designed for scalability, maintainability, and testability.

## Architecture Layers

### 1. Presentation Layer (Web Interface)
- **Location**: `essay_evaluator/web/`
- **Technology**: HTML, CSS, Vanilla JavaScript
- **Responsibilities**:
  - User interface rendering
  - File upload handling
  - Real-time feedback display
  - Interactive charts and visualizations

### 2. API Layer
- **Location**: `essay_evaluator/api/`
- **Technology**: Flask REST API
- **Components**:
  - **Routes**: Endpoint definitions (`/api/auth/`, `/api/essays/`)
  - **Middleware**: Authentication, error handling, logging
  - **Validators**: Input validation and sanitization
- **Responsibilities**:
  - HTTP request/response handling
  - JWT authentication
  - Rate limiting
  - Request validation

### 3. Business Logic Layer
- **Location**: `essay_evaluator/core/`
- **Components**:
  - **Agent**: LangGraph-based evaluation orchestrator
  - **Evaluation**: Criterion-specific evaluators
  - **Models**: Pydantic data models
- **Responsibilities**:
  - Essay evaluation orchestration
  - LLM prompt management
  - Score calculation
  - Validation rules

### 4. Data Access Layer
- **Location**: `essay_evaluator/utils/database/`
- **Technology**: SQLAlchemy ORM
- **Responsibilities**:
  - Database CRUD operations
  - Query optimization
  - Transaction management
  - Connection pooling

### 5. Utility Layer
- **Location**: `essay_evaluator/utils/`
- **Components**:
  - **PDF Processing**: Text extraction and cleaning
  - **Validators**: Input validation helpers
- **Responsibilities**:
  - PDF text extraction
  - Text preprocessing
  - File handling
  - Utility functions

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface (Browser)                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Login    │  │  Upload    │  │   Results  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask API Layer                         │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐   │
│  │ Auth Routes   │  │ Essay Routes  │  │  Middleware  │   │
│  └───────────────┘  └───────────────┘  └──────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                ┌───────────┴──────────┐
                ▼                      ▼
┌────────────────────────┐  ┌──────────────────────────┐
│  Core Business Logic   │  │   Database Layer         │
│  ┌─────────────────┐  │  │  ┌──────────────────┐   │
│  │  LangGraph      │  │  │  │  SQLAlchemy ORM  │   │
│  │  Agent          │  │  │  │                  │   │
│  └────────┬────────┘  │  │  └────────┬─────────┘   │
│           │            │  │           │              │
│  ┌────────▼────────┐  │  │  ┌────────▼─────────┐  │
│  │  6 Evaluation   │  │  │  │  SQLite/Postgres │  │
│  │  Criteria Nodes │  │  │  └──────────────────┘  │
│  └─────────────────┘  │  │                         │
└────────────────────────┘  └──────────────────────────┘
            │
            ▼
┌────────────────────────┐
│   External Services    │
│  ┌─────────────────┐  │
│  │  OpenAI GPT-4   │  │
│  └─────────────────┘  │
└────────────────────────┘
```

## Data Flow

### Essay Evaluation Flow

```
1. User uploads PDF
   ↓
2. PDF → Text extraction (PyPDF/pdfplumber)
   ↓
3. Text validation and preprocessing
   ↓
4. Create evaluation request
   ↓
5. LangGraph Agent initialization
   ↓
6. Parallel execution of 6 criteria evaluations (GPT-4)
   │
   ├─ Technical Quality
   ├─ Creativity
   ├─ Thematic Alignment
   ├─ Social Responsibility
   ├─ AI Usage
   └─ Impact Potential
   ↓
7. Results aggregation
   ↓
8. Final synthesis and general commentary
   ↓
9. Score calculation (weighted average)
   ↓
10. Save to database
   ↓
11. Return results to client
   ↓
12. Display in UI with visualizations
```

## Concurrency Model

### Parallel Evaluation Processing

The system uses LangGraph's built-in parallelization to evaluate all 6 criteria simultaneously:

```python
# 6 criteria evaluated in parallel
workflow.add_edge("inicio", "calidad_tecnica")
workflow.add_edge("inicio", "creatividad")
workflow.add_edge("inicio", "vinculacion")
workflow.add_edge("inicio", "bienestar")
workflow.add_edge("inicio", "uso_ia")
workflow.add_edge("inicio", "impacto")

# All converge to final synthesis
workflow.add_edge("calidad_tecnica", "comentario_general")
workflow.add_edge("creatividad", "comentario_general")
# ...
```

**Performance Impact**: Reduces evaluation time from ~35s (sequential) to ~10-15s (parallel)

## Security Architecture

### Authentication Flow

```
1. User enters credentials
   ↓
2. Server validates against database (bcrypt)
   ↓
3. Generate JWT token (1 hour expiry)
   ↓
4. Client stores token (localStorage)
   ↓
5. All API requests include token in header
   ↓
6. Middleware validates token on each request
   ↓
7. Token refresh on expiry
```

### Security Layers

1. **Transport Security**: HTTPS in production
2. **Authentication**: JWT tokens with expiration
3. **Password Security**: bcrypt hashing with salt
4. **Input Validation**: Pydantic models + Flask validators
5. **SQL Injection Prevention**: SQLAlchemy ORM (parameterized queries)
6. **XSS Prevention**: Content Security Policy headers
7. **CSRF Protection**: SameSite cookies

## Scalability Considerations

### Current Limitations
- SQLite: Single-writer limitation
- Local file storage
- In-memory processing

### Scaling Path
1. **Database**: Migrate to PostgreSQL for concurrent writes
2. **Storage**: Move to S3/Azure Blob for file storage
3. **Caching**: Add Redis for evaluation caching
4. **Queue**: Celery for async task processing
5. **Load Balancer**: Nginx for multiple instances
6. **Containerization**: Docker + Kubernetes

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML/CSS/JS | User interface |
| Backend | Flask | REST API |
| Agent Framework | LangGraph | Evaluation orchestration |
| LLM | OpenAI GPT-4 | Essay analysis |
| ORM | SQLAlchemy | Database abstraction |
| Database | SQLite | Data persistence |
| PDF Processing | PyPDF + pdfplumber | Text extraction |
| Authentication | JWT + bcrypt | Security |
| Validation | Pydantic | Data validation |

## Design Patterns

1. **Repository Pattern**: Database operations abstracted in `database/operations.py`
2. **Factory Pattern**: Agent creation and configuration
3. **Strategy Pattern**: Different evaluation criteria as separate strategies
4. **Singleton Pattern**: Database connection pool
5. **Decorator Pattern**: Authentication middleware (`@require_auth`)
6. **Observer Pattern**: Real-time progress updates (WebSocket ready)

## Extension Points

The architecture supports easy extension:

1. **New Criteria**: Add new evaluation node to LangGraph
2. **New File Types**: Add processor in `utils/pdf/`
3. **New APIs**: Add route in `api/routes/`
4. **New LLM Providers**: Abstract LLM interface
5. **New Storage**: Abstract storage interface
