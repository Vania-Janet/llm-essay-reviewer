"""
Script principal para ejecutar el agente evaluador de ensayos.
"""
import os
from agent import EvaluadorEnsayos
from models import EvaluacionEnsayo


def imprimir_evaluacion(evaluacion: EvaluacionEnsayo):
    """Imprime la evaluación de forma legible."""
    print("\n" + "="*80)
    print(" "*25 + "REPORTE DE EVALUACIÓN")
    print("="*80 + "\n")
    
    # Criterio 1
    print("📝 1. CALIDAD TÉCNICA Y RIGOR ACADÉMICO (20%)")
    print(f"   Calificación: {evaluacion.calidad_tecnica.calificacion}/5")
    print(f"   {evaluacion.calidad_tecnica.comentario}")
    print()
    
    # Criterio 2
    print("🎨 2. CREATIVIDAD Y ORIGINALIDAD (20%)")
    print(f"   Calificación: {evaluacion.creatividad.calificacion}/5")
    print(f"   {evaluacion.creatividad.comentario}")
    print()
    
    # Criterio 3
    print("🎯 3. VINCULACIÓN CON LOS EJES TEMÁTICOS (15%)")
    print(f"   Calificación: {evaluacion.vinculacion_tematica.calificacion}/5")
    print(f"   {evaluacion.vinculacion_tematica.comentario}")
    print()
    
    # Criterio 4
    print("🌍 4. REFLEXIÓN SOBRE BIENESTAR COLECTIVO Y RESPONSABILIDAD SOCIAL (20%)")
    print(f"   Calificación: {evaluacion.bienestar_colectivo.calificacion}/5")
    print(f"   {evaluacion.bienestar_colectivo.comentario}")
    print()
    
    # Criterio 5
    print("🤖 5. USO RESPONSABLE Y REFLEXIVO DE HERRAMIENTAS DE IA (15%)")
    print(f"   Calificación: {evaluacion.uso_ia.calificacion}/5")
    if evaluacion.no_utilizo_ia:
        print("   ⚠️  No utilizó IA")
    print(f"   {evaluacion.uso_ia.comentario}")
    print()
    
    # Criterio 6
    print("✨ 6. POTENCIAL DE IMPACTO Y PUBLICACIÓN (10%)")
    print(f"   Calificación: {evaluacion.potencial_impacto.calificacion}/5")
    print(f"   {evaluacion.potencial_impacto.comentario}")
    print()
    
    # Puntuación total
    print("="*80)
    print(f"🎯 PUNTUACIÓN TOTAL PONDERADA: {evaluacion.puntuacion_total:.2f}/5.00")
    print("="*80)
    print()
    
    # Comentario general
    print("📋 COMENTARIO GENERAL Y RETROALIMENTACIÓN:")
    print("-" * 80)
    print(evaluacion.comentario_general)
    print("-" * 80)
    print()
    
    if evaluacion.justificacion_breve:
        print("📌 JUSTIFICACIÓN BREVE:")
        print(evaluacion.justificacion_breve)
        print()


