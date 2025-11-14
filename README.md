# Agente Evaluador de Ensayos 🎓

Sistema de evaluación automática de ensayos usando **LangGraph** y **LangChain** con GPT-4.

## 📋 Descripción

Este agente evalúa ensayos académicos según 6 criterios específicos con ponderaciones establecidas:

1. **Calidad técnica y rigor académico (20%)** - Estructura, coherencia y solidez argumentativa
2. **Creatividad y originalidad (20%)** - Ideas nuevas y enfoques innovadores
3. **Vinculación con ejes temáticos (15%)** - Tecnología, sostenibilidad, inclusión
4. **Bienestar colectivo y responsabilidad social (20%)** - Impactos sociales, éticos y ambientales
5. **Uso responsable de IA (15%)** - Transparencia y ética en el uso de herramientas de IA
6. **Potencial de impacto y publicación (10%)** - Capacidad de comunicar e inspirar

Cada criterio se evalúa en una escala del 1 al 5 con comentarios detallados.

## 🏗️ Arquitectura

El sistema utiliza **LangGraph** para crear un grafo de evaluación secuencial:

```
Inicio → Calidad Técnica → Creatividad → Vinculación → Bienestar → Uso IA → Impacto → Comentario General → Fin
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
├── main.py                # Script principal
└── README.md              # Este archivo
```

## 🚀 Instalación

1. **Clonar o descargar el proyecto**

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:
Crea o edita el archivo `.env`:
```env
OPENAI_API_KEY=tu_clave_de_openai_aqui
```

## 💻 Uso

### Ejecución básica:

```bash
python main.py
```

### Uso programático:

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

## 📊 Resultados

El sistema genera:

1. **Reporte en consola**: Evaluación completa con todas las calificaciones y comentarios
2. **Reporte HTML**: Documento visualmente atractivo con toda la evaluación (opcional)
3. **Objeto Python**: `EvaluacionEnsayo` con todos los datos estructurados

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
evaluador = EvaluadorEnsayos(
    model_name="gpt-4o-mini",  # o "gpt-3.5-turbo"
    temperature=0.5
)
```

### Modificar prompts:

Edita `prompts.py` para ajustar los criterios de evaluación o el tono de los comentarios.

### Ajustar ponderaciones:

Modifica el método `calcular_puntuacion_total()` en `models.py`.

## 🛠️ Tecnologías

- **LangChain**: Framework para aplicaciones con LLMs
- **LangGraph**: Orquestación de flujos complejos con grafos
- **OpenAI GPT-4**: Modelo de lenguaje para evaluación
- **Pydantic**: Validación de datos y modelos
- **Python 3.8+**

## 📝 Notas

- El agente está optimizado para ensayos en español
- Cada evaluación toma aproximadamente 1-2 minutos dependiendo del largo del ensayo
- Se recomienda GPT-4 para mejores resultados, aunque GPT-3.5 también funciona
- Los comentarios son constructivos y orientados a la mejora

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
