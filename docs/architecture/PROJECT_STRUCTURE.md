# 📁 Project Structure Guide

## Overview

This document explains the professional, modular structure of the Essay Evaluator project. The structure follows industry best practices for Python applications and ensures code is maintainable, testable, and easily understandable.

---

## 🎯 Design Principles

The project structure follows these key principles:

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Modularity**: Components are loosely coupled and can be tested independently
3. **Scalability**: Easy to add new features without modifying existing code
4. **Replicability**: Clear structure makes it easy for others to understand and contribute
5. **Industry Standards**: Follows Python packaging conventions (PEP 8, PEP 517)

---

## 📂 Directory Structure

```
essay-agent/
│
├── essay_evaluator/              # 📦 Main application package
│   ├── __init__.py               # Package initialization and version info
│   │
│   ├── core/                     # 🧠 Core business logic (domain layer)
│   │   ├── __init__.py
│   │   ├── agent/                # LangGraph evaluation agent
│   │   │   ├── __init__.py
│   │   │   └── evaluator.py     # Main EvaluadorEnsayos class
│   │   ├── evaluation/           # Evaluation criteria and prompts
│   │   │   ├── __init__.py
│   │   │   └── prompts.py       # LLM prompt templates
│   │   └── models/               # Pydantic data models
│   │       ├── __init__.py
│   │       └── evaluation.py    # EvaluacionEnsayo, EvaluacionCriterio
│   │
│   ├── api/                      # 🌐 REST API layer
│   │   ├── __init__.py
│   │   ├── app.py               # Flask application entry point
│   │   ├── routes/              # API endpoint definitions
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication routes
│   │   │   └── essays.py        # Essay CRUD and evaluation routes
│   │   └── middleware/          # Request/response processing
│   │       ├── __init__.py
│   │       ├── auth.py          # JWT verification middleware
│   │       └── error_handlers.py # Global error handling
│   │
│   ├── web/                      # 🎨 Web interface (presentation layer)
│   │   ├── static/              # Static assets
│   │   │   ├── css/
│   │   │   │   └── styles.css   # Application styles
│   │   │   ├── js/
│   │   │   │   ├── script.js    # Main application logic
│   │   │   │   └── criteria-management.js # Criteria CRUD
│   │   │   └── images/
│   │   │       ├── icon.png     # Favicon
│   │   │       └── logo.png     # Application logo
│   │   └── templates/           # HTML templates
│   │       ├── index.html       # Main application page
│   │       └── login.html       # Login page
│   │
│   ├── utils/                    # 🔧 Utility modules
│   │   ├── __init__.py
│   │   ├── pdf/                 # PDF processing
│   │   │   ├── __init__.py
│   │   │   └── processor.py    # PDFProcessor class
│   │   ├── database/            # Database utilities
│   │   │   ├── __init__.py
│   │   │   └── connection.py   # SQLAlchemy models and connection
│   │   └── validators.py       # Input validation helpers
│   │
│   ├── data/                     # 💾 Data storage
│   │   ├── raw/                 # Raw uploaded PDFs
│   │   ├── processed/           # Processed text files
│   │   └── database/            # SQLite database files
│   │       └── essays.db
│   │
│   └── tests/                    # 🧪 Test suite
│       ├── __init__.py
│       ├── test_agent.py        # Agent unit tests
│       ├── test_api.py          # API integration tests
│       ├── test_pdf_processor.py # PDF processing tests
│       └── fixtures/            # Test data
│
├── scripts/                      # 🛠️ Utility scripts
│   ├── migrate_structure.py     # Migrate old structure to new
│   ├── load_processed_essays.py # Import existing essays
│   ├── setup_database.py        # Initialize database
│   └── batch_evaluate.py        # Batch process essays
│
├── docs/                         # 📚 Documentation
│   ├── architecture/            # Architecture documentation
│   │   ├── system_design.md     # System architecture overview
│   │   └── data_flow.md         # Data flow diagrams
│   ├── api/                     # API documentation
│   │   └── endpoints.md         # API endpoint reference
│   └── user_guide/              # User guides
│       ├── getting_started.md   # Quick start guide
│       └── admin_guide.md       # Admin/deployment guide
│
├── config/                       # ⚙️ Configuration files
│   ├── __init__.py
│   ├── development.py           # Development settings
│   ├── production.py            # Production settings
│   └── testing.py               # Test configuration
│
├── logs/                         # 📝 Application logs
│   └── app.log
│
├── .env.example                  # Environment variables template
├── .env                          # Environment variables (not in git)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package installation configuration
├── pytest.ini                    # Pytest configuration
├── README.md                     # Project README
├── PROJECT_STRUCTURE.md          # This file
└── LICENSE                       # License file
```

