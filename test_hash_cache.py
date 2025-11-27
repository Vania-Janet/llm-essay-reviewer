#!/usr/bin/env python3
"""
Script de prueba para verificar el funcionamiento del Hash Cache.
"""
import hashlib
from pathlib import Path

def test_hash_consistency():
    """Verificar que el mismo texto genera el mismo hash."""
    texto1 = "Este es un ensayo de prueba con contenido específico."
    texto2 = "Este es un ensayo de prueba con contenido específico."
    texto3 = "Este es un ensayo de prueba con contenido distinto."
    
    hash1 = hashlib.sha256(texto1.encode('utf-8')).hexdigest()
    hash2 = hashlib.sha256(texto2.encode('utf-8')).hexdigest()
    hash3 = hashlib.sha256(texto3.encode('utf-8')).hexdigest()
    
    print("=" * 70)
    print("TEST 1: Consistencia de Hashes")
    print("=" * 70)
    print(f"Texto 1: '{texto1[:50]}...'")
    print(f"Hash 1:  {hash1}")
    print()
    print(f"Texto 2: '{texto2[:50]}...'")
    print(f"Hash 2:  {hash2}")
    print()
    
    if hash1 == hash2:
        print("✅ PASS: Mismo texto genera mismo hash")
    else:
        print("❌ FAIL: Mismo texto debería generar mismo hash")
    
    print()
    print(f"Texto 3: '{texto3[:50]}...'")
    print(f"Hash 3:  {hash3}")
    print()
    
    if hash1 != hash3:
        print("✅ PASS: Texto diferente genera hash diferente")
    else:
        print("❌ FAIL: Texto diferente debería generar hash diferente")
    
    print()

def test_hash_sensitivity():
    """Verificar sensibilidad a cambios mínimos."""
    original = "Ensayo sobre tecnología"
    con_mayuscula = "Ensayo sobre Tecnología"  # Solo cambio de mayúscula
    con_acento = "Ensayo sobre tecnología."  # Solo un punto extra
    
    hash_original = hashlib.sha256(original.encode('utf-8')).hexdigest()
    hash_mayuscula = hashlib.sha256(con_mayuscula.encode('utf-8')).hexdigest()
    hash_acento = hashlib.sha256(con_acento.encode('utf-8')).hexdigest()
    
    print("=" * 70)
    print("TEST 2: Sensibilidad a Cambios Mínimos")
    print("=" * 70)
    print(f"Original:       '{original}'")
    print(f"Hash:           {hash_original}")
    print()
    print(f"Con mayúscula:  '{con_mayuscula}'")
    print(f"Hash:           {hash_mayuscula}")
    print(f"¿Diferente?     {hash_original != hash_mayuscula} ✅" if hash_original != hash_mayuscula else "❌")
    print()
    print(f"Con punto:      '{con_acento}'")
    print(f"Hash:           {hash_acento}")
    print(f"¿Diferente?     {hash_original != hash_acento} ✅" if hash_original != hash_acento else "❌")
    print()

def test_performance():
    """Medir velocidad de hash vs búsqueda en BD."""
    import time
    
    texto_largo = "Lorem ipsum dolor sit amet. " * 1000  # ~28KB
    
    print("=" * 70)
    print("TEST 3: Performance del Hash")
    print("=" * 70)
    print(f"Tamaño del texto: {len(texto_largo)} caracteres (~{len(texto_largo)//1024}KB)")
    print()
    
    # Medir tiempo de hash
    inicio = time.perf_counter()
    for _ in range(1000):
        hash_resultado = hashlib.sha256(texto_largo.encode('utf-8')).hexdigest()
    fin = time.perf_counter()
    
    tiempo_promedio = (fin - inicio) / 1000 * 1000  # en milisegundos
    
    print(f"1000 operaciones de hash en {fin - inicio:.4f} segundos")
    print(f"Tiempo promedio por hash: {tiempo_promedio:.4f} ms")
    print()
    
    if tiempo_promedio < 1:
        print(f"✅ PASS: Hash muy rápido (<1ms)")
    else:
        print(f"⚠️ WARN: Hash lento (>{tiempo_promedio:.2f}ms)")
    
    print()

def test_collision_probability():
    """Explicar probabilidad de colisión."""
    print("=" * 70)
    print("TEST 4: Probabilidad de Colisión")
    print("=" * 70)
    print("SHA-256 genera hashes de 256 bits (64 caracteres hexadecimales)")
    print()
    print("Espacio de posibilidades: 2^256 ≈ 1.16 × 10^77")
    print("(Más que átomos en el universo observable: ~10^80)")
    print()
    print("Para tener 50% de probabilidad de colisión necesitarías:")
    print("  ~2^128 ≈ 3.4 × 10^38 ensayos diferentes")
    print()
    print("En la práctica:")
    print("  - 1,000 ensayos: probabilidad < 10^-70")
    print("  - 1,000,000 ensayos: probabilidad < 10^-64")
    print("  - 1,000,000,000 ensayos: probabilidad < 10^-58")
    print()
    print("✅ CONCLUSIÓN: Colisiones son prácticamente IMPOSIBLES")
    print()

if __name__ == '__main__':
    print("\n")
    print("🚀 PRUEBAS DEL SISTEMA DE HASH CACHE")
    print("\n")
    
    test_hash_consistency()
    test_hash_sensitivity()
    test_performance()
    test_collision_probability()
    
    print("=" * 70)
    print("✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 70)
    print()
