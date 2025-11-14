# Agente Evaluador de Ensayos 🎓

Sistema de evaluación automática de ensayos usando **LangGraph** y **LangChain** con GPT-4.

## ✨ Características Principales

- ✅ **Evaluación automatizada** con 5 criterios académicos rigurosos
- 📄 **Procesamiento de PDFs** con extracción y limpieza inteligente
- 🧹 **Limpieza de texto con LLM** para PDFs mal formateados
- 📊 **Reportes HTML** detallados y visualmente atractivos
- 🔄 **Procesamiento por lotes** de múltiples ensayos
- 🎯 **Structured output** para calificaciones precisas

## 📋 Criterios de Evaluación

Este agente evalúa ensayos académicos según 5 criterios específicos con ponderaciones establecidas:

1. **Calidad técnica y rigor académico (20%)** - Estructura, coherencia y solidez argumentativa
2. **Creatividad y originalidad (20%)** - Ideas nuevas y enfoques innovadores
3. **Vinculación con ejes temáticos (20%)** - Tecnología, sostenibilidad, inclusión
4. **Bienestar colectivo y responsabilidad social (20%)** - Impactos sociales, éticos y ambientales
5. **Potencial de impacto y publicación (20%)** - Capacidad de comunicar e inspirar

Cada criterio se evalúa en una escala del 1 al 5 con comentarios detallados.

## 🏗️ Arquitectura

El sistema utiliza **LangGraph** para crear un grafo de evaluación secuencial:

```
Inicio → Calidad Técnica → Creatividad → Vinculación → Bienestar → Impacto → Comentario General → Fin
```

Cada nodo del grafo:
- Evalúa un criterio específico usando prompts especializados
- Asigna una calificación (1-5)
- Genera comentarios detallados
- Pasa el estado al siguiente nodo

## 📁 Estructura del Proyecto

```
essay-agent/
├── .env                    # Variables de entorno (OPENAI_API_KEY)
├── requirements.txt        # Dependencias del proyecto
├── models.py              # Modelos Pydantic para datos
├── prompts.py             # Prompts del sistema
├── agent.py               # Agente evaluador con LangGraph
├── pdf_processor.py       # Procesador de PDFs con limpieza LLM
├── main.py                # Script para evaluar ensayos .txt
├── evaluar_batch.py       # Evaluación masiva de archivos .txt
├── evaluar_pdfs.py        # Evaluación directa desde PDFs
└── README.md              # Este archivo
```

## 🚀 Instalación

1. **Clonar o descargar el proyecto**

```bash
git clone https://github.com/Vania-Janet/llm-essay-reviewer.git
cd llm-essay-reviewer
```

2. **Instalar dependencias**:

```bash
pip install -r requirements.txt
```

**Nota**: Esto instalará automáticamente:
- `langchain`, `langgraph`, `langchain-openai` (evaluación con LLMs)
- `pypdf` y `pdfplumber` (procesamiento de PDFs)
- `pydantic`, `python-dotenv` (utilidades)

3. **Configurar variables de entorno**:

Crea o edita el archivo `.env`:
```env
OPENAI_API_KEY=tu_clave_de_openai_aqui
```

**Obtener API key**: https://platform.openai.com/api-keys

4. **Verificar instalación**:

```bash
python test_pdf_processor.py
```

## 💻 Uso

### Opción 1: Evaluar ensayos desde PDFs (Recomendado)

```bash
python evaluar_pdfs.py
```

Este script:
1. Extrae texto del PDF usando pypdf o pdfplumber
2. Limpia el texto con LLM (quita números de página, une líneas cortadas, etc.)
3. Evalúa el ensayo con los 5 criterios
4. Genera reportes HTML detallados

**Ejemplo de uso programático:**
```python
from evaluar_pdfs import evaluar_pdf

# Evaluar un PDF individual
evaluacion = evaluar_pdf("mi_ensayo.pdf", output_dir="reportes")

# Evaluar todos los PDFs de un directorio
from evaluar_pdfs import evaluar_directorio_pdfs
evaluar_directorio_pdfs("pdfs_ensayos/", output_dir="reportes")
```

### Opción 2: Evaluar archivos de texto

```bash
python main.py
```

### Opción 3: Evaluación masiva de archivos .txt

```bash
python evaluar_batch.py
```

### Opción 4: Procesar PDFs sin evaluar (solo limpieza)

```bash
python pdf_processor.py
```

### Uso programático básico:

