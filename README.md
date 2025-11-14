# 🎓 Sistema de Evaluación Inteligente de Ensayos

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-green.svg)](https://langchain.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema de evaluación automática de ensayos académicos impulsado por inteligencia artificial, utilizando **LangGraph** y **LangChain** con modelos GPT-4 de OpenAI.

---

## ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🎯 **Evaluación Multi-Criterio** | 5 criterios académicos rigurosos con ponderaciones personalizables |
| 📄 **Procesamiento Inteligente de PDFs** | Extracción y limpieza automática de documentos |
| 🤖 **IA Avanzada** | Powered by GPT-4 con structured outputs para precisión |
| 📊 **Reportes Profesionales** | Generación de reportes HTML visualmente atractivos |
| 🔄 **Procesamiento por Lotes** | Evaluación masiva de múltiples ensayos |
| 🌐 **Interfaz Web** | Aplicación web profesional con drag & drop |

---

## 📋 Criterios de Evaluación

El sistema evalúa ensayos académicos mediante **5 criterios fundamentales**, cada uno con análisis detallado y comentarios constructivos:

| Criterio | Peso | Descripción |
|----------|------|-------------|
| 📝 **Calidad Técnica y Rigor Académico** | 20% | Estructura, coherencia, argumentación sólida y respaldo bibliográfico |
| 🎨 **Creatividad y Originalidad** | 20% | Innovación en ideas, perspectivas únicas y pensamiento crítico |
| 🎯 **Vinculación con Ejes Temáticos** | 20% | Integración de tecnología, sostenibilidad e inclusión |
| 🌍 **Bienestar Colectivo y Responsabilidad Social** | 20% | Impacto social, consideraciones éticas y sostenibilidad |
| ✨ **Potencial de Impacto y Publicación** | 20% | Claridad comunicativa, relevancia y capacidad de inspirar |

**Sistema de Calificación:** Escala de 1 a 5 con retroalimentación detallada por criterio.

---

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

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8 o superior
- Cuenta de OpenAI con API key activa
- pip (gestor de paquetes de Python)

### Pasos de Instalación

#### 1. Clonar el Repositorio

```bash
git clone https://github.com/Vania-Janet/llm-essay-reviewer.git
cd llm-essay-reviewer
```

#### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `langchain`, `langgraph`, `langchain-openai` - Framework de IA
- `pypdf`, `pdfplumber` - Procesamiento de documentos PDF
- `flask` - Servidor web (para interfaz web)
- `pydantic`, `python-dotenv` - Utilidades y validación

#### 3. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
OPENAI_API_KEY=sk-tu_clave_aqui
```

> 🔑 **Obtén tu API Key:** [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

#### 4. Verificar Instalación

```bash
python test_pdf_processor.py
```

---

## 💻 Guía de Uso

### 🌐 Opción 1: Interfaz Web (Recomendado)

La forma más sencilla de usar el sistema:

```bash
cd web
python app.py
```

Luego abre en tu navegador: **http://localhost:5001**

**Características de la interfaz web:**
- ✅ Drag & drop de archivos PDF
- ✅ Procesamiento en tiempo real
- ✅ Visualización profesional de resultados
- ✅ Diseño responsivo y moderno

---

### 📄 Opción 2: Evaluar PDFs desde Línea de Comandos

```bash
python evaluar_pdfs.py
```

**Proceso automatizado:**
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

---

### 📝 Opción 3: Evaluar Archivos de Texto

```bash
python main.py
```

---

### 🔄 Opción 4: Evaluación Masiva (Batch Processing)

```bash
python evaluar_batch.py
```

Procesa múltiples ensayos simultáneamente desde un directorio.

---

### 🧹 Opción 5: Procesamiento de PDFs (Solo Limpieza)

```bash
python pdf_processor.py
```

Extrae y limpia texto de PDFs sin evaluación.

---

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

---

## 🛠️ Stack Tecnológico

| Tecnología | Propósito | Versión |
|------------|-----------|---------|
| **LangChain** | Framework para aplicaciones LLM | Latest |
| **LangGraph** | Orquestación de flujos con grafos | Latest |
| **OpenAI GPT-4** | Modelo de lenguaje avanzado | GPT-4 / GPT-4o |
| **Flask** | Servidor web backend | Latest |
| **Pydantic** | Validación y modelos de datos | 2.0+ |
| **pypdf / pdfplumber** | Procesamiento de documentos PDF | Latest |
| **Python** | Lenguaje de programación | 3.8+ |

---

---

## 🎯 Casos de Uso

### Instituciones Educativas
- ✅ Evaluación automática de admisiones
- ✅ Retroalimentación instantánea para estudiantes
- ✅ Pre-selección de trabajos académicos

### Convocatorias y Concursos
- ✅ Procesamiento masivo de ensayos
- ✅ Evaluación objetiva y estandarizada
- ✅ Generación de reportes comparativos

### Investigación y Análisis
- ✅ Limpieza y estructuración de documentos académicos
- ✅ Análisis de contenido textual
- ✅ Extracción de insights de múltiples ensayos

---

---

## ⚙️ Configuración y Optimización

### Modelos Recomendados

| Tarea | Modelo | Razón |
|-------|--------|-------|
| **Evaluación de Ensayos** | GPT-4 / GPT-4o | Mayor precisión y análisis profundo |
| **Limpieza de PDFs** | GPT-4o-mini | Costo-efectivo, suficiente para limpieza |

### Notas Importantes

- ✅ Sistema optimizado para ensayos en **español**
- ⏱️ Tiempo de evaluación: **1-2 minutos** por ensayo
- 🎯 **Structured outputs** garantizan calificaciones precisas (1-5)
- 💬 Comentarios constructivos orientados a la mejora
- 📄 La limpieza de PDFs mantiene **100% del contenido original**

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas y apreciadas. Para contribuir:

1. 🍴 Fork del repositorio
2. 🔨 Crea una rama para tu feature (`git checkout -b feature/NuevaFuncionalidad`)
3. 💾 Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. 📤 Push a la rama (`git push origin feature/NuevaFuncionalidad`)
5. 🎯 Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 📧 Soporte y Contacto

- 🐛 **Reportar bugs:** [Abrir un issue](https://github.com/Vania-Janet/llm-essay-reviewer/issues)
- 💡 **Sugerencias:** [Iniciar una discusión](https://github.com/Vania-Janet/llm-essay-reviewer/discussions)
- 📧 **Email:** [Contacto directo](mailto:tu-email@ejemplo.com)

---

## 🌟 Agradecimientos

Desarrollado con ❤️ utilizando tecnologías de vanguardia en IA y procesamiento de lenguaje natural.

**Powered by:**
- [LangChain](https://langchain.com/)
- [OpenAI](https://openai.com/)
- [Python](https://python.org/)

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella ⭐**

</div>
