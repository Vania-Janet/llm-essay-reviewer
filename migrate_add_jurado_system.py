#!/usr/bin/env python3
"""
Script de migración para agregar el sistema de evaluación por jurados.

Este script:
1. Crea la tabla evaluaciones_jurado
2. Actualiza la tabla usuarios para incluir roles de jurado
3. Crea un usuario admin maestro
4. Crea un usuario sistema_ia para las evaluaciones automáticas
5. Migra evaluaciones existentes al nuevo sistema (opcional)
"""
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from models import app
from database import db, Usuario, EvaluacionJurado, Ensayo
import bcrypt
from datetime import datetime


def crear_usuario_sistema_ia():
    """Crea el usuario Sistema IA si no existe."""
    sistema_ia = Usuario.query.filter_by(username='sistema_ia').first()
    
    if not sistema_ia:
        # Generar un password aleatorio (no se usará para login)
        password = bcrypt.hashpw(b'sistema_ia_no_login', bcrypt.gensalt()).decode('utf-8')
        
        sistema_ia = Usuario(
            username='sistema_ia',
            email='sistema@ia.local',
            password_hash=password,
            nombre_completo='Sistema de IA - Evaluador Automático',
            rol='sistema_ia',
            activo=True
        )
        db.session.add(sistema_ia)
        db.session.commit()
        print(f"✅ Usuario Sistema IA creado (ID: {sistema_ia.id})")
    else:
        print(f"ℹ️  Usuario Sistema IA ya existe (ID: {sistema_ia.id})")
    
    return sistema_ia


def crear_usuario_admin(username='admin', password='admin123', email='admin@essay-evaluator.com'):
    """Crea el usuario administrador maestro si no existe."""
    admin = Usuario.query.filter_by(username=username).first()
    
    if not admin:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin = Usuario(
            username=username,
            email=email,
            password_hash=password_hash,
            nombre_completo='Administrador Maestro',
            rol='admin',
            activo=True
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Usuario Admin creado (ID: {admin.id})")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   ⚠️  CAMBIA EL PASSWORD DESPUÉS DEL PRIMER LOGIN!")
    else:
        print(f"ℹ️  Usuario Admin ya existe (ID: {admin.id})")
    
    return admin


def migrar_evaluaciones_existentes():
    """
    Migra las evaluaciones existentes de la tabla ensayos al sistema de jurados.
    Las evaluaciones existentes se asignan al usuario sistema_ia.
    """
    sistema_ia = Usuario.query.filter_by(rol='sistema_ia').first()
    
    if not sistema_ia:
        print("❌ Error: Usuario sistema_ia no encontrado. Créalo primero.")
        return 0
    
    # Obtener todos los ensayos
    ensayos = Ensayo.query.all()
    migradas = 0
    
    print(f"\n📊 Migrando {len(ensayos)} evaluaciones existentes...")
    
    for ensayo in ensayos:
        # Verificar si ya existe una evaluación del sistema_ia para este ensayo
        evaluacion_existente = EvaluacionJurado.query.filter_by(
            ensayo_id=ensayo.id,
            jurado_id=sistema_ia.id
        ).first()
        
        if evaluacion_existente:
            print(f"   ⏭️  Ensayo {ensayo.id} ya tiene evaluación del sistema IA")
            continue
        
        # Crear evaluación del sistema IA basada en la evaluación existente
        evaluacion_ia = EvaluacionJurado(
            ensayo_id=ensayo.id,
            jurado_id=sistema_ia.id,
            calificacion_tecnica=ensayo.calidad_tecnica.get('calificacion', 0) if ensayo.calidad_tecnica else 0,
            calificacion_creatividad=ensayo.creatividad.get('calificacion', 0) if ensayo.creatividad else 0,
            calificacion_vinculacion=ensayo.vinculacion_tematica.get('calificacion', 0) if ensayo.vinculacion_tematica else 0,
            calificacion_bienestar=ensayo.bienestar_colectivo.get('calificacion', 0) if ensayo.bienestar_colectivo else 0,
            calificacion_uso_ia=ensayo.uso_responsable_ia.get('calificacion', 0) if ensayo.uso_responsable_ia else 0,
            calificacion_impacto=ensayo.potencial_impacto.get('calificacion', 0) if ensayo.potencial_impacto else 0,
            comentario_tecnica=ensayo.calidad_tecnica.get('comentario', '') if ensayo.calidad_tecnica else '',
            comentario_creatividad=ensayo.creatividad.get('comentario', '') if ensayo.creatividad else '',
            comentario_vinculacion=ensayo.vinculacion_tematica.get('comentario', '') if ensayo.vinculacion_tematica else '',
            comentario_bienestar=ensayo.bienestar_colectivo.get('comentario', '') if ensayo.bienestar_colectivo else '',
            comentario_uso_ia=ensayo.uso_responsable_ia.get('comentario', '') if ensayo.uso_responsable_ia else '',
            comentario_impacto=ensayo.potencial_impacto.get('comentario', '') if ensayo.potencial_impacto else '',
            comentario_general=ensayo.comentario_general or '',
            estado='completada',
            fecha_creacion=ensayo.fecha_evaluacion,
            fecha_completada=ensayo.fecha_evaluacion
        )
        
        # Calcular puntuación total
        evaluacion_ia.calcular_puntuacion_total()
        
        db.session.add(evaluacion_ia)
        migradas += 1
    
    db.session.commit()
    print(f"✅ {migradas} evaluaciones migradas al sistema de jurados")
    
    return migradas


