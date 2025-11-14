"""
Script para evaluar múltiples ensayos desde un directorio.
"""
import os
from pathlib import Path
from agent import EvaluadorEnsayos
from main import imprimir_evaluacion, guardar_evaluacion_html


def evaluar_directorio(directorio: str, output_dir: str = "evaluaciones"):
    """
    Evalúa todos los archivos .txt en un directorio.
    
    Args:
        directorio: Ruta del directorio con ensayos
        output_dir: Directorio donde guardar los reportes HTML
    """
    # Crear directorio de salida
    Path(output_dir).mkdir(exist_ok=True)
    
    # Buscar archivos .txt
    archivos = list(Path(directorio).glob("*.txt"))
    
    if not archivos:
        print(f"No se encontraron archivos .txt en {directorio}")
        return
    
    print(f"\nSe encontraron {len(archivos)} ensayos para evaluar")
    print("="*80)
    
    # Crear evaluador
    evaluador = EvaluadorEnsayos()
    
    # Evaluar cada archivo
    resultados = []
    for i, archivo in enumerate(archivos, 1):
        print(f"\n\n{'='*80}")
        print(f"Evaluando {i}/{len(archivos)}: {archivo.name}")
        print('='*80)
        
        try:
            # Leer ensayo
            with open(archivo, 'r', encoding='utf-8') as f:
                ensayo = f.read()
            
            # Evaluar
            evaluacion = evaluador.evaluar(ensayo)
            
            # Guardar resultado
            nombre_html = f"{archivo.stem}_evaluacion.html"
            ruta_html = Path(output_dir) / nombre_html
            guardar_evaluacion_html(evaluacion, str(ruta_html))
            
            resultados.append({
                'archivo': archivo.name,
                'puntuacion': evaluacion.puntuacion_total,
                'evaluacion': evaluacion
            })
            
            print(f"\nEvaluación completada: {evaluacion.puntuacion_total:.2f}/5.00")
            
        except Exception as e:
            print(f"\n Error evaluando {archivo.name}: {e}")
            continue
    
    # Resumen final
    print("\n\n" + "="*80)
    print("RESUMEN DE EVALUACIONES")
    print("="*80)
    
    # Ordenar por puntuación
    resultados_ordenados = sorted(resultados, key=lambda x: x['puntuacion'], reverse=True)
    
    for i, resultado in enumerate(resultados_ordenados, 1):
        print(f"{i}. {resultado['archivo']:40} | {resultado['puntuacion']:.2f}/5.00")
    
    print(f"\n✅ Todos los reportes guardados en: {output_dir}/")


def main():
    """Función principal."""
    print("\n📚 EVALUADOR MASIVO DE ENSAYOS")
    print("="*80)
    
    directorio = input("\nIngresa la ruta del directorio con ensayos (.txt): ").strip()
    
    if not os.path.exists(directorio):
        print(f"❌ Error: No se encontró el directorio {directorio}")
        return
    
    output_dir = input("Directorio de salida (default: evaluaciones): ").strip()
    if not output_dir:
        output_dir = "evaluaciones"
    
    evaluar_directorio(directorio, output_dir)


if __name__ == "__main__":
    main()