```python
from agent import EvaluadorEnsayos

# Crear el evaluador
evaluador = EvaluadorEnsayos()

# Evaluar un ensayo
ensayo = """
Tu ensayo aquí...
"""

evaluacion = evaluador.evaluar(ensayo)

# Acceder a los resultados
print(f"Puntuación total: {evaluacion.puntuacion_total}/5.00")
print(f"Calidad técnica: {evaluacion.calidad_tecnica.calificacion}/5")
print(f"Comentario: {evaluacion.comentario_general}")
```

### Procesamiento de PDFs (solo extracción y limpieza):

```python
from pdf_processor import PDFProcessor

processor = PDFProcessor()

# Procesar un PDF individual
texto_limpio = processor.procesar_pdf(
    "ensayo.pdf",
    output_path="ensayo_limpio.txt",
    limpiar=True  # Usa LLM para limpiar el texto
)

# Procesar directorio completo
textos = processor.procesar_directorio(
    "pdfs/",
    output_dir="textos_limpios/",
    limpiar=True
)
```

## 📊 Resultados

El sistema genera:

1. **Texto limpio** (si se procesa desde PDF): Ensayo sin números de página, líneas cortadas arregladas
2. **Reporte en consola**: Evaluación completa con todas las calificaciones y comentarios
3. **Reporte HTML**: Documento visualmente atractivo con toda la evaluación
4. **Objeto Python**: `EvaluacionEnsayo` con todos los datos estructurados para análisis posterior

### Ejemplo de salida:

```
📝 1. CALIDAD TÉCNICA Y RIGOR ACADÉMICO (20%)
   Calificación: 4/5
   El ensayo presenta una estructura coherente y argumentos bien sustentados...

🎨 2. CREATIVIDAD Y ORIGINALIDAD (20%)
   Calificación: 5/5
   Destacable propuesta de "tecnología educativa comunitaria"...

🎯 PUNTUACIÓN TOTAL PONDERADA: 4.35/5.00
```

## 🔧 Personalización

### Cambiar modelo de IA:

```python
# Para evaluación
evaluador = EvaluadorEnsayos(
    model_name="gpt-4o-mini",  # Más económico
    temperature=0.3
)

# Para limpieza de PDFs
processor = PDFProcessor(
    model_name="gpt-4o-mini",  # Suficiente para limpieza
    temperature=0.1  # Baja para mantener fidelidad
)
```

### Modificar prompts:

Edita `prompts.py` para ajustar los criterios de evaluación o el tono de los comentarios.

### Ajustar ponderaciones:

Modifica el método `calcular_puntuacion_total()` en `models.py`.

### Elegir método de extracción de PDF:

```python
# Automático (prefiere pdfplumber)
processor.procesar_pdf("ensayo.pdf", metodo="auto")

# Específico
processor.procesar_pdf("ensayo.pdf", metodo="pypdf")  # Más rápido
processor.procesar_pdf("ensayo.pdf", metodo="pdfplumber")  # Mejor calidad
```

## 🛠️ Tecnologías

- **LangChain**: Framework para aplicaciones con LLMs
- **LangGraph**: Orquestación de flujos complejos con grafos
- **OpenAI GPT-4**: Modelo de lenguaje para evaluación
- **Pydantic**: Validación de datos y modelos estructurados
- **pypdf / pdfplumber**: Extracción de texto desde PDFs
- **Python 3.8+**

## 🎯 Casos de Uso

1. **Evaluación de convocatorias**: Procesa y evalúa múltiples ensayos enviados en PDF
2. **Feedback automático**: Proporciona retroalimentación detallada a estudiantes
3. **Pre-selección**: Filtra ensayos por puntuación antes de revisión humana
4. **Limpieza de documentos**: Procesa PDFs académicos para análisis posterior
5. **Análisis comparativo**: Genera estadísticas de múltiples ensayos

## 📝 Notas Importantes

- El agente está optimizado para ensayos en español
- Cada evaluación toma aproximadamente 1-2 minutos dependiendo del largo
- **Evaluación**: Se recomienda GPT-4 o GPT-4o para mejores resultados
- **Limpieza de PDF**: GPT-4o-mini es suficiente y más económico
- Los comentarios son constructivos y orientados a la mejora
- La limpieza de PDF mantiene TODO el contenido original, solo mejora el formato
- Usa structured output para garantizar calificaciones precisas (1-5)

## 🔐 Variables de Entorno Requeridas

```env
OPENAI_API_KEY=sk-...  # Tu clave API de OpenAI
```

## 📄 Licencia

Este proyecto es de código abierto.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.
