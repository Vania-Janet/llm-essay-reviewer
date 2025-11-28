"""
Módulo para procesar PDFs y limpiar el texto extraído usando LLM.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


PROMPT_LIMPIEZA = """Eres un experto en limpieza y formateo de texto extraído de PDFs.

Tu tarea es limpiar el siguiente texto que fue extraído de un PDF, manteniendo TODO el contenido original intacto.

INSTRUCCIONES IMPORTANTES:
1. Une líneas cortadas que pertenecen al mismo párrafo (palabras cortadas con guiones, líneas que continúan)
2. Elimina números de página sueltos
3. Elimina encabezados y pies de página repetitivos
4. Mantén la separación clara entre párrafos (línea en blanco entre ellos)
5. Conserva TODAS las citas textuales y referencias bibliográficas exactamente como aparecen
6. Conserva títulos, subtítulos y estructura del documento
7. NO resumas, NO parafrasees, NO cambies el contenido
8. NO agregues ni quites ideas, solo mejora el formato
9. Corrige errores obvios de OCR (letras mal reconocidas)
10. Mantén el estilo y tono original del autor

TEXTO EXTRAÍDO DEL PDF:
{texto_crudo}

Devuelve únicamente el texto limpio y bien formateado, sin comentarios adicionales."""


class PDFProcessor:
    """Procesador de PDFs con limpieza automática usando LLM."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.1):
        """
        Inicializa el procesador de PDFs.
        
        Args:
            model_name: Modelo de OpenAI a usar (gpt-4o-mini es más económico)
            temperature: Temperatura baja para mantener fidelidad al texto original
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("user", PROMPT_LIMPIEZA)
        ])
    
    def extraer_texto_pypdf(self, pdf_path: str) -> str:
        """
        Extrae texto de un PDF usando pypdf.
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Texto extraído del PDF
        """
        if not PYPDF_AVAILABLE:
            raise ImportError("pypdf no está instalado. Instálalo con: pip install pypdf")
        
        texto_completo = []
        
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            num_paginas = len(reader.pages)
            
            print(f"Extrayendo texto de {num_paginas} paginas con pypdf...")
            
            for i, page in enumerate(reader.pages, 1):
                texto = page.extract_text()
                if texto.strip():
                    texto_completo.append(texto)
                print(f"   Página {i}/{num_paginas} procesada", end='\r')
            
            print()  # Nueva línea después del progreso
        
        return "\n\n".join(texto_completo)
    
    def extraer_texto_pdfplumber(self, pdf_path: str) -> str:
        """
        Extrae texto de un PDF usando pdfplumber (mejor para tablas y layout complejo).
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Texto extraído del PDF
        """
        if not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber no está instalado. Instálalo con: pip install pdfplumber")
        
        texto_completo = []
        
        with pdfplumber.open(pdf_path) as pdf:
            num_paginas = len(pdf.pages)
            
            print(f"Extrayendo texto de {num_paginas} paginas con pdfplumber...")
            
            for i, page in enumerate(pdf.pages, 1):
                texto = page.extract_text()
                if texto and texto.strip():
                    texto_completo.append(texto)
                print(f"   Página {i}/{num_paginas} procesada", end='\r')
            
            print()  # Nueva línea después del progreso
        
        return "\n\n".join(texto_completo)
    
    def extraer_texto(self, pdf_path: str, metodo: str = "auto") -> str:
        """
        Extrae texto de un PDF usando el método especificado.
        
        Args:
            pdf_path: Ruta al archivo PDF
            metodo: "auto", "pypdf" o "pdfplumber"
            
        Returns:
            Texto extraído del PDF
        """
        if metodo == "auto":
            # Preferir pdfplumber si está disponible
            if PDFPLUMBER_AVAILABLE:
                return self.extraer_texto_pdfplumber(pdf_path)
            elif PYPDF_AVAILABLE:
                return self.extraer_texto_pypdf(pdf_path)
            else:
                raise ImportError(
                    "No se encontró ninguna biblioteca de PDF instalada. "
                    "Instala una con: pip install pypdf o pip install pdfplumber"
                )
        elif metodo == "pypdf":
            return self.extraer_texto_pypdf(pdf_path)
        elif metodo == "pdfplumber":
            return self.extraer_texto_pdfplumber(pdf_path)
        else:
            raise ValueError(f"Método no válido: {metodo}. Usa 'auto', 'pypdf' o 'pdfplumber'")
    
    def limpiar_texto(self, texto_crudo: str) -> str:
        """
        Limpia el texto extraído usando LLM.
        
        Args:
            texto_crudo: Texto extraído del PDF sin procesar
            
        Returns:
            Texto limpio y bien formateado
        """
        print("🧹 Limpiando texto con LLM...")
        
        chain = self.prompt | self.llm
        respuesta = chain.invoke({"texto_crudo": texto_crudo})
        
        return respuesta.content.strip()
    
    def procesar_pdf(
        self, 
        pdf_path: str, 
        output_path: Optional[str] = None,
        metodo: str = "auto",
        limpiar: bool = True
    ) -> str:
        """
        Procesa un PDF completo: extrae y opcionalmente limpia el texto.
        
        Args:
            pdf_path: Ruta al archivo PDF
            output_path: Ruta donde guardar el texto limpio (opcional)
            metodo: Método de extracción ("auto", "pypdf", "pdfplumber")
            limpiar: Si True, limpia el texto con LLM
            
        Returns:
            Texto procesado (limpio o crudo según el parámetro)
        """
        # Validar que el archivo existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")
        
        print(f"\nProcesando PDF: {Path(pdf_path).name}")
        print("="*80)
        
        # Extraer texto
        texto = self.extraer_texto(pdf_path, metodo=metodo)
        
        print(f"Extraidos {len(texto)} caracteres")
        
        # Limpiar si se solicitó
        if limpiar:
            texto = self.limpiar_texto(texto)
            print(f"Texto limpiado: {len(texto)} caracteres")
        
        # Guardar si se especificó ruta de salida
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(texto)
            print(f"Guardado en: {output_path}")
        
        print("="*80 + "\n")
        
        return texto
    
    def procesar_directorio(
        self,
        directorio: str,
        output_dir: str = "ensayos_limpios",
        metodo: str = "auto",
        limpiar: bool = True
    ) -> dict[str, str]:
        """
        Procesa todos los PDFs en un directorio.
        
        Args:
            directorio: Directorio con archivos PDF
            output_dir: Directorio donde guardar los textos procesados
            metodo: Método de extracción
            limpiar: Si True, limpia los textos con LLM
            
        Returns:
            Diccionario con {nombre_archivo: texto_procesado}
        """
        # Crear directorio de salida
        Path(output_dir).mkdir(exist_ok=True)
        
        # Buscar PDFs
        pdfs = list(Path(directorio).glob("*.pdf"))
        
        if not pdfs:
            print(f"ERROR: No se encontraron archivos PDF en {directorio}")
            return {}
        
        print(f"\nSe encontraron {len(pdfs)} archivos PDF para procesar")
        print("="*80)
        
        resultados = {}
        
        for i, pdf_path in enumerate(pdfs, 1):
            print(f"\n[{i}/{len(pdfs)}] Procesando: {pdf_path.name}")
            
            try:
                # Generar ruta de salida
                output_path = Path(output_dir) / f"{pdf_path.stem}.txt"
                
                # Procesar PDF
                texto = self.procesar_pdf(
                    str(pdf_path),
                    output_path=str(output_path),
                    metodo=metodo,
                    limpiar=limpiar
                )
                
                resultados[pdf_path.name] = texto
                
            except Exception as e:
                print(f"ERROR: Procesando {pdf_path.name}: {e}")
                continue
        
        print("\n" + "="*80)
        print(f"Procesados {len(resultados)}/{len(pdfs)} archivos exitosamente")
        print(f"Archivos guardados en: {output_dir}/")
        print("="*80 + "\n")
        
        return resultados


def main():
    """Función principal para uso desde línea de comandos."""
    import sys
    
    print("\nPROCESADOR DE PDFs PARA ENSAYOS")
    print("="*80)
    
    if len(sys.argv) > 1:
        # Modo línea de comandos
        pdf_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        processor = PDFProcessor()
        texto = processor.procesar_pdf(pdf_path, output_path=output_path)
        
        if not output_path:
            print("\n" + "="*80)
            print("TEXTO PROCESADO:")
            print("="*80)
            print(texto[:500] + "..." if len(texto) > 500 else texto)
    else:
        # Modo interactivo
        pdf_path = input("Ingresa la ruta del PDF o directorio: ").strip()
        
        if not os.path.exists(pdf_path):
            print(f"ERROR: No se encontro {pdf_path}")
            return
        
        processor = PDFProcessor()
        
        if os.path.isdir(pdf_path):
            # Procesar directorio
            output_dir = input("Directorio de salida (default: ensayos_limpios): ").strip()
            if not output_dir:
                output_dir = "ensayos_limpios"
            
            processor.procesar_directorio(pdf_path, output_dir=output_dir)
        else:
            # Procesar archivo individual
            output_path = input("Guardar como (Enter para solo mostrar): ").strip()
            if not output_path:
                output_path = None
            
            texto = processor.procesar_pdf(pdf_path, output_path=output_path)
            
            if not output_path:
                print("\n" + "="*80)
                print("TEXTO PROCESADO (primeros 1000 caracteres):")
                print("="*80)
                print(texto[:1000] + "..." if len(texto) > 1000 else texto)


if __name__ == "__main__":
    main()
