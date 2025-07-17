"""
Extractor de Imágenes PDF
Extrae las 4 imágenes más grandes de cada página y las guarda con nombres específicos
"""

import pymupdf  # type: ignore
import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from PIL import Image
import io


class ImageExtractor:
    """
    Clase para extraer imágenes de páginas PDF y guardarlas con nombres específicos
    """

    def __init__(self):
        self.image_positions = {
            "before": "superior_izquierda",
            "during1": "superior_derecha",
            "during2": "inferior_izquierda",
            "after": "inferior_derecha",
        }

    def get_image_info(self, page, img_index: int) -> Optional[Dict]:
        """
        Obtiene información detallada de una imagen

        Args:
            page: Página del PDF
            img_index: Índice de la imagen

        Returns:
            Dict con información de la imagen o None si hay error
        """
        try:
            # Obtener la lista de imágenes
            image_list = page.get_images()
            if img_index >= len(image_list):
                return None

            # Obtener información de la imagen
            img = image_list[img_index]
            xref = img[0]

            # Crear Pixmap para obtener dimensiones
            pix = pymupdf.Pixmap(page.parent, xref)

            # Obtener coordenadas reales de la imagen en la página
            # Buscar la imagen en el contenido de la página
            image_rect = self._find_image_rect(page, xref)

            image_info = {
                "index": img_index,
                "xref": xref,
                "width": pix.width,
                "height": pix.height,
                "size": pix.width * pix.height,
                "pixmap": pix,
                "rect": image_rect,  # Coordenadas reales
            }

            return image_info

        except Exception as e:
            print(f"⚠️ Error obteniendo información de imagen {img_index}: {e}")
            return None

    def _find_image_rect(self, page, xref) -> Optional[tuple]:
        """
        Encuentra las coordenadas reales de una imagen en la página

        Args:
            page: Página del PDF
            xref: Referencia de la imagen

        Returns:
            tuple: (x0, y0, x1, y1) o None si no se encuentra
        """
        try:
            # Buscar la imagen en el contenido de la página
            for block in page.get_text("dict")["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if "image" in span and span["image"] == xref:
                                return (
                                    span["bbox"][0],
                                    span["bbox"][1],
                                    span["bbox"][2],
                                    span["bbox"][3],
                                )

            # Si no se encuentra en el contenido, usar aproximación
            # basada en el orden de aparición
            return None

        except Exception as e:
            print(f"⚠️ Error encontrando coordenadas de imagen: {e}")
            return None

    def get_largest_images(self, page, count: int = 4) -> List[Dict]:
        """
        Obtiene las imágenes más grandes de una página

        Args:
            page: Página del PDF
            count: Número de imágenes a obtener

        Returns:
            Lista de diccionarios con información de las imágenes más grandes
        """
        try:
            image_list = page.get_images()
            if not image_list:
                return []

            # Obtener información de todas las imágenes
            images_info = []
            for img_index in range(len(image_list)):
                img_info = self.get_image_info(page, img_index)
                if img_info:
                    images_info.append(img_info)

            # Ordenar por tamaño (más grandes primero)
            images_info.sort(key=lambda x: x["size"], reverse=True)

            # Tomar las primeras 'count' imágenes
            return images_info[:count]

        except Exception as e:
            print(f"⚠️ Error obteniendo imágenes más grandes: {e}")
            return []

    def determine_image_positions(
        self, page, images_info: List[Dict]
    ) -> Dict[str, str]:
        """
        Determina las posiciones de las 4 imágenes basado en coordenadas reales
        Sistema de coordenadas: y=0 en la parte superior, aumenta hacia abajo

        Args:
            page: Página del PDF
            images_info: Lista de información de las 4 imágenes más grandes

        Returns:
            Dict: Mapeo de índice de imagen a posición (before, during1, during2, after)
        """
        try:
            # Obtener dimensiones de la página
            page_width = page.rect.width
            page_height = page.rect.height

            # Filtrar imágenes que tienen coordenadas reales
            images_with_coords = []
            for img_info in images_info:
                if img_info.get("rect"):
                    x0, y0, x1, y1 = img_info["rect"]
                    center_x = (x0 + x1) / 2
                    center_y = (y0 + y1) / 2

                    images_with_coords.append(
                        {
                            "index": img_info["index"],
                            "center_x": center_x,
                            "center_y": center_y,
                            "rect": img_info["rect"],
                        }
                    )

            # Si no tenemos coordenadas reales, usar método de fallback
            if len(images_with_coords) < 4:
                print(
                    "⚠️ No se encontraron coordenadas reales para todas las imágenes, usando método de fallback"
                )
                return self._fallback_position_determination(images_info)

            # Separar imágenes por posición vertical
            # En PyMuPDF: y menor = superior, y mayor = inferior
            upper_images = [
                img for img in images_with_coords if img["center_y"] < page_height / 2
            ]
            lower_images = [
                img for img in images_with_coords if img["center_y"] >= page_height / 2
            ]

            # Validar que tenemos 2 imágenes arriba y 2 abajo
            if len(upper_images) != 2 or len(lower_images) != 2:
                print("⚠️ Distribución de imágenes no es 2x2, usando método de fallback")
                return self._fallback_position_determination(images_info)

            # Determinar posiciones horizontales en cada fila
            # Fila superior (y menor)
            upper_left = min(upper_images, key=lambda x: x["center_x"])  # before
            upper_right = max(upper_images, key=lambda x: x["center_x"])  # during1

            # Fila inferior (y mayor)
            lower_left = min(lower_images, key=lambda x: x["center_x"])  # during2
            lower_right = max(lower_images, key=lambda x: x["center_x"])  # after

            # Crear mapeo de índices a posiciones
            position_mapping = {
                upper_left["index"]: "before",
                upper_right["index"]: "during1",
                lower_left["index"]: "during2",
                lower_right["index"]: "after",
            }

            print(f"📍 Posiciones determinadas por coordenadas reales:")
            for img in images_with_coords:
                pos = position_mapping[img["index"]]
                print(f"   - {pos}: ({img['center_x']:.1f}, {img['center_y']:.1f})")

            return position_mapping

        except Exception as e:
            print(f"⚠️ Error determinando posiciones por coordenadas: {e}")
            return self._fallback_position_determination(images_info)

    def _fallback_position_determination(
        self, images_info: List[Dict]
    ) -> Dict[str, str]:
        """
        Método de fallback basado en orden de aparición

        Args:
            images_info: Lista de información de las imágenes

        Returns:
            Dict: Mapeo de índice a posición
        """
        positions = ["before", "during1", "during2", "after"]
        position_mapping = {}

        for i, img_info in enumerate(images_info):
            position_mapping[img_info["index"]] = positions[i % 4]

        print("⚠️ Usando método de fallback basado en orden de aparición")
        return position_mapping

    def save_image(self, image_info: Dict, output_dir: str, filename: str) -> bool:
        """
        Guarda una imagen en formato PNG

        Args:
            image_info: Información de la imagen
            output_dir: Directorio de salida
            filename: Nombre del archivo

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Crear directorio si no existe
            os.makedirs(output_dir, exist_ok=True)

            # Obtener el Pixmap
            pix = image_info["pixmap"]

            # Convertir a RGB si es necesario
            if pix.n - pix.alpha > 3:  # CMYK
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

            # Guardar como PNG
            output_path = os.path.join(output_dir, f"{filename}.png")
            pix.save(output_path)

            print(f"💾 Guardada: {filename}.png ({pix.width}x{pix.height})")
            return True

        except Exception as e:
            print(f"❌ Error guardando imagen {filename}: {e}")
            return False

    def extract_images_from_page(self, page, page_num: int, output_dir: str) -> bool:
        """
        Extrae las 4 imágenes más grandes de una página

        Args:
            page: Página del PDF
            page_num: Número de página
            output_dir: Directorio de salida

        Returns:
            bool: True si se extrajeron exitosamente
        """
        try:
            print(f"📄 Procesando página {page_num + 1}...")

            # Obtener las 4 imágenes más grandes
            largest_images = self.get_largest_images(page, 4)

            if len(largest_images) < 4:
                print(
                    f"⚠️ Página {page_num + 1}: Solo se encontraron {len(largest_images)} imágenes grandes"
                )
                return False

            # Crear subdirectorio para la página
            page_dir = os.path.join(output_dir, f"page_{page_num + 1}")
            os.makedirs(page_dir, exist_ok=True)

            # Determinar posiciones de todas las imágenes
            position_mapping = self.determine_image_positions(page, largest_images)

            # Procesar cada imagen
            saved_count = 0
            for image_info in largest_images:
                # Obtener posición del mapeo
                position = position_mapping.get(image_info["index"], "unknown")
                filename = f"{position}"

                # Guardar imagen
                if self.save_image(image_info, page_dir, filename):
                    saved_count += 1

                # Liberar memoria
                image_info["pixmap"] = None

            print(f"✅ Página {page_num + 1}: {saved_count}/4 imágenes extraídas")
            return saved_count == 4

        except Exception as e:
            print(f"❌ Error procesando página {page_num + 1}: {e}")
            return False

    def extract_images_from_pdf(self, pdf_path: str, output_dir: str) -> bool:
        """
        Extrae imágenes de todas las páginas de un PDF

        Args:
            pdf_path: Ruta del PDF
            output_dir: Directorio de salida

        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            print(f"🖼️ Extrayendo imágenes de: {pdf_path}")

            # Abrir PDF
            pdf_document = pymupdf.open(pdf_path)
            total_pages = len(pdf_document)

            print(f"📖 PDF tiene {total_pages} páginas")

            # Procesar cada página
            successful_pages = 0
            for page_num in range(total_pages):
                page = pdf_document[page_num]

                if self.extract_images_from_page(page, page_num, output_dir):
                    successful_pages += 1

            # Cerrar documento
            pdf_document.close()

            print(
                f"✅ Extracción completada: {successful_pages}/{total_pages} páginas procesadas"
            )
            return successful_pages > 0

        except Exception as e:
            print(f"❌ Error extrayendo imágenes del PDF: {e}")
            return False