---

## 📦 Package Breakdown

### 1. `essay_evaluator/` - Main Application Package

This is the root package containing all application code. It's designed to be installable via pip.

**Why this structure?**
- Enables `pip install -e .` for development
- Makes imports clean: `from essay_evaluator.core.agent import EvaluadorEnsayos`
- Follows Python packaging standards

### 2. `essay_evaluator/core/` - Business Logic

**Purpose**: Contains the core domain logic independent of external frameworks.

**Modules:**

#### `agent/` - Evaluation Agent
- **File**: `evaluator.py`
- **Class**: `EvaluadorEnsayos`
- **Responsibility**: Orchestrates essay evaluation using LangGraph
- **Key Feature**: Parallel execution of 6 evaluation criteria

```python
from essay_evaluator.core.agent import EvaluadorEnsayos

evaluator = EvaluadorEnsayos()
result = evaluator.evaluar(essay_text, anexo_ia)
```

#### `evaluation/` - Evaluation Logic
- **File**: `prompts.py`
- **Content**: LLM prompt templates for each criterion
- **Responsibility**: Define evaluation instructions for GPT-4

#### `models/` - Data Models
- **File**: `evaluation.py`
- **Classes**: `EvaluacionEnsayo`, `EvaluacionCriterio`, `FragmentoDestacado`
- **Responsibility**: Pydantic models for type validation and serialization

**Design Decision**: Core is framework-agnostic. It doesn't depend on Flask, SQLAlchemy, or specific PDF libraries. This makes it testable and reusable.

### 3. `essay_evaluator/api/` - REST API Layer

**Purpose**: HTTP interface for the application.

**Structure:**

#### `app.py` - Flask Application
- Main Flask app initialization
- Route registration
- Middleware setup
- Error handlers

#### `routes/` - Endpoint Definitions
- **`auth.py`**: Login, logout, user management
- **`essays.py`**: Essay CRUD operations, evaluation, comparison

#### `middleware/` - Request Processing
- **`auth.py`**: JWT token verification
- **`error_handlers.py`**: Consistent error responses

**Example Usage:**
```python
# In routes/essays.py
from essay_evaluator.core.agent import EvaluadorEnsayos
from essay_evaluator.api.middleware.auth import require_auth

@app.route('/api/essays/evaluate', methods=['POST'])
@require_auth
def evaluate_essay():
    # API endpoint implementation
    pass
```

### 4. `essay_evaluator/web/` - Web Interface

**Purpose**: User-facing HTML/CSS/JavaScript interface.

**Structure:**

#### `static/` - Static Assets
- **`css/styles.css`**: Application styling (2600+ lines)
- **`js/script.js`**: Main application logic
- **`js/criteria-management.js`**: Criterion CRUD operations
- **`images/`**: Logo and favicon

#### `templates/` - HTML Templates
- **`index.html`**: Main application (essay library, evaluation, results)
- **`login.html`**: Authentication page

**Design Decision**: Using vanilla JavaScript instead of React/Vue for simplicity and no build step required.

