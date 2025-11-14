# Registro de Cambios

## [Nueva Funcionalidad] - Base de Datos y Comparación de Ensayos

### ✨ Características Nuevas

#### 1. Base de Datos SQLite
- **Archivo**: `database.py`
- Los ensayos evaluados ahora se guardan automáticamente en una base de datos SQLite
- Almacena texto completo, evaluaciones y metadatos de cada ensayo
- Base de datos ubicada en: `web/essays.db`

#### 2. Historial de Ensayos
- **Botón**: "Ver Historial" en la interfaz de resultados
- Muestra todos los ensayos evaluados con:
  - Nombre del archivo
  - Fecha de evaluación
  - Puntuación total
  - Vista previa del texto
- Permite seleccionar múltiples ensayos mediante checkboxes

#### 3. Comparación de Ensayos
- **Requisito**: Seleccionar al menos 2 ensayos del historial
- **Botón**: "Comparar Seleccionados"
- La IA genera un análisis comparativo completo que incluye:
  - Resumen ejecutivo
  - Análisis comparativo por criterio
  - Fortalezas y debilidades de cada ensayo
  - Ranking justificado
  - Recomendaciones específicas
  - Conclusión con el ensayo ganador

### 🔧 Cambios Técnicos

#### Backend (`web/app.py`)
- Nuevos endpoints:
  - `GET /essays` - Listar todos los ensayos
  - `GET /essays/<id>` - Obtener un ensayo específico
  - `POST /compare` - Comparar múltiples ensayos
- Integración con base de datos SQLite
- Guardar automáticamente ensayos evaluados

#### Frontend
- `index.html`: Nuevas secciones para historial y comparación
- `styles.css`: Estilos para las nuevas interfaces
- `script.js`: Funciones para gestionar historial y comparaciones

#### Dependencias
- `flask-sqlalchemy>=3.1.1` - ORM para base de datos
- `werkzeug>=3.0.0` - Utilidades web

### 📖 Cómo Usar

1. **Evaluar Ensayos Normalmente**
   - Sube y evalúa ensayos como siempre
   - Ahora se guardan automáticamente en la base de datos

2. **Ver Historial**
   - Después de evaluar un ensayo, haz clic en "Ver Historial"
   - Verás todos los ensayos evaluados anteriormente

3. **Comparar Ensayos**
   - En el historial, selecciona 2 o más ensayos usando los checkboxes
   - Haz clic en "Comparar Seleccionados"
   - Espera mientras la IA genera el análisis comparativo
   - Revisa el análisis detallado con recomendaciones

### 🎯 Casos de Uso

- **Jurados de Concursos**: Comparar ensayos finalistas para determinar ganadores
- **Evaluación Académica**: Analizar diferencias entre trabajos de estudiantes
- **Análisis de Calidad**: Identificar patrones en ensayos exitosos vs. menos exitosos
- **Mejora Continua**: Usar comparaciones para entender qué hace destacar a un ensayo

### 🔍 Notas Técnicas

- La base de datos se crea automáticamente al iniciar el servidor
- Los ensayos se almacenan con texto completo y evaluaciones detalladas
- Las comparaciones usan GPT-4 para análisis profundos y contextuales
- La interfaz permite selección múltiple ilimitada de ensayos