def guardar_evaluacion_html(evaluacion: EvaluacionEnsayo, archivo: str = "evaluacion.html"):
    """Guarda la evaluación en formato HTML."""
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evaluación de Ensayo</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }}
        .criterio {{
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            border-radius: 5px;
        }}
        .criterio h3 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        .calificacion {{
            font-size: 24px;
            font-weight: bold;
            color: #27ae60;
            margin: 10px 0;
        }}
        .comentario {{
            color: #555;
            margin-top: 10px;
            white-space: pre-wrap;
        }}
        .total {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            margin: 30px 0;
            border-radius: 10px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
        }}
        .comentario-general {{
            background-color: #fff9e6;
            padding: 25px;
            border-radius: 10px;
            border: 2px solid #ffd700;
            margin: 30px 0;
        }}
        .comentario-general h3 {{
            color: #d4a500;
            margin-top: 0;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            background-color: #e74c3c;
            color: white;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 REPORTE DE EVALUACIÓN DE ENSAYO</h1>
        
        <div class="criterio">
            <h3>📝 1. Calidad Técnica y Rigor Académico (20%)</h3>
            <div class="calificacion">Calificación: {evaluacion.calidad_tecnica.calificacion}/5</div>
            <div class="comentario">{evaluacion.calidad_tecnica.comentario}</div>
        </div>
        
        <div class="criterio">
            <h3>🎨 2. Creatividad y Originalidad (20%)</h3>
            <div class="calificacion">Calificación: {evaluacion.creatividad.calificacion}/5</div>
            <div class="comentario">{evaluacion.creatividad.comentario}</div>
        </div>
        
        <div class="criterio">
            <h3>🎯 3. Vinculación con los Ejes Temáticos (15%)</h3>
            <div class="calificacion">Calificación: {evaluacion.vinculacion_tematica.calificacion}/5</div>
            <div class="comentario">{evaluacion.vinculacion_tematica.comentario}</div>
        </div>
        
        <div class="criterio">
            <h3>🌍 4. Reflexión sobre Bienestar Colectivo y Responsabilidad Social (20%)</h3>
            <div class="calificacion">Calificación: {evaluacion.bienestar_colectivo.calificacion}/5</div>
            <div class="comentario">{evaluacion.bienestar_colectivo.comentario}</div>
        </div>
        
        <div class="criterio">
            <h3>🤖 5. Uso Responsable y Reflexivo de Herramientas de IA (15%)</h3>
            <div class="calificacion">
                Calificación: {evaluacion.uso_ia.calificacion}/5
                {"<span class='badge'>NO UTILIZÓ IA</span>" if evaluacion.no_utilizo_ia else ""}
            </div>
            <div class="comentario">{evaluacion.uso_ia.comentario}</div>
        </div>
        
        <div class="criterio">
            <h3>✨ 6. Potencial de Impacto y Publicación (10%)</h3>
            <div class="calificacion">Calificación: {evaluacion.potencial_impacto.calificacion}/5</div>
            <div class="comentario">{evaluacion.potencial_impacto.comentario}</div>
        </div>
        
        <div class="total">
            🎯 PUNTUACIÓN TOTAL PONDERADA: {evaluacion.puntuacion_total:.2f}/5.00
        </div>
        
        <div class="comentario-general">
            <h3>📋 COMENTARIO GENERAL Y RETROALIMENTACIÓN</h3>
            <div class="comentario">{evaluacion.comentario_general}</div>
        </div>
    </div>
</body>
</html>
"""
    
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Evaluación guardada en: {archivo}")


def main():
    """Función principal."""
    # Verificar variables de entorno
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: No se encontró la variable OPENAI_API_KEY en .env")
        print("   Por favor, asegúrate de que el archivo .env contiene:")
        print("   OPENAI_API_KEY=tu_clave_aqui")
        return
    
    # Ensayo de ejemplo (reemplazar con un ensayo real)
    ensayo_ejemplo = """
    La Inteligencia Artificial y el Futuro de la Educación Inclusiva
    
    En la última década, la inteligencia artificial ha transformado radicalmente múltiples aspectos 
    de nuestra sociedad, y el sector educativo no ha sido la excepción. Sin embargo, esta revolución 
    tecnológica plantea preguntas fundamentales sobre equidad, accesibilidad y el verdadero propósito 
    de la educación en el siglo XXI.
    
    La tecnología educativa impulsada por IA promete personalizar el aprendizaje, adaptándose a las 
    necesidades individuales de cada estudiante. Sistemas de tutoría inteligente pueden identificar 
    las fortalezas y debilidades de los alumnos, ofreciendo contenido y ejercicios específicamente 
    diseñados para su nivel de comprensión. Esta personalización podría democratizar el acceso a 
    una educación de calidad, tradicionalmente reservada para quienes pueden permitirse tutores 
    privados o instituciones de élite.
    
    No obstante, esta visión optimista debe confrontarse con realidades complejas. La brecha digital 
    sigue siendo una barrera formidable: millones de estudiantes en el mundo carecen de acceso a 
    dispositivos tecnológicos o conexión a internet estable. La implementación de soluciones basadas 
    en IA sin considerar estas desigualdades podría amplificar, en lugar de reducir, las disparidades 
    educativas existentes.
    
    Además, debemos cuestionar críticamente los sesgos algorítmicos que pueden perpetuar 
    discriminaciones históricas. Si los sistemas de IA se entrenan con datos que reflejan 
    inequidades sociales, económicas o culturales, corremos el riesgo de codificar y normalizar 
    estas injusticias en las herramientas que supuestamente deberían liberarnos de ellas.
    
    La verdadera innovación no radica únicamente en la sofisticación tecnológica, sino en nuestra 
    capacidad de diseñar sistemas que prioricen el bienestar colectivo. Esto implica desarrollar 
    IA educativa con participación activa de comunidades diversas, educadores y estudiantes, 
    asegurando que las soluciones respondan a necesidades reales y no a especulaciones de mercado.
    
    Imaginando el futuro, propongo un modelo de "tecnología educativa comunitaria": plataformas 
    de código abierto, desarrolladas colaborativamente, que respeten la privacidad de los 
    estudiantes y operen con transparencia algorítmica. Estas herramientas deberían ser 
    multilingües, culturalmente sensibles y diseñadas para funcionar incluso con conectividad 
    limitada, reconociendo la diversidad de contextos en los que se implementarán.
    
    La memoria tecnológica debe servirnos de guía: recordemos que cada innovación educativa 
    —desde la imprenta hasta internet— ha traído consigo promesas de democratización que no 
    siempre se materializaron equitativamente. Aprendamos de estos patrones históricos para 
    construir un futuro donde la IA en educación sea verdaderamente inclusiva, sostenible y 
    orientada al florecimiento humano integral.
    
    En conclusión, la inteligencia artificial tiene el potencial de revolucionar la educación, 
    pero solo si nos comprometemos conscientemente a diseñarla con ética, inclusión y 
    responsabilidad social en su núcleo. El desafío no es tecnológico, sino profundamente humano: 
    ¿qué tipo de sociedad queremos construir y qué papel jugará la educación en ese proyecto 
    colectivo?
    """
    
    print("\n🎓 AGENTE EVALUADOR DE ENSAYOS")
    print("=" * 80)
    print("\nEste agente evaluará ensayos según los criterios establecidos.")
    print("Utilizando: LangGraph + LangChain + OpenAI GPT-4")
    print()
    
    # Preguntar si usar ensayo de ejemplo o cargar uno
    usar_ejemplo = input("¿Deseas evaluar el ensayo de ejemplo? (s/n): ").lower().strip()
    
    if usar_ejemplo == 's':
        ensayo = ensayo_ejemplo
    else:
        archivo = input("Ingresa la ruta del archivo con el ensayo: ").strip()
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                ensayo = f.read()
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo {archivo}")
            return
        except Exception as e:
            print(f"❌ Error al leer el archivo: {e}")
            return
    
    # Crear evaluador
    print("\n🔧 Inicializando agente evaluador...")
    evaluador = EvaluadorEnsayos()
    
    # Evaluar ensayo
    evaluacion = evaluador.evaluar(ensayo)
    
    # Mostrar resultados
    imprimir_evaluacion(evaluacion)
    
    # Guardar en HTML
    guardar_html = input("\n¿Deseas guardar el reporte en HTML? (s/n): ").lower().strip()
    if guardar_html == 's':
        nombre_archivo = input("Nombre del archivo (default: evaluacion.html): ").strip()
        if not nombre_archivo:
            nombre_archivo = "evaluacion.html"
        if not nombre_archivo.endswith('.html'):
            nombre_archivo += '.html'
        
        guardar_evaluacion_html(evaluacion, nombre_archivo)
        print(f"\n✅ Puedes abrir el archivo '{nombre_archivo}' en tu navegador para ver el reporte.")


if __name__ == "__main__":
    main()