### 5. `essay_evaluator/utils/` - Utility Modules

**Purpose**: Reusable utility functions and classes.

**Modules:**

#### `pdf/processor.py` - PDF Processing
- **Class**: `PDFProcessor`
- **Methods**: 
  - `extract_text_from_pdf()`: Extract raw text
  - `clean_text()`: Remove artifacts, normalize
  - `split_essay_and_annex()`: Separate main essay from AI annex

#### `database/connection.py` - Database Layer
- **Models**: `Ensayo`, `Usuario`, `CriterioPersonalizado`
- **Functions**: Database initialization, connection management
- **ORM**: SQLAlchemy for database abstraction

#### `validators.py` - Input Validation
- File type validation
- Size limits
- Text sanitization

### 6. `essay_evaluator/data/` - Data Storage

**Purpose**: Persistent data storage.

**Structure:**
- **`raw/`**: Original uploaded PDFs (not processed)
- **`processed/`**: Extracted and cleaned text files
- **`database/`**: SQLite database files

**Design Decision**: Keeps data separate from code for easy backup and migration.

### 7. `essay_evaluator/tests/` - Test Suite

**Purpose**: Automated testing for quality assurance.

**Test Types:**
- **Unit Tests**: Test individual functions/classes
- **Integration Tests**: Test API endpoints
- **Fixtures**: Reusable test data

**Run Tests:**
```bash
pytest essay_evaluator/tests/
pytest --cov=essay_evaluator --cov-report=html
```

---

## 🔧 Configuration Management

### `config/` Directory

**Purpose**: Environment-specific settings.

**Files:**

#### `development.py`
- Debug mode enabled
- Verbose logging
- Local database
- Relaxed security

#### `production.py`
- Debug mode disabled
- Error logging only
- PostgreSQL/remote database
- Strict security (HTTPS, CSRF)

#### `testing.py`
- In-memory database
- Mock external services
- Fast execution

**Usage:**
```python
import os
from config import development, production

config = production.config if os.getenv('FLASK_ENV') == 'production' else development.config
```

---

## 📜 Scripts Directory

### `scripts/` - Utility Scripts

**Purpose**: One-off operations and maintenance tasks.

**Scripts:**

#### `migrate_structure.py`
- Migrates files from old flat structure to new modular structure
- Creates directories
- Copies files
- Updates imports

**Run:**
```bash
python scripts/migrate_structure.py
```

#### `setup_database.py`
- Creates database tables
- Seeds initial data
- Creates default admin user

#### `batch_evaluate.py`
- Evaluate multiple essays at once
- Progress tracking
- Error handling

#### `load_processed_essays.py`
- Import existing essays from old system
- Migrate data to new database schema

---

## 📚 Documentation Structure

### `docs/` Directory

**Purpose**: Comprehensive project documentation.

**Structure:**

#### `architecture/` - Technical Documentation
- **`system_design.md`**: Architecture overview, design patterns
- **`data_flow.md`**: Data flow diagrams and sequence diagrams

#### `api/` - API Documentation
- **`endpoints.md`**: Complete API reference with examples
- Request/response formats
- Authentication
- Error codes

#### `user_guide/` - End-User Documentation
- **`getting_started.md`**: Installation and quick start
- **`admin_guide.md`**: Deployment and administration

---

## 🔄 Import Structure

### Clean Import Paths

The new structure enables clean, explicit imports:

```python
# Core business logic
from essay_evaluator.core.agent import EvaluadorEnsayos
from essay_evaluator.core.models.evaluation import EvaluacionEnsayo

# Utilities
from essay_evaluator.utils.pdf.processor import PDFProcessor
from essay_evaluator.utils.database.connection import db, Ensayo

# API components
from essay_evaluator.api.routes.auth import AuthManager
```

### Why This Matters

**Before (flat structure):**
```python
from agent import EvaluadorEnsayos  # What agent?
from models import EvaluacionEnsayo  # Which models?
```

