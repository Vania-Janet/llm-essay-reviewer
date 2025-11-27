"""
Script de prueba rápida para verificar el agente con actualizaciones concurrentes.
"""
from agent import EvaluadorEnsayos

def main():
    print("🧪 Probando el agente evaluador con texto de prueba...")
    
    # Crear evaluador
    evaluador = EvaluadorEnsayos(model_name="gpt-4o-mini", temperature=0.3)
    
    # Texto de prueba corto
    ensayo_prueba = """
    La inteligencia artificial representa uno de los avances tecnológicos más significativos 
    de nuestro tiempo. Su impacto en la sociedad es profundo y multifacético, abarcando 
    desde la automatización de tareas rutinarias hasta la creación de nuevas formas de 
    interacción humana. Sin embargo, también plantea desafíos éticos importantes relacionados 
    con la privacidad, el sesgo algorítmico y el futuro del trabajo.
    
    En este ensayo, exploraremos cómo la IA puede ser una herramienta para el bienestar 
    colectivo si se desarrolla de manera responsable y ética.
    """
    
    anexo_prueba = """
    USO DE IA: Se utilizó ChatGPT para revisar la gramática y mejorar la claridad de algunas 
    oraciones. También se consultó para obtener referencias bibliográficas sobre ética en IA.
    """
    
    try:
        # Evaluar
        evaluacion = evaluador.evaluar(ensayo_prueba, anexo_prueba)
        
        print("\n" + "="*60)
        print("✅ PRUEBA EXITOSA")
        print("="*60)
        print(f"Puntuación total: {evaluacion.puntuacion_total:.2f}/5.0")
        print(f"Calidad técnica: {evaluacion.calidad_tecnica.calificacion}/5")
        print(f"Creatividad: {evaluacion.creatividad.calificacion}/5")
        print(f"Vinculación temática: {evaluacion.vinculacion_tematica.calificacion}/5")
        print(f"Bienestar colectivo: {evaluacion.bienestar_colectivo.calificacion}/5")
        print(f"Uso responsable IA: {evaluacion.uso_responsable_ia.calificacion}/5")
        print(f"Potencial impacto: {evaluacion.potencial_impacto.calificacion}/5")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
