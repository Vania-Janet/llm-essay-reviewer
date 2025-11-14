# Guía de Usuario - Comparación de Ensayos

## 🎯 Nueva Funcionalidad: Comparación de Ensayos

Esta actualización agrega la capacidad de almacenar, listar y comparar múltiples ensayos evaluados.

---

## 📚 Funcionalidades Principales

### 1. Almacenamiento Automático

Cada ensayo evaluado se guarda automáticamente en una base de datos local, incluyendo:
- ✅ Texto completo del ensayo
- ✅ Todas las evaluaciones y calificaciones
- ✅ Comentarios por criterio
- ✅ Fecha y hora de evaluación
- ✅ Nombre del archivo original

### 2. Historial de Ensayos

**Cómo acceder:**
1. Evalúa al menos un ensayo
2. En los resultados, haz clic en el botón **"Ver Historial"** 📋
3. Verás una lista de todos los ensayos evaluados

**Información mostrada:**
- Nombre del archivo
- Fecha de evaluación
- Puntuación total
- Vista previa del contenido

### 3. Comparación Múltiple

**Requisitos:**
- Mínimo 2 ensayos en el historial
- Máximo: sin límite

**Pasos para comparar:**

1. **Abre el historial** 
   - Haz clic en "Ver Historial" desde los resultados

2. **Selecciona ensayos**
   - Marca los checkboxes de los ensayos que quieres comparar
   - Mínimo 2 ensayos requeridos
   - El botón "Comparar Seleccionados" se activará

3. **Genera la comparación**
   - Haz clic en "Comparar Seleccionados"
   - Espera mientras la IA analiza (puede tomar 10-30 segundos)

4. **Revisa el análisis**
   - La IA generará un informe completo con:
     - 📊 Resumen ejecutivo
     - ⚖️ Análisis comparativo por criterio
     - 💪 Fortalezas y debilidades
     - 🏆 Ranking justificado
     - 💡 Recomendaciones específicas
     - 🎖️ Conclusión con el ganador

---

## 🎨 Interfaz de Usuario

### Botones Nuevos

**En la página de resultados:**
- 🕐 **Ver Historial**: Abre el historial de ensayos evaluados

**En la página de historial:**
- ✅ **Comparar Seleccionados**: Compara los ensayos marcados
- ❌ **Cerrar**: Vuelve a la página principal

**En la página de comparación:**
- ❌ **Cerrar**: Vuelve al historial

---

## 💡 Casos de Uso

### Para Jurados de Concursos
```
1. Evalúa todos los ensayos participantes
2. Ve al historial
3. Selecciona los 3-5 finalistas
4. Compara para identificar al ganador
```

### Para Profesores
```
1. Evalúa los trabajos de todos los estudiantes
2. Selecciona ensayos con puntuaciones similares
3. Compara para entender diferencias sutiles
4. Usa el análisis para dar retroalimentación detallada
```

### Para Autoevaluación
```
1. Evalúa diferentes versiones de tu ensayo
2. Compara para ver mejoras
3. Identifica qué cambios funcionaron mejor
```

---

## 🔧 Detalles Técnicos

### Base de Datos
- **Ubicación**: `web/essays.db`
- **Tipo**: SQLite (local, sin servidor requerido)
- **Respaldo**: Copia el archivo `.db` para hacer backup

### Endpoints API

```python
GET /essays
# Lista todos los ensayos

GET /essays/<id>
# Obtiene un ensayo específico

POST /compare
# Body: { "essay_ids": [1, 2, 3] }
# Compara múltiples ensayos
```

---

## 🚨 Limitaciones Conocidas

1. **Tiempo de Comparación**: Puede tomar 10-30 segundos dependiendo del número de ensayos
2. **Número de Ensayos**: Comparar más de 5 ensayos puede resultar en respuestas muy largas
3. **Almacenamiento**: Cada ensayo ocupa ~10-50KB en la base de datos

---

## 🐛 Solución de Problemas

### El historial no muestra ensayos
- ✅ Asegúrate de haber evaluado al menos un ensayo
- ✅ Verifica que el archivo `essays.db` existe en la carpeta `web/`

### Error al comparar ensayos
- ✅ Verifica que tienes conexión a internet (necesaria para OpenAI)
- ✅ Asegúrate de seleccionar al menos 2 ensayos
- ✅ Revisa que la variable `OPENAI_API_KEY` esté configurada

### La base de datos no se crea
- ✅ Verifica que tienes permisos de escritura en la carpeta `web/`
- ✅ Reinstala dependencias: `pip install flask-sqlalchemy`

---

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:
1. Verifica la consola del servidor para errores
2. Revisa el archivo `CHANGELOG.md` para cambios recientes
3. Contacta al desarrollador con detalles específicos del error

---

## 🎉 ¡Disfruta la Nueva Funcionalidad!

La comparación de ensayos te permitirá tomar decisiones más informadas y justas en procesos de evaluación.
