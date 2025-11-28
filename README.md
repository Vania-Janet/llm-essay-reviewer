# Essay Agent - Sistema de Evaluación de Ensayos con IA

Sistema completo para la evaluación automatizada de ensayos académicos utilizando modelos de lenguaje avanzados (LLMs). Incluye autenticación de usuarios, gestión de ensayos, evaluación mediante IA, sistema de jurados, y generación de reportes en PDF.

## Tabla de Contenidos

- [Características Principales](#características-principales)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Testing](#testing)
- [Despliegue en Producción](#despliegue-en-producción)
- [API Endpoints](#api-endpoints)

## Características Principales

### Sistema de Autenticación
- Registro y login de usuarios con validación robusta
- Tokens JWT con expiración configurable
- Hashing de contraseñas con bcrypt (12 rounds)
- Gestión de roles (usuario, jurado, admin)
- Rate limiting para prevenir ataques de fuerza bruta

### Evaluación de Ensayos
- Subida y procesamiento de archivos PDF
- Extracción de texto con pdfplumber
- Evaluación automatizada mediante OpenAI GPT-4
- Detección y emparejamiento de anexos IA
- Criterios de evaluación personalizables:
  - Calidad técnica
  - Creatividad
  - Vinculación temática
  - Bienestar colectivo
  - Uso responsable de IA
  - Potencial de impacto

### Sistema de Jurados
- Evaluación manual por múltiples jurados
- Comparación de evaluaciones IA vs Jurado
- Sistema de pesos personalizables por criterio
- Gestión de estados (borrador, completada)
- Tracking de cambios y fecha de completado

### Reportes y Análisis
- Generación de reportes PDF profesionales
- Rankings de ensayos por puntuación
- Estadísticas de evaluaciones
- Historial de evaluaciones por jurado
- Comparativas entre evaluaciones

### Interfaz de Usuario
- Panel de administración completo
- Interfaz de chat para consultas sobre ensayos
- Visualización de evaluaciones en tiempo real
- Gestión de criterios personalizados
- Panel de estadísticas

## Arquitectura del Sistema

### Stack Tecnológico

**Backend:**
- Flask 3.0+ (Framework web)
- SQLAlchemy (ORM)
- Flask-Migrate (Migraciones de BD)
- Flask-Limiter (Rate limiting)

**Autenticación y Seguridad:**
- bcrypt (Hashing de contraseñas)
- PyJWT (Tokens JWT)
- Flask-CORS (Control de CORS)

**IA y Procesamiento:**
- LangChain (Framework LLM)
- LangGraph (Orchestration)
- OpenAI GPT-4 (Modelo de lenguaje)
- pypdf/pdfplumber (Procesamiento PDF)

**Reportes:**
- ReportLab (Generación PDF)

**Base de Datos:**
- SQLite (Desarrollo)
- PostgreSQL (Recomendado para producción)

### Patrones de Diseño

**Factory Pattern:** Creación de la aplicación Flask con diferentes configuraciones

**Blueprint Pattern:** Organización modular de rutas (auth, essays, evaluation, admin)

**Middleware Pattern:** Manejo de autenticación, rate limiting y logging

**Repository Pattern:** Modelos SQLAlchemy como capa de acceso a datos

## Estructura del Proyecto

```
essay-agent/
├── app/
│   ├── __init__.py
│   ├── config.py                 # Configuración por entornos
│   ├── api/
│   │   ├── __init__.py
│   │   ├── middleware.py         # Rate limiting y auth manager
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py          # Login, registro, logout
│   │       ├── essays.py        # CRUD de ensayos
│   │       ├── evaluation.py    # Evaluación y chat
│   │       └── admin.py         # Panel de administración
│   ├── core/
│   │   ├── __init__.py
│   │   ├── evaluator.py         # Motor de evaluación IA
│   │   ├── models.py            # Modelos LangChain
│   │   └── prompts.py           # Prompts para el LLM
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py        # Inicialización SQLAlchemy
│   │   └── models.py            # Modelos de BD (Usuario, Ensayo, etc.)
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py          # AuthManager, JWT, bcrypt
│   │   ├── pdf_processor.py    # Extracción de texto PDF
│   │   ├── attachment_matcher.py # Emparejamiento anexos
│   │   ├── logger.py            # Sistema de logging
│   │   └── report_generator.py # Generación reportes PDF
│   ├── static/
│   │   ├── styles.css
│   │   ├── script.js
│   │   ├── main.js
│   │   ├── grading_cockpit.js
│   │   └── criteria_management.js
│   └── templates/
│       ├── index.html           # Dashboard principal
│       └── login.html           # Página de login
├── data/
│   ├── pdfs/                    # Ensayos PDF
│   ├── anexos/                  # Anexos IA
│   ├── processed/               # Archivos procesados
│   ├── uploads/                 # Uploads temporales
│   └── essays.db                # Base de datos SQLite
├── migrations/                  # Migraciones Alembic
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures pytest
│   ├── test_unit.py             # Tests unitarios
│   ├── test_integration.py      # Tests de integración
│   ├── test_production.py       # Tests de producción
│   └── test_load.py             # Tests de carga
├── scripts/
│   ├── evaluar_pdfs.py          # Script de evaluación batch
│   ├── generar_excel_profesional.py
│   ├── load_processed_essays.py
│   └── matches_ia.py            # Emparejamiento anexos
├── run.py                       # Entry point de la aplicación
├── manage.py                    # CLI para migraciones
├── requirements.txt             # Dependencias Python
├── .env.example                 # Plantilla de variables de entorno
└── README.md                    # Este archivo
```

## Requisitos del Sistema

### Software
- Python 3.10 o superior
- pip (gestor de paquetes Python)
- Virtual environment (recomendado)

### Servicios Externos
- OpenAI API Key (para evaluación con GPT-4)

### Opcional
- PostgreSQL 13+ (para producción)
- Redis (para caché y rate limiting avanzado)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Vania-Janet/llm-essay-reviewer.git
cd essay-agent
```

### 2. Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar (macOS/Linux)
source .venv/bin/activate

# Activar (Windows)
.venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copiar el archivo de ejemplo y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=tu-secret-key-muy-segura-aqui
DEBUG=True

# OpenAI
OPENAI_API_KEY=sk-tu-api-key-aqui

# JWT
JWT_SECRET_KEY=tu-jwt-secret-key-aqui

# Database (opcional, por defecto usa SQLite)
# DATABASE_URL=postgresql://usuario:password@localhost/essays_db

# CORS (opcional)
CORS_ORIGINS=http://localhost:3000,http://localhost:5001
```

### 5. Inicializar Base de Datos

```bash
# Crear las tablas
python manage.py init

# Aplicar migraciones (si existen)
python manage.py upgrade
```

## Configuración

### Configuración por Entornos

El sistema soporta tres entornos configurables:

**Development** (`development`)
- Debug habilitado
- Base de datos SQLite local
- CORS permisivo
- Logging detallado

**Testing** (`testing`)
- Base de datos temporal
- Rate limiting deshabilitado
- Configuración optimizada para tests

**Production** (`production`)
- Debug deshabilitado
- Validación estricta de secrets
- HTTPS requerido
- Rate limiting estricto

### Cambiar de Entorno

```bash
export FLASK_ENV=production
python run.py
```

## Uso

### Iniciar el Servidor

```bash
# Desarrollo (puerto 5001)
python run.py

# Especificar puerto
PORT=8000 python run.py

# Producción
FLASK_ENV=production python run.py
```

La aplicación estará disponible en `http://localhost:5001`

### Crear Usuario Administrador

```python
python manage.py create-admin
```

### Evaluar Ensayos en Batch

```bash
python scripts/evaluar_pdfs.py
```

### Generar Reporte Excel

```bash
python scripts/generar_excel_profesional.py
```

## Testing

### Ejecutar Todos los Tests

```bash
pytest tests/ -v
```

### Tests por Categoría

```bash
# Tests unitarios
pytest tests/test_unit.py -v

# Tests de integración
pytest tests/test_integration.py -v

# Tests de producción
pytest tests/test_production.py -v

# Tests de carga
pytest tests/test_load.py -v
```

### Tests con Cobertura

```bash
pytest tests/ --cov=app --cov-report=html
```

### Tests en Paralelo

```bash
pytest tests/ -v -n auto
```

## Despliegue en Producción

### Checklist Pre-Producción

- [ ] Configurar `SECRET_KEY` y `JWT_SECRET_KEY` únicos
- [ ] Configurar `OPENAI_API_KEY`
- [ ] Cambiar a PostgreSQL (recomendado)
- [ ] Habilitar HTTPS
- [ ] Configurar `secure=True` en cookies
- [ ] Configurar sistema de logging
- [ ] Configurar backups de base de datos
- [ ] Configurar monitoreo (Sentry, etc.)
- [ ] Revisar rate limits
- [ ] Configurar CORS apropiadamente

### Base de Datos PostgreSQL

```bash
# Instalar driver
pip install psycopg2-binary

# Configurar DATABASE_URL en .env
DATABASE_URL=postgresql://usuario:password@localhost:5432/essays_db
```

### Servidor WSGI (Gunicorn)

```bash
# Instalar Gunicorn
pip install gunicorn

# Ejecutar
gunicorn -w 4 -b 0.0.0.0:8000 "run:create_app('production')"
```

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:create_app('production')"]
```

## API Endpoints

### Autenticación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/register` | Registrar nuevo usuario | No |
| POST | `/api/login` | Iniciar sesión | No |
| POST | `/api/logout` | Cerrar sesión | Sí |
| GET | `/api/verify-token` | Verificar token válido | Sí |
| POST | `/api/change-password` | Cambiar contraseña | Sí |

### Ensayos

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/essays` | Listar todos los ensayos | Sí |
| GET | `/api/essays/:id` | Obtener ensayo específico | Sí |
| POST | `/api/evaluate` | Subir y evaluar PDF | Sí |
| GET | `/api/essays/ranking` | Ranking de ensayos | Sí |
| GET | `/api/essays/:id/evaluation` | Ver evaluación | Sí |
| DELETE | `/api/essays/:id` | Eliminar ensayo | Admin |

### Evaluación

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/chat` | Chat sobre ensayo | Sí |
| POST | `/api/essays/:id/evaluate` | Evaluar como jurado | Jurado |
| GET | `/api/jurado/evaluations` | Mis evaluaciones | Jurado |
| POST | `/api/essays/:id/report` | Generar reporte PDF | Sí |

### Administración

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/admin/users` | Listar usuarios | Admin |
| GET | `/api/admin/statistics` | Estadísticas | Admin |
| PUT | `/api/admin/users/:id` | Editar usuario | Admin |
| DELETE | `/api/admin/users/:id` | Eliminar usuario | Admin |

### Criterios Personalizados

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/api/criterios` | Listar criterios | Sí |
| POST | `/api/criterios` | Crear criterio | Jurado |
| PUT | `/api/criterios/:id` | Actualizar criterio | Jurado |
| DELETE | `/api/criterios/:id` | Eliminar criterio | Jurado |

### Health Check

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Estado del servidor | No |
| GET | `/api/db-status` | Estado de la BD | No |

## Modelos de Base de Datos

### Usuario
- Autenticación y autorización
- Roles: usuario, jurado, admin
- Tracking de último acceso

### Ensayo
- Contenido del ensayo (texto, PDF)
- Evaluación automatizada
- Hash de texto para prevenir duplicados
- Relación con anexos IA

### EvaluacionJurado
- Evaluaciones manuales por jurados
- Múltiples criterios de evaluación
- Estados: borrador, completada
- Cálculo automático de puntuación total

### CriterioPersonalizado
- Criterios definidos por usuarios
- Sistema de pesos configurables
- Ordenamiento personalizable

### Comparacion
- Comparación IA vs Jurado
- Tracking de diferencias
- Análisis de discrepancias

### PuntajeCriterio
- Puntuaciones por criterio individual
- Comentarios detallados
- Tracking de cambios

## Seguridad

### Implementaciones de Seguridad

- Hashing de contraseñas con bcrypt (12 rounds)
- Tokens JWT con expiración (24 horas por defecto)
- Rate limiting en endpoints sensibles
- Validación de entrada en todos los endpoints
- HttpOnly cookies para tokens
- CORS configurable
- Prevención de SQL injection (SQLAlchemy ORM)
- Validación de tipos de archivo
- Límite de tamaño de archivo (16MB)

### Recomendaciones Adicionales

Para producción, considera implementar:
- HTTPS obligatorio
- CSRF protection
- Content Security Policy headers
- Monitoreo de actividad sospechosa
- Rotación periódica de secrets
- Auditoría de accesos

## Soporte y Contribuciones

Para reportar problemas o solicitar características:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

Para contribuir:
1. Fork del repositorio
2. Crear rama para feature
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## Licencia

Este proyecto es privado y confidencial. Todos los derechos reservados.

## Contacto

Para más información, contactar al equipo de desarrollo del proyecto.

---

**Nota:** Este README asume que el proyecto está en desarrollo activo. Actualizar la documentación conforme se agreguen nuevas características o se realicen cambios significativos.
