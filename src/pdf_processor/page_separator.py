"""
Separador de Páginas PDF
Filtra páginas que contienen exactamente 4 imágenes grandes y crea un nuevo PDF
"""

import pymupdf  # type: ignore
import os
from pathlib import Path
from typing import List, Tuple, Optional


class PDFPageSeparator:
    """
    Clase para separar páginas de PDF que contienen imágenes grandes
    """

    def __init__(self):
        self.min_images_per_page = 4
        self.max_images_per_page = 5  # Permitir hasta 5 imágenes (4 fotos + logo)
        self.min_image_size = (
            10000  # Tamaño mínimo en bytes para considerar imagen grande
        )

    def count_large_images_on_page(self, page) -> int:
        """
        Cuenta el número de imágenes grandes en una página específica
        Ignora logos y imágenes pequeñas

        Args:
            page: Página del PDF (objeto fitz.Page)

        Returns:
            int: Número de imágenes grandes encontradas
        """
        try:
            # Obtener la lista de imágenes en la página
            image_list = page.get_images()
            large_images_count = 0

            for img_index, img in enumerate(image_list):
                try:
                    # Obtener el XREF de la imagen
                    xref = img[0]
                    # Crear un Pixmap para analizar la imagen
                    pix = pymupdf.Pixmap(page.parent, xref)

                    # Verificar el tamaño de la imagen (ancho x alto)
                    image_size = pix.width * pix.height

                    # Considerar imagen grande si tiene más de 100x100 píxeles
                    if image_size >= 10000:  # 100x100 = 10000 píxeles
                        large_images_count += 1

                    # Liberar memoria
                    pix = None

                except Exception as e:
                    print(f"⚠️ Error analizando imagen {img_index}: {e}")
                    continue

            return large_images_count
        except Exception as e:
            print(f"⚠️ Error contando imágenes grandes en página: {e}")
            return 0

    def is_page_with_images(self, page) -> bool:
        """
        Verifica si una página contiene exactamente 4 imágenes grandes

        Args:
            page: Página del PDF (objeto fitz.Page)

        Returns:
            bool: True si la página tiene exactamente 4 imágenes grandes
        """
        image_count = self.count_large_images_on_page(page)
        return self.min_images_per_page <= image_count <= self.max_images_per_page

    def filter_pages_with_images(
        self, input_pdf_path: str, output_dir: str
    ) -> Optional[str]:
        """
        Filtra páginas que contienen exactamente 4 imágenes grandes y crea un nuevo PDF

        Args:
            input_pdf_path: Ruta del PDF de entrada
            output_dir: Directorio donde guardar el PDF filtrado

        Returns:
            Optional[str]: Ruta del PDF filtrado o None si no hay páginas válidas
        """
        try:
            # Abrir el PDF original
            pdf_document = pymupdf.open(input_pdf_path)
            total_pages = len(pdf_document)

            print(f"📖 Procesando PDF con {total_pages} páginas...")

            # Crear un nuevo documento para las páginas filtradas
            filtered_doc = pymupdf.open()
            pages_with_images = []

            # Revisar cada página
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                image_count = self.count_large_images_on_page(page)

                print(f"📄 Página {page_num + 1}: {image_count} imágenes grandes")

                if self.is_page_with_images(page):
                    # Copiar la página al nuevo documento
                    filtered_doc.insert_pdf(
                        pdf_document, from_page=page_num, to_page=page_num
                    )
                    pages_with_images.append(page_num + 1)

            # Cerrar el documento original
            pdf_document.close()

            if not pages_with_images:
                print("❌ No se encontraron páginas con exactamente 4 imágenes grandes")
                filtered_doc.close()
                return None

            # Crear directorio de salida si no existe
            os.makedirs(output_dir, exist_ok=True)

            # Guardar el PDF filtrado
            input_filename = Path(input_pdf_path).stem
            output_filename = f"{input_filename}_filtered.pdf"
            output_path = os.path.join(output_dir, output_filename)

            filtered_doc.save(output_path)
            filtered_doc.close()

            print(
                f"✅ Se encontraron {len(pages_with_images)} páginas con imágenes grandes"
            )
            print(f"📋 Páginas con imágenes: {pages_with_images}")
            print(f"💾 PDF filtrado guardado en: {output_path}")

            return output_path

        except Exception as e:
            print(f"❌ Error procesando PDF: {str(e)}")
            return None

    def get_page_info(self, pdf_path: str) -> List[Tuple[int, int]]:
        """
        Obtiene información de todas las páginas del PDF

        Args:
            pdf_path: Ruta del PDF

        Returns:
            List[Tuple[int, int]]: Lista de tuplas (número_página, cantidad_imágenes_grandes)
        """
        try:
            pdf_document = pymupdf.open(pdf_path)  # type: ignore
            page_info = []

            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                image_count = self.count_large_images_on_page(page)
                page_info.append((page_num + 1, image_count))

            pdf_document.close()
            return page_info

        except Exception as e:
            print(f"❌ Error obteniendo información del PDF: {str(e)}")
            return []
