"""
Test del Extractor Avanzado de Imágenes PDF
Prueba el método pdf2image + OpenCV para extracción con coordenadas reales
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from pdf_processor.page_separator import PDFPageSeparator
from pdf_processor.advanced_image_extractor import AdvancedImageExtractor
from utils.file_manager import FileManager


def test_advanced_extractor():
    """
    Función de prueba para el extractor avanzado
    """
    print("🔬 Iniciando Test del Extractor Avanzado...")

    # Configurar rutas
    input_pdf = "src/data/panel_fotografico_corregido_cabanaconde.pdf"
    temp_dir = "temp"
    debug_output_dir = "debug_advanced_images"

    # Verificar que el archivo PDF existe
    if not os.path.exists(input_pdf):
        print(f"❌ Error: No se encontró el archivo {input_pdf}")
        return

    try:
        # Paso 1: Separar páginas con imágenes (como en main.py)
        print("📄 Paso 1: Separando páginas con imágenes...")
        separator = PDFPageSeparator()
        filtered_pdf_path = separator.filter_pages_with_images(input_pdf, temp_dir)

        if not filtered_pdf_path:
            print("❌ No se encontraron páginas con imágenes")
            return

        print(f"✅ Páginas filtradas guardadas en: {filtered_pdf_path}")

        # Paso 2: Crear extractor avanzado
        advanced_extractor = AdvancedImageExtractor()

        # Verificar dependencias
        print("🔍 Verificando dependencias...")
        if not advanced_extractor.check_dependencies():
            print("❌ Dependencias no disponibles")
            print("💡 Instalar con:")
            print("   pip install pdf2image opencv-python")
            print("   # En Windows también necesitas poppler")
            print(
                "   # Descargar de: https://github.com/oschwartz10612/poppler-windows/releases"
            )
            return

        print("✅ Dependencias verificadas")
        print("🚀 Iniciando extracción con método avanzado...")

        # Crear directorio de debug
        os.makedirs(debug_output_dir, exist_ok=True)

        # Procesar PDF filtrado con método avanzado
        if advanced_extractor.extract_images_from_pdf(
            filtered_pdf_path, debug_output_dir
        ):
            print(
                f"✅ Extracción avanzada completada! Imágenes guardadas en: {debug_output_dir}"
            )
        else:
            print("❌ Error en extracción avanzada")

    except Exception as e:
        print(f"❌ Error durante el test: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        # Limpiar archivos temporales
        file_manager = FileManager()
        file_manager.cleanup_temp_files(temp_dir)


if __name__ == "__main__":
    test_advanced_extractor()
