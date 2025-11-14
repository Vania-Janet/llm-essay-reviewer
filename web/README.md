# Interfaz Web - Evaluador de Ensayos

## Descripción

Interfaz web profesional para el sistema de evaluación de ensayos con IA. Permite a los usuarios cargar archivos PDF mediante drag & drop o selección de archivos, y visualizar los resultados de la evaluación de manera clara y profesional.

## Características

- **Diseño profesional y formal** con los colores especificados:
  - Amarillo: RGB(221, 218, 54)
  - Azul: RGB(41, 52, 109)
  - Gradiente lineal entre ambos colores

- **Funcionalidades:**
  - Carga de archivos PDF por arrastrar y soltar (drag & drop)
  - Selección de archivos mediante botón
  - Indicador visual de procesamiento
  - Visualización detallada de resultados por criterio
  - Puntuación total con barra de progreso animada
  - Logo en la esquina superior izquierda
  - Diseño responsivo para dispositivos móviles

## Estructura de Archivos

```
web/
├── index.html      # Página principal
├── styles.css      # Estilos CSS
├── script.js       # Lógica JavaScript del cliente
├── app.py          # Servidor Flask
├── image.png       # Logo de la aplicación
└── README.md       # Este archivo
```

## Instalación

1. Instalar dependencias adicionales:

```bash
pip install flask
```

2. Asegurarse de que las dependencias del proyecto principal estén instaladas:

```bash
pip install -r ../requirements.txt
```

## Uso

1. Iniciar el servidor web:

```bash
cd web
python app.py
```

2. Abrir en el navegador:

```
http://localhost:5000
```

3. Cargar un archivo PDF:
   - Arrastra un archivo PDF al área designada, o
   - Haz clic en "Seleccionar Archivo" y elige un PDF

4. Hacer clic en "Evaluar Ensayo" y esperar los resultados

## Tecnologías Utilizadas

- **Frontend:**
  - HTML5
  - CSS3 (Flexbox, Grid, Animaciones)
  - JavaScript (Vanilla JS)

- **Backend:**
  - Flask (Python web framework)
  - Sistema de evaluación existente (LangChain + OpenAI)

## API Endpoints

### POST /evaluate

Evalúa un ensayo en formato PDF.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: archivo PDF con key "file"

**Response:**
```json
{
  "puntuacion_total": 4.25,
  "calidad_tecnica": {
    "calificacion": 4,
    "comentario": "..."
  },
  "creatividad": {
    "calificacion": 5,
    "comentario": "..."
  },
  "vinculacion_tematica": {
    "calificacion": 4,
    "comentario": "..."
  },
  "bienestar_colectivo": {
    "calificacion": 4,
    "comentario": "..."
  },
  "potencial_impacto": {
    "calificacion": 5,
    "comentario": "..."
  },
  "comentario_general": "..."
}
```

## Personalización

### Cambiar Colores

Edita las variables CSS en `styles.css`:

```css
:root {
    --primary-yellow: rgb(221, 218, 54);
    --primary-blue: rgb(41, 52, 109);
    --gradient: linear-gradient(135deg, var(--primary-blue) 0%, var(--primary-yellow) 100%);
}
```

### Modificar el Puerto

En `app.py`, cambia el puerto en la última línea:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Notas de Desarrollo

- Los archivos se guardan temporalmente en `web/uploads/` y se eliminan después de procesarse
- Tamaño máximo de archivo: 16MB
- Formatos soportados: PDF únicamente
- El servidor está configurado en modo debug para desarrollo

## Seguridad

En producción, considerar:
- Desactivar el modo debug de Flask
- Implementar autenticación de usuarios
- Agregar rate limiting
- Validación adicional de archivos
- Usar HTTPS
- Configurar CORS apropiadamente

## Soporte

Para problemas o preguntas, consultar la documentación principal del proyecto o contactar al desarrollador.
