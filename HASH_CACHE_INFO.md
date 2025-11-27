# 🚀 Hash Cache - Sistema de Deduplicación Inteligente

## ¿Qué es el Hash Cache?

El **Hash Cache** es un sistema de optimización que evita evaluaciones duplicadas utilizando hashes criptográficos del contenido del ensayo.

## 🎯 Beneficios

### Ahorro de Costos
- ✅ **0 llamadas a OpenAI** para ensayos duplicados
- ✅ **0 costo de API** en re-evaluaciones
- ✅ **Ahorro estimado: hasta 90%** en escenarios con múltiples submissions

### Velocidad
- ⚡ **Respuesta instantánea** (<100ms vs ~10-30 segundos con IA)
- ⚡ **100x más rápido** que una evaluación completa
- ⚡ Sin latencia de red con OpenAI

### Consistencia
- 🎯 **Misma evaluación garantizada** para el mismo contenido
- 🎯 **Resultados reproducibles** en cualquier momento
- 🎯 **Integridad de datos** mediante SHA-256

## 🔧 Implementación Técnica

### Algoritmo de Hash
```python
import hashlib

# Se usa SHA-256 (seguro y rápido)
texto_hash = hashlib.sha256(texto.encode('utf-8')).hexdigest()
# Resultado: string hexadecimal de 64 caracteres
# Ejemplo: "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
```

### Flujo de Evaluación

```
1. Usuario sube PDF
   ↓
2. Extraer texto del PDF
   ↓
3. Calcular SHA-256 del texto
   ↓
4. Buscar en BD: ¿Existe este hash?
   ↓
   ├── SÍ → ⚡ CACHE HIT
   │         └── Devolver evaluación existente (instantáneo)
   │
   └── NO → 🔄 CACHE MISS
             └── Evaluar con OpenAI
             └── Guardar con hash en BD
```

## 📊 Estadísticas de Uso

### Indicadores en la Interfaz
- **Cache Hit**: Mensaje verde "✨ Evaluación recuperada del caché"
- **Cache Miss**: Evaluación normal (sin mensaje especial)

### Logs del Servidor
```
⚡ CACHE HIT: Ensayo duplicado encontrado (ID: 123)
   Hash: 9f86d081884c7d65...
   Archivo original: Ensayo_Juan_Perez.pdf

🔄 CACHE MISS: Evaluando nuevo ensayo con OpenAI
   Hash: a3c2f5b8e9d1c4a7...
```

## 🔐 Seguridad y Colisiones

### SHA-256
- **Probabilidad de colisión**: ~2^-256 (prácticamente imposible)
- **Más seguro que**: MD5, SHA-1
- **Velocidad**: ~100MB/s (suficientemente rápido)

### ¿Qué pasa si cambia una letra?
```python
texto1 = "Este es un ensayo"
texto2 = "Este es un Ensayo"  # Mayúscula en "Ensayo"

hash1 = sha256(texto1)  # → "abc123..."
hash2 = sha256(texto2)  # → "xyz789..." (completamente diferente)
```

**Resultado**: Hashes totalmente distintos → Se evalúa como nuevo ensayo ✅

## 📈 Casos de Uso Reales

### Escenario 1: Estudiante resubmite por error
```
Intento 1: Sube "Ensayo_Final.pdf" → Evaluación con IA (10s, $0.02)
Intento 2: Sube "Ensayo_Final.pdf" de nuevo → ⚡ Cache (0.1s, $0.00)

Ahorro: $0.02 + 9.9 segundos
```

### Escenario 2: Múltiples profesores revisan
```
Profesor A: Carga ensayo para revisión → Evaluación (10s, $0.02)
Profesor B: Carga mismo ensayo 2 días después → ⚡ Cache (0.1s, $0.00)
Profesor C: Carga mismo ensayo 1 semana después → ⚡ Cache (0.1s, $0.00)

Ahorro total: $0.04 + 19.8 segundos
```

### Escenario 3: Migración de datos
```
Script carga 100 ensayos procesados previamente:
- 27 ya existían en BD → ⚡ 27 cache hits (instantáneo)
- 73 nuevos → 73 evaluaciones con IA

Ahorro: 27 × $0.02 = $0.54 + ~270 segundos (4.5 minutos)
```

## 🛠️ Código en Producción

### Backend (web/app.py)
```python
@app.route('/evaluate', methods=['POST'])
@require_auth
def evaluate():
    # ... procesar PDF ...
    texto = pdf_processor.procesar_pdf(str(filepath))
    
    # 🚀 HASH CACHE
    texto_hash = hashlib.sha256(texto.encode('utf-8')).hexdigest()
    ensayo_existente = Ensayo.query.filter_by(texto_hash=texto_hash).first()
    
    if ensayo_existente:
        print(f"⚡ CACHE HIT: ID {ensayo_existente.id}")
        return jsonify({
            **ensayo_existente.to_dict(),
            'cache_hit': True,
            'mensaje_cache': '✨ Evaluación recuperada del caché'
        })
    
    # Cache miss → evaluar con IA
    evaluacion = evaluador.evaluar(texto)
    # ... guardar en BD ...
```

### Frontend (web/script.js)
```javascript
const result = await response.json();

if (result.cache_hit) {
    showNotification(result.mensaje_cache, 'success');
    console.log('⚡ CACHE HIT - Sin consumo de API');
}
```

### Modelo de Datos (database.py)
```python
class Ensayo(db.Model):
    texto_hash = db.Column(db.String(64), unique=True, index=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.texto_completo:
            # Calcular hash automáticamente
            self.texto_hash = hashlib.sha256(
                self.texto_completo.encode('utf-8')
            ).hexdigest()
```

## 📝 Mantenimiento

### Índice de Base de Datos
```sql
-- El índice en texto_hash hace las búsquedas O(1)
CREATE INDEX idx_texto_hash ON ensayos(texto_hash);
```

### Limpieza de Cache (si es necesario)
```python
# Si quieres forzar re-evaluación de un ensayo:
ensayo = Ensayo.query.filter_by(id=123).first()
ensayo.texto_hash = None  # Forzará nueva evaluación
db.session.commit()
```

## 🎓 Comparación con Otras Soluciones

| Solución | Velocidad | Costo | Complejidad | Persistencia |
|----------|-----------|-------|-------------|--------------|
| **Hash Cache (SQLite)** | ⚡⚡⚡ Instantáneo | $0.00 | Baja | ✅ Permanente |
| Redis Cache | ⚡⚡ Muy rápido | $5-50/mes | Media | ⚠️ Volátil |
| Memcached | ⚡⚡ Muy rápido | Variable | Media | ❌ Volátil |
| Sin cache | 🐌 10-30s | $0.01-0.05 | Baja | N/A |

## ✅ Conclusión

El Hash Cache con SQLite es la solución óptima para este proyecto porque:

1. **No requiere infraestructura adicional** (Redis, Memcached)
2. **Persistencia garantizada** (no se pierde al reiniciar)
3. **Cero configuración** (funciona out-of-the-box)
4. **Ahorro significativo** en costos de API
5. **Mejora la UX** con respuestas instantáneas

---

**Implementado**: Noviembre 2025  
**Versión**: 1.0  
**Mantenedor**: Sistema de Evaluación de Ensayos
