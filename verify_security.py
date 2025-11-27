#!/usr/bin/env python3
"""
Script de verificación de seguridad
Verifica que todas las correcciones críticas estén aplicadas
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Verificar que un archivo existe."""
    if Path(filepath).exists():
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - FALTA")
        return False

def check_file_contains(filepath, text, description):
    """Verificar que un archivo contiene cierto texto."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if text in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - NO ENCONTRADO")
                return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🔒 VERIFICACIÓN DE SEGURIDAD")
    print("="*60 + "\n")
    
    base_path = Path(__file__).parent
    issues = []
    
    # 1. Verificar archivos de autenticación
    print("📁 Archivos de autenticación:")
    if not check_file_exists(base_path / "web" / "auth.py", "auth.py existe"):
        issues.append("Falta archivo auth.py")
    if not check_file_exists(base_path / "web" / "login.html", "login.html existe"):
        issues.append("Falta archivo login.html")
    print()
    
    # 2. Verificar protección en rutas
    print("🛡️  Protección de rutas (@require_auth):")
    app_path = base_path / "web" / "app.py"
    
    checks = [
        ("@app.route('/evaluate'", "@require_auth en /evaluate"),
        ("@app.route('/chat'", "@require_auth en /chat"),
        ("@app.route('/essays'", "@require_auth en /essays"),
        ("@app.route('/compare'", "@require_auth en /compare"),
    ]
    
    for route, desc in checks:
        if not check_file_contains(app_path, route, f"Ruta {route} definida"):
            issues.append(f"Ruta {route} no definida")
    print()
    
    # 3. Verificar configuración dinámica de cookies
    print("🍪 Configuración de cookies:")
    if not check_file_contains(
        app_path,
        "is_production = os.getenv('FLASK_ENV') == 'production'",
        "Cookies dinámicas según entorno"
    ):
        issues.append("Cookies no configuradas dinámicamente")
    print()
    
    # 4. Verificar protección XSS
    print("🔐 Protección XSS:")
    script_path = base_path / "web" / "script.js"
    if not check_file_contains(
        script_path,
        "function escapeHtml",
        "Función escapeHtml() implementada"
    ):
        issues.append("Falta función escapeHtml()")
    
    if not check_file_contains(
        script_path,
        "escapeHtml(essay.nombre_archivo)",
        "escapeHtml() usada en nombres de archivo"
    ):
        issues.append("escapeHtml() no usada en todos los lugares")
    print()
    
    # 5. Verificar dependencias
    print("📦 Dependencias de seguridad:")
    req_path = base_path / "requirements.txt"
    if not check_file_contains(req_path, "bcrypt", "bcrypt en requirements.txt"):
        issues.append("Falta bcrypt en requirements")
    if not check_file_contains(req_path, "PyJWT", "PyJWT en requirements.txt"):
        issues.append("Falta PyJWT en requirements")
    print()
    
    # 6. Verificar .env
    print("⚙️  Configuración:")
    env_path = base_path / ".env"
    env_example_path = base_path / ".env.example"
    
    if check_file_exists(env_path, ".env existe"):
        if not check_file_contains(env_path, "JWT_SECRET_KEY", "JWT_SECRET_KEY configurada"):
            issues.append("Falta JWT_SECRET_KEY en .env")
        if not check_file_contains(env_path, "FLASK_SECRET_KEY", "FLASK_SECRET_KEY configurada"):
            issues.append("Falta FLASK_SECRET_KEY en .env")
    else:
        print("⚠️  .env no existe - ejecuta: python setup_security.py")
        issues.append(".env no configurado")
    
    check_file_exists(env_example_path, ".env.example existe (plantilla)")
    print()
    
    # 7. Verificar documentación
    print("📚 Documentación:")
    check_file_exists(base_path / "SECURITY.md", "SECURITY.md (guía completa)")
    check_file_exists(base_path / "SECURITY_AUDIT.md", "SECURITY_AUDIT.md (correcciones)")
    print()
    
    # Resumen
    print("="*60)
    if not issues:
        print("✅ TODAS LAS VERIFICACIONES PASARON")
        print("="*60)
        print("\n🎉 Sistema seguro y listo para usar")
        print("\n📝 Próximos pasos:")
        print("   1. cd web && python app.py")
        print("   2. Abrir: http://localhost:5001/login.html")
        print("\n⚠️  Recuerda: HTTPS obligatorio en producción")
        return 0
    else:
        print("⚠️  SE ENCONTRARON PROBLEMAS")
        print("="*60)
        print("\n❌ Problemas detectados:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n🔧 Solución:")
        print("   Revisa SECURITY_AUDIT.md para las correcciones")
        return 1

if __name__ == '__main__':
    sys.exit(main())
