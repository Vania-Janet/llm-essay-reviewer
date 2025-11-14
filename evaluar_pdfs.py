"""
Script para procesar PDFs y evaluarlos automáticamente.
Combina la extracción/limpieza de PDFs con la evaluación de ensayos.
"""
import os
from pathlib import Path
from pdf_processor import PDFProcessor
from agent import EvaluadorEnsayos
from main import imprimir_evaluacion, guardar_evaluacion_html


def evaluar_pdf(
    pdf_path: str,
    output_dir: str = "evaluaciones_pdf",
    metodo_extraccion: str = "auto",
    guardar_texto: bool = True
):
    """
    Procesa un PDF y lo evalúa automáticamente.
    
    Args:
        pdf_path: Ruta al archivo PDF
        output_dir: Directorio donde guardar los reportes
        metodo_extraccion: Método de extracción ("auto", "pypdf", "pdfplumber")
        guardar_texto: Si True, guarda el texto limpio en .txt
    """
    # Crear directorio de salida
    Path(output_dir).mkdir(exist_ok=True)
    
    pdf_name = Path(pdf_path).stem
    
    print("\n" + "="*80)
    print(f"📄 PROCESANDO Y EVALUANDO: {pdf_name}")
    print("="*80 + "\n")
    
    # Paso 1: Extraer y limpiar texto del PDF
    print("PASO 1/2: Extracción y limpieza del PDF")
    print("-"*80)
    
    processor = PDFProcessor()
    
    texto_limpio_path = None
    if guardar_texto:
        texto_limpio_path = Path(output_dir) / f"{pdf_name}_limpio.txt"
    
    try:
        texto = processor.procesar_pdf(
            pdf_path,
            output_path=str(texto_limpio_path) if texto_limpio_path else None,
            metodo=metodo_extraccion,
            limpiar=True
        )
    except Exception as e:
        print(f"❌ Error procesando PDF: {e}")
        return None
    
    print(f"✅ Texto extraído y limpiado: {len(texto)} caracteres")
    print()
    
    # Paso 2: Evaluar el ensayo
    print("PASO 2/2: Evaluación del ensayo")
    print("-"*80)
    
    evaluador = EvaluadorEnsayos()
    
    try:
        evaluacion = evaluador.evaluar(texto)
    except Exception as e:
        print(f"❌ Error evaluando ensayo: {e}")
        return None
    
    # Mostrar resultados
    print("\n")
    imprimir_evaluacion(evaluacion)
    
    # Guardar reporte HTML
    reporte_html = Path(output_dir) / f"{pdf_name}_evaluacion.html"
    guardar_evaluacion_html(evaluacion, str(reporte_html))
    
    print(f"\n📊 Puntuación final: {evaluacion.puntuacion_total:.2f}/5.00")
    print(f"📁 Archivos generados:")
    if texto_limpio_path:
        print(f"   - Texto limpio: {texto_limpio_path}")
    print(f"   - Reporte HTML: {reporte_html}")
    print()
    
    return evaluacion


