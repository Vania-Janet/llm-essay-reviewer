# Essay Evaluator - AI-Powered Academic Essay Assessment System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, automated academic essay evaluation system powered by GPT-4, LangGraph, and LangChain. This system provides comprehensive, multi-criteria assessment of academic essays with detailed feedback and professional reporting.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Capabilities
- **Multi-Criteria Evaluation**: 6 rigorous academic criteria with weighted scoring
- **AI-Powered Analysis**: GPT-4 with structured outputs for precise evaluations
- **PDF Processing**: Intelligent extraction and cleaning of essay documents
- **Batch Processing**: Evaluate multiple essays simultaneously
- **Professional Reports**: Generate detailed HTML/PDF evaluation reports
- **Comparison Tools**: Side-by-side analysis of multiple essays
- **Statistics Dashboard**: Visual analytics with Chart.js

### Web Interface
- **Modern UI**: Clean, responsive design with drag-and-drop upload
- **User Authentication**: Secure JWT-based authentication
- **Essay Library**: Browse, search, and manage evaluated essays
- **Interactive Chat**: Ask questions about essays and evaluations
- **Real-time Processing**: Progress indicators for batch evaluations
- **Export Capabilities**: Download results as Excel/CSV

### Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Technical Quality** | 16.7% | Structure, coherence, and academic rigor |
| **Creativity** | 16.7% | Innovation and original thinking |
| **Thematic Alignment** | 16.7% | Relevance to contest themes |
| **Social Responsibility** | 16.7% | Ethical and sustainability considerations |
| **AI Usage** | 16.7% | Responsible and reflective use of AI tools |
| **Impact Potential** | 16.7% | Publication quality and potential influence |

**Scoring**: Each criterion scored 1-5 with detailed justification

---

## 📁 Project Structure

```
essay-agent/
├── essay_evaluator/              # Main application package
│   ├── __init__.py
│   ├── core/                     # Core business logic
│   │   ├── __init__.py
│   │   ├── agent/                # LangGraph agent
│   │   │   ├── __init__.py
│   │   │   ├── evaluator.py     # Main evaluation agent
│   │   │   └── graph.py         # Graph construction
│   │   ├── evaluation/           # Evaluation logic
│   │   │   ├── __init__.py
│   │   │   ├── criteria.py      # Criterion evaluators
│   │   │   └── prompts.py       # LLM prompts
│   │   └── models/               # Data models
│   │       ├── __init__.py
│   │       ├── essay.py         # Essay models
│   │       └── evaluation.py    # Evaluation models
│   │
│   ├── api/                      # REST API
│   │   ├── __init__.py
│   │   ├── app.py               # Flask application
│   │   ├── routes/              # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── essays.py        # Essay operations
│   │   │   └── evaluation.py   # Evaluation endpoints
│   │   └── middleware/          # API middleware
│   │       ├── __init__.py
│   │       ├── auth.py          # JWT verification
│   │       └── error_handlers.py
│   │
│   ├── web/                      # Web interface
│   │   ├── static/              # Static assets
│   │   │   ├── css/
│   │   │   │   └── styles.css
│   │   │   ├── js/
│   │   │   │   ├── script.js
│   │   │   │   └── criteria-management.js
│   │   │   └── images/
│   │   │       ├── icon.png
│   │   │       └── logo.png
│   │   └── templates/           # HTML templates
│   │       ├── index.html
│   │       └── login.html
│   │
│   ├── utils/                    # Utility modules
│   │   ├── __init__.py
│   │   ├── pdf/                 # PDF processing
│   │   │   ├── __init__.py
│   │   │   ├── extractor.py    # PDF text extraction
│   │   │   └── cleaner.py      # Text cleaning
│   │   ├── database/            # Database utilities
│   │   │   ├── __init__.py
│   │   │   ├── connection.py   # DB connection
│   │   │   └── operations.py   # CRUD operations
│   │   └── validators.py       # Input validation
│   │
│   ├── data/                     # Data storage
│   │   ├── raw/                 # Raw uploaded PDFs
│   │   ├── processed/           # Processed texts
│   │   └── database/            # SQLite database
│   │       └── essays.db
│   │
│   └── tests/                    # Test suite
│       ├── __init__.py
│       ├── test_agent.py
│       ├── test_api.py
│       ├── test_pdf_processor.py
│       └── fixtures/
│
├── scripts/                      # Utility scripts
│   ├── load_processed_essays.py # Migrate existing data
│   ├── setup_database.py       # Initialize database
│   └── batch_evaluate.py       # Batch processing
│
├── docs/                         # Documentation
│   ├── architecture/            # Architecture docs
│   │   ├── system_design.md
│   │   └── data_flow.md
│   ├── api/                     # API documentation
│   │   └── endpoints.md
│   └── user_guide/              # User guides
│       ├── getting_started.md
│       └── admin_guide.md
│
├── config/                       # Configuration files
│   ├── development.py
│   ├── production.py
│   └── testing.py
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package installation
├── pytest.ini                    # Pytest configuration
├── README.md                     # This file
└── LICENSE                       # License file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenAI API key
- (Optional) Redis for caching

### Step 1: Clone the Repository

```bash
git clone https://github.com/Vania-Janet/llm-essay-reviewer.git
cd llm-essay-reviewer
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

