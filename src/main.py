"""
Procesador de Paneles Fotográficos - Archivo Principal
Orquesta todo el proceso de extracción y procesamiento de PDFs
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from pdf_processor.page_separator import PDFPageSeparator
from pdf_processor.advanced_image_extractor import AdvancedImageExtractor
from pdf_processor.text_extractor import TextExtractor
from llm_processor.llm_processor import LLMProcessor
from utils.file_manager import FileManager
from utils.output_organizer import OutputOrganizer
from pdf_generator.pdf_generator import PDFPanelGenerator
from pdf_generator.pdf_unifier import PDFUnifier


def main():
    """
    Función principal que orquesta todo el proceso
    """
    print("🚀 Iniciando Procesador de Paneles Fotográficos...")

    # Configurar rutas
    input_pdf = "src/data/panel_fotografico_corregido_cabanaconde.pdf"
    temp_dir = "temp"

    # Verificar que el archivo PDF existe
    if not os.path.exists(input_pdf):
        print(f"❌ Error: No se encontró el archivo {input_pdf}")
        return

    try:
        # Paso 1: Separar páginas con imágenes
        print("📄 Paso 1: Separando páginas con imágenes...")
        separator = PDFPageSeparator()
        filtered_pdf_path = separator.filter_pages_with_images(input_pdf, temp_dir)

        if filtered_pdf_path:
            print(f"✅ Páginas filtradas guardadas en: {filtered_pdf_path}")
        else:
            print("❌ No se encontraron páginas con imágenes")
            return

        # Paso 2: Extraer imágenes de las páginas filtradas
        print("🖼️ Paso 2: Extrayendo imágenes con método avanzado...")
        image_extractor = AdvancedImageExtractor()
        images_output_dir = "output/images"

        if image_extractor.extract_images_from_pdf(
            filtered_pdf_path, images_output_dir
        ):
            print(
                f"✅ Imágenes extraídas con coordenadas reales guardadas en: {images_output_dir}"
            )
        else:
            print("❌ Error extrayendo imágenes")
            return

        # Paso 3: Extraer texto de las páginas filtradas
        print("📄 Paso 3: Extrayendo texto...")
        text_extractor = TextExtractor()

        if text_extractor.extract_text_from_pdf(filtered_pdf_path, images_output_dir):
            print(f"✅ Texto extraído guardado en: {images_output_dir}")
        else:
            print("❌ Error extrayendo texto")
            return

            # Paso 4: Procesar texto con LLM
        print("🤖 Paso 4: Procesando texto con LLM...")
        llm_processor = LLMProcessor()

        # Procesar todos los archivos markdown
        results = llm_processor.process_all_text_files(images_output_dir)

        if results:
            # Guardar resultados en JSON dentro de cada carpeta de página
            if llm_processor.save_results(results, images_output_dir):
                print(f"✅ Resultados guardados en las carpetas de páginas")
            else:
                print("❌ Error guardando resultados")
                return
        else:
            print("❌ No se obtuvieron resultados del LLM")
            return

        # Paso 5: Organizar output por actividades
        print("📂 Paso 5: Organizando output por actividades...")
        organizer = OutputOrganizer()

        if organizer.organize_output():
            stats = organizer.get_organization_stats()
            print(f"✅ Output organizado exitosamente!")
            print(
                f"📊 Estadísticas: {stats['organization_stats']['total_sets_organized']} sets organizados en {stats['organization_stats']['total_activity_folders']} actividades"
            )
        else:
            print("❌ Error organizando output")
            return

        # Paso 6: Generar PDFs por actividad
        print("📄 Paso 6: Generando PDFs por actividad...")
        pdf_generator = PDFPanelGenerator()

        if pdf_generator.generate_pdfs():
            print("✅ PDFs generados exitosamente!")
        else:
            print("❌ Error generando PDFs")
            return

        # Paso 7: Unificar PDFs en un solo archivo
        print("📄 Paso 7: Unificando PDFs...")
        pdf_unifier = PDFUnifier()

        if pdf_unifier.unify_pdfs():
            unified_path = pdf_unifier.get_unified_pdf_path()
            print(f"✅ PDF unificado creado exitosamente: {unified_path}")
        else:
            print("❌ Error unificando PDFs")
            return

        print("🎉 Proceso completado exitosamente!")

    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")
    finally:
        # Limpiar archivos temporales
        file_manager = FileManager()
        file_manager.cleanup_temp_files(temp_dir)


if __name__ == "__main__":
    main()
