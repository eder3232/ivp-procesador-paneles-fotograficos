"""
Extractor de Texto PDF
Extrae texto de páginas PDF y lo guarda en archivos markdown
"""

import pdfplumber
import os
from pathlib import Path
from typing import Optional, Dict, List


class TextExtractor:
    """
    Clase para extraer texto de páginas PDF y guardarlo en markdown
    """

    def __init__(self):
        self.encoding = "utf-8"

    def clean_text(self, text: str) -> str:
        """
        Limpia el texto extraído manteniendo la estructura

        Args:
            text: Texto extraído del PDF

        Returns:
            str: Texto limpio con estructura preservada
        """
        if not text:
            return ""

        # Preservar saltos de línea originales
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            # Limpiar caracteres extraños pero preservar espacios
            cleaned_line = line.strip()

            # Eliminar líneas completamente vacías
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
            else:
                # Preservar una línea vacía para separación visual
                cleaned_lines.append("")

        # Unir líneas preservando saltos de línea
        cleaned_text = "\n".join(cleaned_lines)

        # Eliminar múltiples líneas vacías consecutivas
        while "\n\n\n" in cleaned_text:
            cleaned_text = cleaned_text.replace("\n\n\n", "\n\n")

        return cleaned_text.strip()

    def extract_text_from_page(self, page, page_num: int) -> Optional[str]:
        """
        Extrae texto de una página específica

        Args:
            page: Página del PDF (objeto pdfplumber.Page)
            page_num: Número de página

        Returns:
            Optional[str]: Texto extraído y limpio, o None si hay error
        """
        try:
            # Extraer texto de la página
            text = page.extract_text()

            if not text:
                print(f"⚠️ Página {page_num + 1}: No se encontró texto")
                return None

            # Limpiar el texto
            cleaned_text = self.clean_text(text)

            if not cleaned_text:
                print(f"⚠️ Página {page_num + 1}: Texto vacío después de limpieza")
                return None

            print(f"📝 Página {page_num + 1}: {len(cleaned_text)} caracteres extraídos")
            return cleaned_text

        except Exception as e:
            print(f"❌ Error extrayendo texto de página {page_num + 1}: {e}")
            return None

    def save_text_as_markdown(self, text: str, output_dir: str, page_num: int) -> bool:
        """
        Guarda el texto extraído como archivo markdown

        Args:
            text: Texto a guardar
            output_dir: Directorio de salida
            page_num: Número de página

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Crear directorio si no existe
            os.makedirs(output_dir, exist_ok=True)

            # Crear nombre del archivo
            filename = f"text.md"
            filepath = os.path.join(output_dir, filename)

            # Crear contenido markdown
            markdown_content = f"""# Texto de la Página {page_num + 1}

{text}

---
*Extraído automáticamente del PDF*
"""

            # Guardar archivo
            with open(filepath, "w", encoding=self.encoding) as f:
                f.write(markdown_content)

            print(f"💾 Guardado: {filepath}")
            return True

        except Exception as e:
            print(f"❌ Error guardando texto de página {page_num + 1}: {e}")
            return False

    def extract_text_from_pdf(self, pdf_path: str, output_base_dir: str) -> bool:
        """
        Extrae texto de todas las páginas de un PDF

        Args:
            pdf_path: Ruta del PDF
            output_base_dir: Directorio base de salida (output/images)

        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            print(f"📄 Extrayendo texto de: {pdf_path}")

            # Abrir PDF con pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"📖 PDF tiene {total_pages} páginas")

                successful_pages = 0

                # Procesar cada página
                for page_num in range(total_pages):
                    page = pdf.pages[page_num]

                    # Extraer texto de la página
                    text = self.extract_text_from_page(page, page_num)

                    if text:
                        # Determinar directorio de salida (mismo que las imágenes)
                        page_dir = os.path.join(output_base_dir, f"page_{page_num + 1}")

                        # Guardar como markdown
                        if self.save_text_as_markdown(text, page_dir, page_num):
                            successful_pages += 1

                print(
                    f"✅ Extracción de texto completada: {successful_pages}/{total_pages} páginas procesadas"
                )
                return successful_pages > 0

        except Exception as e:
            print(f"❌ Error extrayendo texto del PDF: {e}")
            return False

    def get_text_summary(self, pdf_path: str) -> Dict:
        """
        Obtiene un resumen del texto extraído sin guardarlo

        Args:
            pdf_path: Ruta del PDF

        Returns:
            Dict: Resumen con estadísticas del texto
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_with_text = 0
                total_characters = 0

                for page_num in range(total_pages):
                    page = pdf.pages[page_num]
                    text = self.extract_text_from_page(page, page_num)

                    if text:
                        pages_with_text += 1
                        total_characters += len(text)

                return {
                    "total_pages": total_pages,
                    "pages_with_text": pages_with_text,
                    "total_characters": total_characters,
                    "average_characters_per_page": (
                        total_characters / pages_with_text if pages_with_text > 0 else 0
                    ),
                }

        except Exception as e:
            print(f"❌ Error obteniendo resumen del texto: {e}")
            return {}