Required environment variables:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Database
DATABASE_URL=sqlite:///essay_evaluator/data/database/essays.db

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development

# JWT Authentication
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ACCESS_TOKEN_EXPIRES=3600

# Upload Settings
UPLOAD_FOLDER=essay_evaluator/data/raw
MAX_UPLOAD_SIZE=10485760  # 10MB

# Optional: Redis Cache
REDIS_URL=redis://localhost:6379/0
```

### Step 5: Initialize Database

```bash
python scripts/setup_database.py
```

---

## 🎯 Quick Start

### Run Web Application

```bash
# Start the Flask web server
python -m essay_evaluator.api.app

# Access the application at:
# http://localhost:5000
```

### Command Line Usage

```python
from essay_evaluator.core.agent import EvaluadorEnsayos

# Initialize evaluator
evaluator = EvaluadorEnsayos()

# Evaluate an essay
with open('essay.txt', 'r') as f:
    essay_text = f.read()

evaluation = evaluator.evaluar(essay_text)
print(f"Score: {evaluation.puntuacion_total:.2f}/5.0")
```

### Batch Processing

```bash
# Evaluate all PDFs in a folder
python scripts/batch_evaluate.py --input pdfs/ --output results/
```

---

## 📖 Usage

### Web Interface

1. **Login**: Access the system at `http://localhost:5000`
2. **Upload Essay**: Drag & drop PDF or use file selector
3. **View Results**: Review detailed evaluation with scores and feedback
4. **Compare Essays**: Select multiple essays for side-by-side comparison
5. **Export**: Download results as Excel or PDF report

### API Endpoints

#### Authentication
```bash
# Register user
POST /api/auth/register
{
  "username": "admin",
  "password": "secure_password"
}

# Login
POST /api/auth/login
{
  "username": "admin",
  "password": "secure_password"
}
```

#### Essay Evaluation
```bash
# Upload and evaluate essay
POST /api/essays/evaluate
Content-Type: multipart/form-data
Authorization: Bearer <token>

# Get essay by ID
GET /api/essays/{essay_id}
Authorization: Bearer <token>

# List all essays
GET /api/essays
Authorization: Bearer <token>

# Compare essays
POST /api/essays/compare
{
  "essay_ids": [1, 2, 3]
}
```

See [API Documentation](docs/api/endpoints.md) for complete reference.

---

## ⚙️ Configuration

### Evaluation Settings

Customize evaluation behavior in `config/development.py`:

```python
EVALUATION_CONFIG = {
    'model': 'gpt-4o',  # or 'gpt-4o-mini' for faster/cheaper
    'temperature': 0.3,
    'max_tokens': 2000,
    'parallel_execution': True,  # Enable parallel criterion evaluation
    'criteria_weights': {
        'calidad_tecnica': 0.167,
        'creatividad': 0.167,
        'vinculacion_tematica': 0.167,
        'bienestar_colectivo': 0.167,
        'uso_responsable_ia': 0.167,
        'potencial_impacto': 0.167
    }
}
```

### Performance Tuning

- **Caching**: Enable Redis for 10x faster repeat evaluations
- **Batch Size**: Adjust `BATCH_SIZE` for concurrent processing
- **Timeouts**: Configure `REQUEST_TIMEOUT` for long documents

---

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suite

```bash
# Test agent
pytest essay_evaluator/tests/test_agent.py

# Test API
pytest essay_evaluator/tests/test_api.py -v

# Test with coverage
pytest --cov=essay_evaluator --cov-report=html
```

---

## 🛠️ Development

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Format code
black essay_evaluator/

# Lint code
flake8 essay_evaluator/

# Type checking
mypy essay_evaluator/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

---

## 📊 Architecture

### System Components

1. **Core Agent**: LangGraph-based parallel evaluation engine
2. **API Layer**: RESTful Flask API with JWT authentication
3. **Web Interface**: Responsive SPA with vanilla JavaScript
4. **Database**: SQLite with SQLAlchemy ORM
5. **PDF Processor**: PyPDF + pdfplumber for text extraction

### Data Flow

```
PDF Upload → Text Extraction → Agent Evaluation → Database Storage → Report Generation
     ↓                             ↓
Validation                   Parallel Criteria
     ↓                       Processing (6 nodes)
Preprocessing                        ↓
                              Final Synthesis
```

See [Architecture Documentation](docs/architecture/system_design.md) for details.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

Please ensure:
- All tests pass
- Code is formatted with Black
- Documentation is updated
- Type hints are added

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Vania Janet** - *Initial work* - [Vania-Janet](https://github.com/Vania-Janet)

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- LangChain team for excellent LLM framework
- Flask community for web framework
- All contributors and testers

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Vania-Janet/llm-essay-reviewer/issues)
- **Documentation**: [Full Documentation](docs/)
- **Email**: support@example.com

---

## 🗺️ Roadmap

- [ ] Add support for more document formats (DOCX, TXT)
- [ ] Implement multi-language support
- [ ] Add plagiarism detection
- [ ] Create mobile app
- [ ] Integrate more LLM providers (Anthropic, Cohere)
- [ ] Add advanced analytics dashboard
- [ ] Implement peer review workflow
- [ ] Export to LaTeX/Academic formats
