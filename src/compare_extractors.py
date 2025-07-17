"""
Comparador de Extractores de Imágenes PDF
Compara el método original vs el método avanzado
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from pdf_processor.image_extractor import ImageExtractor
from pdf_processor.advanced_image_extractor import AdvancedImageExtractor
from pdf_processor.page_separator import PDFPageSeparator
from utils.file_manager import FileManager


def compare_extractors():
    """
    Compara ambos métodos de extracción
    """
    print("🔬 Comparando Métodos de Extracción de Imágenes...")

    # Configurar rutas
    input_pdf = "src/data/panel_fotografico_corregido_cabanaconde.pdf"
    temp_dir = "temp"
    output_original = "output/original_method"
    output_advanced = "output/advanced_method"

    # Verificar que el archivo PDF existe
    if not os.path.exists(input_pdf):
        print(f"❌ Error: No se encontró el archivo {input_pdf}")
        return

    try:
        # Paso 1: Separar páginas con imágenes
        print("📄 Paso 1: Separando páginas con imágenes...")
        separator = PDFPageSeparator()
        filtered_pdf_path = separator.filter_pages_with_images(input_pdf, temp_dir)

        if not filtered_pdf_path:
            print("❌ No se encontraron páginas con imágenes")
            return

        print(f"✅ Páginas filtradas: {filtered_pdf_path}")

        # Paso 2: Probar método original
        print("\n🔄 MÉTODO ORIGINAL (PyMuPDF)")
        print("=" * 50)

        original_extractor = ImageExtractor()
        if original_extractor.extract_images_from_pdf(
            filtered_pdf_path, output_original
        ):
            print("✅ Método original completado")
        else:
            print("❌ Error en método original")

        # Paso 3: Probar método avanzado
        print("\n🚀 MÉTODO AVANZADO (pdf2image + OpenCV)")
        print("=" * 50)

        advanced_extractor = AdvancedImageExtractor()

        # Verificar dependencias
        if not advanced_extractor.check_dependencies():
            print("❌ Dependencias no disponibles para método avanzado")
            print("💡 Instalar con: pip install pdf2image opencv-python")
            print("   # En Windows también necesitas poppler")
            return

        if advanced_extractor.extract_images_from_pdf(
            filtered_pdf_path, output_advanced
        ):
            print("✅ Método avanzado completado")
        else:
            print("❌ Error en método avanzado")

        # Paso 4: Comparar resultados
        print("\n📊 COMPARACIÓN DE RESULTADOS")
        print("=" * 50)

        compare_results(output_original, output_advanced)

    except Exception as e:
        print(f"❌ Error durante la comparación: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        # Limpiar archivos temporales
        file_manager = FileManager()
        file_manager.cleanup_temp_files(temp_dir)


def compare_results(original_dir: str, advanced_dir: str):
    """
    Compara los resultados de ambos métodos

    Args:
        original_dir: Directorio con resultados del método original
        advanced_dir: Directorio con resultados del método avanzado
    """
    try:
        print(f"📁 Método Original: {original_dir}")
        print(f"📁 Método Avanzado: {advanced_dir}")

        # Contar archivos en cada directorio
        original_files = count_png_files(original_dir)
        advanced_files = count_png_files(advanced_dir)

        print(f"\n📈 Estadísticas:")
        print(f"   Método Original: {original_files} archivos PNG")
        print(f"   Método Avanzado: {advanced_files} archivos PNG")

        # Comparar estructura de carpetas
        print(f"\n📂 Estructura de carpetas:")
        print(f"   Método Original: {count_directories(original_dir)} carpetas")
        print(f"   Método Avanzado: {count_directories(advanced_dir)} carpetas")

        # Verificar si las imágenes tienen el mismo tamaño
        print(f"\n🔍 Comparando tamaños de imágenes...")
        compare_image_sizes(original_dir, advanced_dir)

    except Exception as e:
        print(f"❌ Error comparando resultados: {e}")


def count_png_files(directory: str) -> int:
    """Cuenta archivos PNG en un directorio"""
    count = 0
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".png"):
                    count += 1
    return count


def count_directories(directory: str) -> int:
    """Cuenta subdirectorios en un directorio"""
    count = 0
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            count += len(dirs)
    return count


def compare_image_sizes(original_dir: str, advanced_dir: str):
    """Compara tamaños de imágenes entre ambos métodos"""
    try:
        from PIL import Image

        # Obtener tamaños de imágenes del método original
        original_sizes = get_image_sizes(original_dir)
        advanced_sizes = get_image_sizes(advanced_dir)

        print(f"   Método Original - Tamaños: {original_sizes}")
        print(f"   Método Avanzado - Tamaños: {advanced_sizes}")

        # Verificar si los tamaños son similares
        if original_sizes and advanced_sizes:
            if len(original_sizes) == len(advanced_sizes):
                print("   ✅ Ambos métodos extrajeron la misma cantidad de imágenes")
            else:
                print("   ⚠️ Diferente cantidad de imágenes extraídas")

    except ImportError:
        print("   ⚠️ PIL no disponible para comparar tamaños")
    except Exception as e:
        print(f"   ❌ Error comparando tamaños: {e}")


def get_image_sizes(directory: str) -> list:
    """Obtiene tamaños de imágenes en un directorio"""
    sizes = []
    if os.path.exists(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".png"):
                    try:
                        from PIL import Image

                        img_path = os.path.join(root, file)
                        with Image.open(img_path) as img:
                            sizes.append(img.size)
                    except:
                        pass
    return sizes


if __name__ == "__main__":
    compare_extractors()
