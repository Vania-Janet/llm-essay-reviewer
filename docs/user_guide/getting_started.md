# Getting Started with Essay Evaluator

## Quick Start Guide

This guide will help you get the Essay Evaluator system up and running in minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.8 or higher installed
- ✅ pip package manager
- ✅ OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- ✅ Basic command line knowledge
- ✅ Text editor or IDE (VS Code recommended)

## Installation Steps

### Step 1: Clone the Repository

```bash
git clone https://github.com/Vania-Janet/llm-essay-reviewer.git
cd llm-essay-reviewer
```

### Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Your prompt should now show (.venv)
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import flask; import langchain; print('Dependencies installed successfully!')"
```

### Step 4: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
nano .env  # or use your preferred editor
```

**Required Configuration:**

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-openai-key-here
OPENAI_MODEL=gpt-4o
FLASK_SECRET_KEY=change-this-to-random-string
JWT_SECRET_KEY=change-this-to-another-random-string
```

**Generate Secret Keys:**

```bash
# Generate secure random keys
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

### Step 5: Initialize Database

```bash
# Create database and tables
python scripts/setup_database.py
```

Expected output:
```
✅ Database initialized successfully
✅ Default admin user created: admin / admin123
```

### Step 6: Run the Application

```bash
# Start the web server
python -m essay_evaluator.api.app

# Or use the old path (if not migrated yet)
# python web/app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Step 7: Access the Application

1. Open your browser
2. Navigate to: `http://localhost:5000`
3. Login with default credentials:
   - Username: `admin`
   - Password: `admin123`
   - **⚠️ Change these immediately after first login!**

## First Evaluation

### Using the Web Interface

1. **Login** to the system
2. Click **"➕ Evaluar Nuevo Ensayo"**
3. **Upload** a PDF essay (max 10MB)
4. Wait for processing (10-15 seconds)
5. **View** detailed results with scores and feedback

### Using Python API

```python
from essay_evaluator.core.agent import EvaluadorEnsayos

# Initialize evaluator
evaluator = EvaluadorEnsayos()

# Load essay text
with open('my_essay.txt', 'r', encoding='utf-8') as f:
    essay_text = f.read()

# Evaluate
evaluation = evaluator.evaluar(essay_text)

# View results
print(f"Overall Score: {evaluation.puntuacion_total:.2f}/5.0")
print(f"Technical Quality: {evaluation.calidad_tecnica.calificacion}/5")
print(f"Creativity: {evaluation.creatividad.calificacion}/5")
print(f"\nGeneral Feedback:\n{evaluation.comentario_general}")
```

## Common Issues & Solutions

### Issue 1: Module Not Found

**Error:** `ModuleNotFoundError: No module named 'langchain'`

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: OpenAI API Error

**Error:** `AuthenticationError: Invalid API key`

**Solution:**
1. Check your `.env` file has the correct API key
2. Verify the key is active at https://platform.openai.com/api-keys
3. Ensure `.env` is in the project root directory
4. Restart the server after changing `.env`

### Issue 3: Database Error

**Error:** `OperationalError: no such table: essays`

**Solution:**
```bash
# Reinitialize database
python scripts/setup_database.py
```

### Issue 4: Port Already in Use

**Error:** `OSError: [Errno 48] Address already in use`

**Solution:**
```bash
# Find process using port 5000
lsof -ti:5000 | xargs kill -9

# Or run on different port
flask run --port 5001
```

## Configuration Options

### Model Selection

Edit `.env` to change the GPT model:

```env
# Faster and cheaper (recommended for testing)
OPENAI_MODEL=gpt-4o-mini

# More accurate (recommended for production)
OPENAI_MODEL=gpt-4o

# Most powerful (highest cost)
OPENAI_MODEL=gpt-4-turbo
```

### Upload Limits

```env
# Maximum file size (in bytes)
MAX_UPLOAD_SIZE=10485760  # 10MB
MAX_UPLOAD_SIZE=20971520  # 20MB
```

### Evaluation Behavior

Edit `config/development.py`:

```python
EVALUATION_CONFIG = {
    'model': 'gpt-4o-mini',  # Model to use
    'temperature': 0.3,      # 0.0-1.0 (lower = more consistent)
    'max_tokens': 2000,      # Max tokens per response
    'parallel_execution': True,  # Enable parallel evaluation
}
```

## Next Steps

Now that you have the system running:

1. ✅ **Change default password** in user settings
2. 📚 Read [API Documentation](../api/endpoints.md) for programmatic access
3. 🎨 Customize evaluation criteria in the admin panel
4. 📊 Explore the statistics dashboard
5. 🔍 Try comparing multiple essays
6. 📖 Review [Architecture Documentation](../architecture/system_design.md)

## Getting Help

- **Documentation**: Browse the `docs/` folder
- **Issues**: Report bugs on [GitHub Issues](https://github.com/Vania-Janet/llm-essay-reviewer/issues)
- **Examples**: Check `examples/` folder for code samples

## Performance Tips

### Speed Up Evaluations

1. **Use parallel execution** (enabled by default)
2. **Switch to gpt-4o-mini** for faster processing
3. **Enable Redis caching** for repeat evaluations
4. **Reduce max_tokens** if feedback is too long

### Reduce Costs

1. **Use gpt-4o-mini** instead of gpt-4o
2. **Cache evaluations** with Redis
3. **Batch process** multiple essays
4. **Set appropriate token limits**

### Cost Estimation

Approximate costs per essay (USD):

| Model | Cost per Essay | Processing Time |
|-------|---------------|----------------|
| gpt-4o-mini | $0.01-0.02 | 5-8 seconds |
| gpt-4o | $0.05-0.10 | 10-15 seconds |
| gpt-4-turbo | $0.15-0.25 | 15-20 seconds |

*Actual costs depend on essay length and token usage*

## Development Mode

For development with auto-reload:

```bash
# Set environment
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run with auto-reload
flask run --reload
```

## Production Deployment

See [Admin Guide](admin_guide.md) for production deployment instructions.

---

**Congratulations! 🎉** You're now ready to start evaluating essays with AI!