def evaluar_directorio_pdfs(
    directorio: str,
    output_dir: str = "evaluaciones_pdf",
    metodo_extraccion: str = "auto",
    guardar_textos: bool = True
):
    """
    Procesa y evalúa todos los PDFs en un directorio.
    
    Args:
        directorio: Directorio con archivos PDF
        output_dir: Directorio donde guardar los reportes
        metodo_extraccion: Método de extracción
        guardar_textos: Si True, guarda los textos limpios
    """
    # Crear directorio de salida
    Path(output_dir).mkdir(exist_ok=True)
    
    # Buscar PDFs
    pdfs = list(Path(directorio).glob("*.pdf"))
    
    if not pdfs:
        print(f"❌ No se encontraron archivos PDF en {directorio}")
        return
    
    print("\n" + "="*80)
    print(f"📚 PROCESAMIENTO MASIVO: {len(pdfs)} PDFs encontrados")
    print("="*80)
    
    resultados = []
    
    for i, pdf_path in enumerate(pdfs, 1):
        print(f"\n\n{'#'*80}")
        print(f"#{' '*78}#")
        print(f"#  [{i}/{len(pdfs)}] {pdf_path.name:^72}  #")
        print(f"#{' '*78}#")
        print(f"{'#'*80}\n")
        
        try:
            evaluacion = evaluar_pdf(
                str(pdf_path),
                output_dir=output_dir,
                metodo_extraccion=metodo_extraccion,
                guardar_texto=guardar_textos
            )
            
            if evaluacion:
                resultados.append({
                    'archivo': pdf_path.name,
                    'puntuacion': evaluacion.puntuacion_total,
                    'evaluacion': evaluacion
                })
        except Exception as e:
            print(f"❌ Error procesando {pdf_path.name}: {e}")
            continue
    
    # Resumen final
    print("\n\n" + "="*80)
    print("📊 RESUMEN FINAL DE EVALUACIONES")
    print("="*80 + "\n")
    
    if not resultados:
        print("❌ No se pudo procesar ningún PDF exitosamente")
        return
    
    # Ordenar por puntuación
    resultados_ordenados = sorted(resultados, key=lambda x: x['puntuacion'], reverse=True)
    
    print(f"{'#':<4} {'Archivo':<50} {'Puntuación':>12}")
    print("-"*80)
    
    for i, resultado in enumerate(resultados_ordenados, 1):
        nombre = resultado['archivo']
        if len(nombre) > 47:
            nombre = nombre[:44] + "..."
        
        puntuacion = resultado['puntuacion']
        
        # Emoji según puntuación
        if puntuacion >= 4.5:
            emoji = "🏆"
        elif puntuacion >= 4.0:
            emoji = "⭐"
        elif puntuacion >= 3.5:
            emoji = "✅"
        elif puntuacion >= 3.0:
            emoji = "📝"
        else:
            emoji = "📄"
        
        print(f"{i:<4} {nombre:<50} {emoji} {puntuacion:>8.2f}/5.00")
    
    # Estadísticas
    puntuaciones = [r['puntuacion'] for r in resultados]
    promedio = sum(puntuaciones) / len(puntuaciones)
    max_punt = max(puntuaciones)
    min_punt = min(puntuaciones)
    
    print("\n" + "-"*80)
    print(f"{'Estadísticas:':<50}")
    print(f"  • Total procesados: {len(resultados)}/{len(pdfs)}")
    print(f"  • Promedio: {promedio:.2f}/5.00")
    print(f"  • Máxima: {max_punt:.2f}/5.00")
    print(f"  • Mínima: {min_punt:.2f}/5.00")
    print("-"*80)
    
    print(f"\n✅ Todos los reportes guardados en: {output_dir}/")
    print("="*80 + "\n")


def main():
    """Función principal."""
    print("\n📄 EVALUADOR DE ENSAYOS DESDE PDF")
    print("="*80)
    print("\nEste script:")
    print("  1. Extrae texto de PDFs (pypdf o pdfplumber)")
    print("  2. Limpia el texto con LLM (quita números de página, une líneas, etc.)")
    print("  3. Evalúa el ensayo con los 5 criterios establecidos")
    print("  4. Genera reportes HTML detallados")
    print()
    
    ruta = input("Ingresa la ruta del PDF o directorio con PDFs: ").strip()
    
    if not os.path.exists(ruta):
        print(f"❌ Error: No se encontró {ruta}")
        return
    
    output_dir = input("Directorio de salida (default: evaluaciones_pdf): ").strip()
    if not output_dir:
        output_dir = "evaluaciones_pdf"
    
    if os.path.isdir(ruta):
        # Procesar directorio completo
        evaluar_directorio_pdfs(ruta, output_dir=output_dir)
    else:
        # Procesar archivo individual
        evaluar_pdf(ruta, output_dir=output_dir)


if __name__ == "__main__":
    main()