**After (modular structure):**
```python
from essay_evaluator.core.agent import EvaluadorEnsayos  # Clear!
from essay_evaluator.core.models.evaluation import EvaluacionEnsayo  # Specific!
```

---

## 🚀 Running the Application

### Development Mode

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
python -m essay_evaluator.api.app

# Or with Flask CLI
export FLASK_APP=essay_evaluator.api.app
flask run --reload
```

### Production Mode

```bash
# Use production config
export FLASK_ENV=production

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 essay_evaluator.api.app:app
```

---

## 🧪 Testing Strategy

### Test Organization

```
essay_evaluator/tests/
├── test_agent.py          # Core agent tests
├── test_api.py            # API endpoint tests
├── test_pdf_processor.py  # PDF processing tests
└── fixtures/
    ├── sample_essay.pdf
    └── sample_response.json
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest essay_evaluator/tests/test_agent.py

# With coverage
pytest --cov=essay_evaluator --cov-report=html

# Verbose mode
pytest -v
```

---

## 📊 Benefits of This Structure

### 1. **Maintainability**
- Clear separation of concerns
- Easy to find and modify code
- Reduced cognitive load

### 2. **Testability**
- Each module can be tested independently
- Mock dependencies easily
- Clear test organization

### 3. **Scalability**
- Add new features without breaking existing code
- Easy to add new routes, models, or utilities
- Support for microservices migration

### 4. **Collaboration**
- New developers understand structure quickly
- Clear ownership of modules
- Reduces merge conflicts

### 5. **Reusability**
- Core logic can be used in CLI, API, or other interfaces
- Utilities are framework-agnostic
- Easy to create new applications using the same core

---

## 🔄 Migration Guide

### From Old Structure to New

**Run the migration script:**

```bash
python scripts/migrate_structure.py
```

**What it does:**
1. Creates new directory structure
2. Copies files to appropriate locations
3. Creates `__init__.py` files
4. Generates documentation

**Manual steps after migration:**
1. Update imports in copied files
2. Test all functionality
3. Update deployment scripts
4. Archive old files

**Update imports:**

```python
# Old
from agent import EvaluadorEnsayos

# New
from essay_evaluator.core.agent import EvaluadorEnsayos
```

---

## 📝 Best Practices

### When Adding New Code

1. **New API Endpoint**: Add to `api/routes/`
2. **New Model**: Add to `core/models/`
3. **New Utility**: Add to `utils/`
4. **New Test**: Add to `tests/`

### File Naming Conventions

- **Python files**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_CASE`

### Documentation Requirements

- Every module has a docstring
- Every public function has a docstring
- Complex logic has inline comments
- API endpoints documented in `docs/api/`

---

## 🎓 Learning Path

For new developers joining the project:

1. **Start here**: `PROJECT_STRUCTURE.md` (this file)
2. **Understand core**: `essay_evaluator/core/` modules
3. **Review architecture**: `docs/architecture/system_design.md`
4. **Get started**: `docs/user_guide/getting_started.md`
5. **API reference**: `docs/api/endpoints.md`
6. **Run tests**: `pytest essay_evaluator/tests/`
7. **Make changes**: Pick an issue from GitHub

---

## 🤝 Contributing

When contributing to this project:

1. **Follow the structure**: Place new code in appropriate modules
2. **Write tests**: Every new feature needs tests
3. **Document**: Update docs when adding features
4. **Use type hints**: Python 3.8+ type annotations
5. **Format code**: Use Black formatter
6. **Check imports**: Use isort for import ordering

---

## 📞 Questions?

If you have questions about the project structure:

1. Check this document first
2. Review `docs/` directory
3. Look at existing code examples
4. Open an issue on GitHub
5. Contact the maintainers

---

**Last Updated**: November 2025  
**Maintained by**: Vania Janet  
**Version**: 1.0.0