def main():
    """Función principal de migración."""
    print(f"\n{'='*70}")
    print("🔄 MIGRACIÓN: SISTEMA DE EVALUACIÓN POR JURADOS")
    print(f"{'='*70}\n")
    
    with app.app_context():
        # 1. Crear tablas si no existen
        print("📋 Creando tablas en la base de datos...")
        db.create_all()
        print("✅ Tablas creadas/verificadas\n")
        
        # 2. Crear usuario Sistema IA
        print("🤖 Configurando usuario Sistema IA...")
        sistema_ia = crear_usuario_sistema_ia()
        print()
        
        # 3. Crear usuario Admin
        print("👤 Configurando usuario Administrador...")
        admin = crear_usuario_admin()
        print()
        
        # 4. Preguntar si migrar evaluaciones existentes
        print("📊 ¿Deseas migrar las evaluaciones existentes al nuevo sistema?")
        print("   Esto creará evaluaciones del sistema_ia para todos los ensayos existentes.")
        respuesta = input("   (s/n): ").lower().strip()
        
        if respuesta == 's':
            migradas = migrar_evaluaciones_existentes()
            print()
        else:
            print("   ⏭️  Migración de evaluaciones omitida\n")
        
        # 5. Resumen final
        print(f"{'='*70}")
        print("📊 RESUMEN DE LA MIGRACIÓN")
        print(f"{'='*70}")
        
        total_usuarios = Usuario.query.count()
        total_jurados = Usuario.query.filter_by(rol='jurado').count()
        total_admins = Usuario.query.filter_by(rol='admin').count()
        total_evaluaciones = EvaluacionJurado.query.count()
        total_ensayos = Ensayo.query.count()
        
        print(f"Total de usuarios: {total_usuarios}")
        print(f"  - Administradores: {total_admins}")
        print(f"  - Jurados: {total_jurados}")
        print(f"  - Sistema IA: 1")
        print(f"\nTotal de ensayos: {total_ensayos}")
        print(f"Total de evaluaciones: {total_evaluaciones}")
        
        if total_ensayos > 0:
            promedio_evaluaciones = total_evaluaciones / total_ensayos
            print(f"Promedio de evaluaciones por ensayo: {promedio_evaluaciones:.2f}")
        
        print(f"\n{'='*70}")
        print("✨ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print(f"{'='*70}\n")
        
        print("📝 PRÓXIMOS PASOS:")
        print("1. Cambia el password del admin en el primer login")
        print("2. Crea usuarios jurados desde el panel de administración")
        print("3. Asigna ensayos a los jurados para evaluación")
        print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
