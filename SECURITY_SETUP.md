# Configuración de Seguridad para Producción

## 🔒 Variables de Entorno Requeridas

### CRÍTICO: SECRET_KEY y JWT_SECRET_KEY

Estas claves **DEBEN** estar configuradas en producción. Si no están presentes o cambian frecuentemente, causarán que:
- ❌ Todos los usuarios pierdan sus sesiones al reiniciar el servidor
- ❌ Los tokens JWT se invaliden
- ❌ Los usuarios sean desconectados forzosamente

## 📝 Paso a Paso para Configuración

### 1. Generar Claves Seguras

Ejecuta el script de configuración automática:

```bash
python setup_security.py
```

Este script:
- ✅ Genera claves aleatorias criptográficamente seguras
- ✅ Crea o actualiza el archivo `.env`
- ✅ Verifica que las claves estén presentes

**O genera manualmente** con Python:

```python
import secrets

# Generar FLASK_SECRET_KEY
flask_secret = secrets.token_hex(32)
print(f"FLASK_SECRET_KEY={flask_secret}")

# Generar JWT_SECRET_KEY
jwt_secret = secrets.token_hex(32)
print(f"JWT_SECRET_KEY={jwt_secret}")
```

### 2. Configurar Variables de Entorno

#### Opción A: Archivo .env (Desarrollo/Testing)

Crea o edita `.env` en la raíz del proyecto:

```bash
# Flask Configuration
FLASK_SECRET_KEY=tu_clave_secreta_generada_aqui_64_caracteres_hex
FLASK_ENV=production

# JWT Authentication
JWT_SECRET_KEY=tu_jwt_secret_generada_aqui_64_caracteres_hex
JWT_ACCESS_TOKEN_EXPIRES=3600

# OpenAI
OPENAI_API_KEY=tu_api_key_de_openai
OPENAI_MODEL=gpt-4o
```

#### Opción B: Variables de Entorno del Sistema (Producción)

**Linux/macOS:**
```bash
export FLASK_SECRET_KEY="tu_clave_secreta_64_caracteres"
export JWT_SECRET_KEY="tu_jwt_secret_64_caracteres"
export FLASK_ENV="production"
```

**Windows (PowerShell):**
```powershell
$env:FLASK_SECRET_KEY="tu_clave_secreta_64_caracteres"
$env:JWT_SECRET_KEY="tu_jwt_secret_64_caracteres"
$env:FLASK_ENV="production"
```

#### Opción C: Servicios en la Nube

**Heroku:**
```bash
heroku config:set FLASK_SECRET_KEY="tu_clave_secreta"
heroku config:set JWT_SECRET_KEY="tu_jwt_secret"
heroku config:set FLASK_ENV="production"
```

**AWS Elastic Beanstalk:**
```bash
eb setenv FLASK_SECRET_KEY="tu_clave_secreta" \
         JWT_SECRET_KEY="tu_jwt_secret" \
         FLASK_ENV="production"
```

**Azure:**
```bash
az webapp config appsettings set \
  --name tu-app \
  --resource-group tu-grupo \
  --settings FLASK_SECRET_KEY="tu_clave" JWT_SECRET_KEY="tu_jwt"
```

**Docker:**
```yaml
# docker-compose.yml
services:
  web:
    environment:
      - FLASK_SECRET_KEY=tu_clave_secreta
      - JWT_SECRET_KEY=tu_jwt_secret
      - FLASK_ENV=production
```

### 3. Verificar Configuración

Ejecuta el script de verificación:

```bash
python verify_security.py
```

Este script verifica:
- ✅ Presencia de `.env`
- ✅ Variables SECRET_KEY configuradas
- ✅ Longitud adecuada de las claves (mínimo 32 caracteres)
- ✅ Configuración de Flask (modo producción)

### 4. Proteger el Archivo .env

**IMPORTANTE:** El archivo `.env` contiene secretos y **NUNCA** debe ser versionado en Git.

Verifica que `.gitignore` incluya:
```
.env
.env.local
.env.production
*.env
```

## ⚠️ Comportamiento por Entorno

### Desarrollo (FLASK_ENV != production)
- Si no hay `FLASK_SECRET_KEY`, usa una clave fija de desarrollo
- ⚠️ Muestra advertencia en consola
- Permite desarrollo sin configuración compleja

### Producción (FLASK_ENV = production)
- **REQUIERE** `FLASK_SECRET_KEY` obligatoriamente
- Si no está presente, el servidor **NO ARRANCARÁ**
- Falla con error claro: `ValueError: FLASK_SECRET_KEY es requerida en producción`

## 🔍 Solución de Problemas

### Error: "FLASK_SECRET_KEY es requerida en producción"
```
ValueError: FLASK_SECRET_KEY es requerida en producción.
Configura la variable de entorno FLASK_SECRET_KEY.
```

**Solución:**
1. Genera una clave: `python setup_security.py`
2. Configura la variable de entorno
3. Reinicia el servidor

### Los usuarios son desconectados al reiniciar
**Causa:** La `SECRET_KEY` está cambiando en cada reinicio.

**Solución:**
1. Verifica que `FLASK_SECRET_KEY` esté en variables de entorno
2. Asegúrate que la clave sea **permanente** y no se regenere
3. NO uses `os.urandom()` en producción

### Token JWT inválido después de despliegue
**Causa:** `JWT_SECRET_KEY` cambió.

**Solución:**
1. Configura `JWT_SECRET_KEY` fija en variables de entorno
2. Mantén la misma clave entre despliegues
3. Si cambias la clave, todos los usuarios deberán volver a iniciar sesión

## 📋 Checklist de Producción

Antes de desplegar a producción:

- [ ] `FLASK_SECRET_KEY` está configurada (64+ caracteres)
- [ ] `JWT_SECRET_KEY` está configurada (64+ caracteres)
- [ ] `FLASK_ENV=production` está configurado
- [ ] Archivo `.env` está en `.gitignore`
- [ ] Las claves son únicas y aleatorias (no usar ejemplos)
- [ ] `python verify_security.py` pasa sin errores
- [ ] Variables están en el servicio de hosting (no solo en .env)
- [ ] Backup de las claves en lugar seguro (gestor de contraseñas)

## 🔐 Mejores Prácticas

1. **Usa un gestor de secretos en producción:**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Google Cloud Secret Manager

2. **Nunca hardcodees secretos en el código**

3. **Rota las claves periódicamente** (cada 90-180 días)
   - Nota: Rotar claves invalidará todas las sesiones activas

4. **Documenta dónde están las claves:**
   - En equipo, usa gestor compartido (1Password, LastPass Teams)
   - Mantén backup cifrado

5. **Monitorea intentos de acceso no autorizado**

## 📚 Referencias

- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
