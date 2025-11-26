
# Diccionario: nombre_archivo_ensayo -> nombre_archivo_anexo
MATCHES_SEGUROS_IA = {
    "Ensayo_Garduño_Rodríguez_Salvador_Arturo_MEMORIA_TECNOLÓGICA_¿ARCHIVO_FIEL_O_CÁRCEL_DE_LA_IMAGINACIÓN.txt": 
        "AnexoIA_Garduño_Rodríguez_Salvador_Arturo_Memoria_tecnológica_¿Archivo_fiel_o_cárcel_de_la_imaginación.txt",
    
    "Ensayo_Leyva_Angeles_Edson_Una_mirada_a_la_evolución_tecnológica_de_las_pantallas_y_su_impacto_en_la_cultura.txt": 
        "AnexoIA_Leyva_Angeles_Edson_Una_mirada_a_la_evolución_tecnológica_de_las_pantallas_y_su_impacto_en_la_cultura.txt",
    
    "Ensayo_Rodrigo_Vázquez_Ramírez_Pantallas…_¿espejos_infinitos_o_ventanas_al_abismo.txt": 
        "AnexoIA_Rodrigo_Vázquez_Ramírez_Pantallas…_¿espejos_infinitos_o_ventanas_al_abismo.txt",
    
    "Ensayo_Vania_Janet_Raya_Rios_Ver_con_las_manos,_oír_con_los_ojos_IA_accesible_en_pantallas_Samsung_para_inclusión_y_sostenibilida.txt": 
        "AnexoIA_Vania_Janet_Raya_Ríos_Ver_con_las_manos,_oír_con_los_ojos_IA_accesible_en_pantallas_Samsung_para_inclusión_y_sostenibilida.txt",
    
    "Ensayo_Victor_Arieh_Sánchez_Santiago_El_mañana_en_nuestras_manos_sembrando_futuros_con_inteligencia_y_esperanza.txt": 
        "AnexoIA_Victor_Arieh_Sánchez_Santiago_El_mañana_en_nuestras_manos_sembrando_futuros_con_inteligencia_y_esperanza.txt",
    
    "Ensayo_Paulina_Rosas_Chávez_Pantallas_con_memoria_lo_que_las_máquinas_recuerdan_de_nosotros.txt": 
        "AnexoIA_Paulina_Rosas_Pantallas_con_memoria_lo_que_las_máquinas_recuerdan_de_nosotros.txt",

    "Ensayo_Andrea_Mata_Ramírez_Memoria_tecnológica_y_sociedad_el_legado_digital_de_la_ingeniería_humana.txt": 
        "AnexoIA_Andrea_Mata_Ramírez_Memoria_tecnológica_y_sociedad.txt",
    
    "Ensayo_Chavero_Álvarez_Brian_Adair_Memoria_Tecnológica_La_Inteligencia_Artificial_como_Co-creadora_del_Futuro_Transmediático.txt": 
        "AnexoIA_Desconocido_Memoria_Tecnológica_La_Inteligencia_Artificial_como_Co-creadora_del_Futuro_Transmediático.txt",
    
    "Ensayo_Desconocido_La_Inteligencia_Artificial_el_espejo_incómodo_de_la_sociedad.txt": 
        "AnexoIA_Joshua_Vargas_La_Inteligencia_Artificial_el_espejo_incómodo_de_la_sociedad.txt",
    
    "Ensayo_Santillán_Carraro_Ezequiel_Eduardo_Pantallas_Responsables.txt": 
        "AnexoIA_Santillan_Carraro_Ezequiel_Eduardo_Herramientas_Inteligencia_Artificial.txt",
    
    "Ensayo_Fernando_Ordaz_Badager_La_inteligencia_artificial,_la_criminalidad_y_la_verdad_en_la_era_digital.txt": 
        "AnexoIA_SocratesOrdaz_La_inteligencia_artificial,_la_criminalidad_y_la_verdad_en_la_era_digital.txt",
}

# Para búsqueda rápida: dado un nombre de archivo de ensayo, obtener el anexo
def obtener_anexo_ia(nombre_archivo_ensayo: str) -> str | None:
    """
    Obtiene el nombre del archivo de anexo correspondiente al ensayo.
    
    Args:
        nombre_archivo_ensayo: Nombre del archivo del ensayo (con o sin extensión)
    
    Returns:
        Nombre del archivo del anexo si existe match seguro, None si no existe
    """
    # Asegurar que tenga extensión .txt
    if not nombre_archivo_ensayo.endswith('.txt'):
        nombre_archivo_ensayo += '.txt'
    
    return MATCHES_SEGUROS_IA.get(nombre_archivo_ensayo)


def tiene_anexo_ia(nombre_archivo_ensayo: str) -> bool:
    """
    Verifica si un ensayo tiene anexo de IA con match seguro.
    
    Args:
        nombre_archivo_ensayo: Nombre del archivo del ensayo
    
    Returns:
        True si existe match seguro, False en caso contrario
    """
    return obtener_anexo_ia(nombre_archivo_ensayo) is not None


def cargar_texto_anexo(nombre_archivo_anexo: str, directorio: str = "Anexo_procesado") -> str | None:
    """
    Carga el contenido del archivo de anexo.
    
    Args:
        nombre_archivo_anexo: Nombre del archivo del anexo
        directorio: Directorio donde se encuentra el anexo
    
    Returns:
        Contenido del anexo como string, None si no se puede leer
    """
    import os
    
    ruta_anexo = os.path.join(directorio, nombre_archivo_anexo)
    
    try:
        with open(ruta_anexo, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f" Advertencia: Anexo no encontrado: {ruta_anexo}")
        return None
    except Exception as e:
        print(f"Error al leer anexo {ruta_anexo}: {e}")
        return None


# Lista de ensayos con anexo para consulta rápida
ENSAYOS_CON_ANEXO = list(MATCHES_SEGUROS_IA.keys())
