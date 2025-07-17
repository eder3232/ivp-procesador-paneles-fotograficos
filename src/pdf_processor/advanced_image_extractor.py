"""
Extractor Avanzado de Imágenes PDF con Posiciones Reales
Usa pdf2image + OpenCV para extraer imágenes con coordenadas precisas
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import tempfile

try:
    from pdf2image import convert_from_path

    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("⚠️ pdf2image no disponible. Instalar con: pip install pdf2image")


class AdvancedImageExtractor:
    """
    Extractor avanzado que usa pdf2image + OpenCV para posiciones precisas
    """

    def __init__(self):
        self.image_positions = {
            "before": "superior_izquierda",
            "during1": "superior_derecha",
            "during2": "inferior_izquierda",
            "after": "inferior_derecha",
        }

    def check_dependencies(self) -> bool:
        """
        Verifica que las dependencias estén disponibles

        Returns:
            bool: True si todas las dependencias están disponibles
        """
        if not PDF2IMAGE_AVAILABLE:
            print("❌ pdf2image no está instalado")
            print("💡 Instalar con: pip install pdf2image")
            return False

        try:
            import cv2

            return True
        except ImportError:
            print("❌ OpenCV no está instalado")
            print("💡 Instalar con: pip install opencv-python")
            return False

    def pdf_to_image(
        self, pdf_path: str, page_num: int, dpi: int = 300
    ) -> Optional[np.ndarray]:
        """
        Convierte una página PDF a imagen de alta resolución

        Args:
            pdf_path: Ruta del PDF
            page_num: Número de página (0-indexed)
            dpi: Resolución de la imagen

        Returns:
            np.ndarray: Imagen como array de OpenCV o None si hay error
        """
        try:
            # Convertir página específica a imagen
            images = convert_from_path(
                pdf_path, first_page=page_num + 1, last_page=page_num + 1, dpi=dpi
            )

            if not images:
                print(f"❌ No se pudo convertir página {page_num + 1}")
                return None

            # Convertir PIL Image a OpenCV format
            pil_image = images[0]
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            print(
                f"✅ Página {page_num + 1} convertida a imagen ({opencv_image.shape[1]}x{opencv_image.shape[0]})"
            )
            return opencv_image

        except Exception as e:
            print(f"❌ Error convirtiendo página {page_num + 1}: {e}")
            return None

    def detect_all_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detecta todas las regiones posibles de imágenes en la página

        Args:
            image: Imagen de la página como array de OpenCV

        Returns:
            List[Dict]: Lista de todas las regiones detectadas
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Aplicar umbral adaptativo para detectar regiones
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
            )

            # Aplicar operaciones morfológicas para limpiar
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)

            # Encontrar contornos
            contours, _ = cv2.findContours(
                cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Filtrar contornos por área mínima
            img_area = image.shape[0] * image.shape[1]
            min_area = img_area * 0.001  # 0.1% del área total (muy permisivo)

            all_regions = []

            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    # Obtener bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)

                    # Calcular centro
                    center_x = x + w // 2
                    center_y = y + h // 2

                    all_regions.append(
                        {
                            "x": x,
                            "y": y,
                            "w": w,
                            "h": h,
                            "center_x": center_x,
                            "center_y": center_y,
                            "area": area,
                        }
                    )

            # Ordenar por área (más grandes primero)
            all_regions.sort(key=lambda r: r["area"], reverse=True)

            print(f"🔍 Detectadas {len(all_regions)} regiones totales")
            return all_regions

        except Exception as e:
            print(f"❌ Error detectando regiones: {e}")
            return []

    def filter_largest_images(self, regions: List[Dict], count: int = 4) -> List[Dict]:
        """
        Filtra las N imágenes más grandes

        Args:
            regions: Lista de todas las regiones detectadas
            count: Número de imágenes a seleccionar

        Returns:
            List[Dict]: Las N regiones más grandes
        """
        if len(regions) < count:
            print(f"⚠️ Solo se detectaron {len(regions)} regiones, se necesitan {count}")
            return regions

        # Tomar las N más grandes
        largest_regions = regions[:count]

        print(f"📊 Seleccionadas las {len(largest_regions)} regiones más grandes:")
        for i, region in enumerate(largest_regions):
            print(
                f"   Región {i+1}: ({region['x']}, {region['y']}) {region['w']}x{region['h']} - Área: {region['area']:.0f}"
            )

        return largest_regions

    def determine_positions_by_coordinates(
        self, regions: List[Dict], image_shape: Tuple[int, int]
    ) -> Dict[int, str]:
        """
        Determina las posiciones basado en coordenadas del centro

        Args:
            regions: Lista de regiones (máximo 4)
            image_shape: Dimensiones de la imagen (height, width)

        Returns:
            Dict[int, str]: Mapeo de índice a posición
        """
        try:
            if len(regions) != 4:
                print(
                    f"⚠️ Se detectaron {len(regions)} regiones, se necesitan exactamente 4"
                )
                return {}

            # Obtener dimensiones de la imagen
            img_height, img_width = image_shape[0], image_shape[1]

            # Separar por posición vertical (Y)
            upper_regions = [r for r in regions if r["center_y"] < img_height // 2]
            lower_regions = [r for r in regions if r["center_y"] >= img_height // 2]

            print(
                f"📊 Distribución: {len(upper_regions)} superiores, {len(lower_regions)} inferiores"
            )

            # Si no tenemos 2x2, usar orden por área
            if len(upper_regions) != 2 or len(lower_regions) != 2:
                print("⚠️ Distribución no es 2x2, usando orden por área")
                positions = ["before", "during1", "during2", "after"]
                return {i: positions[i] for i in range(len(regions))}

            # Determinar posiciones horizontales en cada fila
            # Fila superior (Y menor)
            upper_left = min(upper_regions, key=lambda r: r["center_x"])
            upper_right = max(upper_regions, key=lambda r: r["center_x"])

            # Fila inferior (Y mayor)
            lower_left = min(lower_regions, key=lambda r: r["center_x"])
            lower_right = max(lower_regions, key=lambda r: r["center_x"])

            # Crear mapeo
            position_mapping = {}

            # Asignar posiciones basado en coordenadas reales
            for i, region in enumerate(regions):
                if region == upper_left:
                    position_mapping[i] = "before"
                elif region == upper_right:
                    position_mapping[i] = "during1"
                elif region == lower_left:
                    position_mapping[i] = "during2"
                elif region == lower_right:
                    position_mapping[i] = "after"

            print("📍 Posiciones determinadas por coordenadas reales:")
            for i, region in enumerate(regions):
                pos = position_mapping.get(i, "unknown")
                print(f"   - {pos}: ({region['center_x']}, {region['center_y']})")

            return position_mapping

        except Exception as e:
            print(f"❌ Error determinando posiciones: {e}")
            return {}

    def extract_region_as_image(
        self, full_image: np.ndarray, region: Dict
    ) -> np.ndarray:
        """
        Extrae una región específica de la imagen completa

        Args:
            full_image: Imagen completa
            region: Diccionario con coordenadas de la región

        Returns:
            np.ndarray: Imagen de la región extraída
        """
        try:
            x, y, w, h = region["x"], region["y"], region["w"], region["h"]
            extracted = full_image[y : y + h, x : x + w]
            return extracted

        except Exception as e:
            print(f"❌ Error extrayendo región: {e}")
            return np.array([])

    def save_opencv_image(self, image: np.ndarray, output_path: str) -> bool:
        """
        Guarda una imagen de OpenCV como PNG

        Args:
            image: Imagen como array de OpenCV
            output_path: Ruta de salida

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Guardar imagen
            success = cv2.imwrite(output_path, image)

            if success:
                print(
                    f"💾 Guardada: {os.path.basename(output_path)} ({image.shape[1]}x{image.shape[0]})"
                )
                return True
            else:
                print(f"❌ Error guardando: {output_path}")
                return False

        except Exception as e:
            print(f"❌ Error guardando imagen: {e}")
            return False

    def extract_images_from_page(
        self, pdf_path: str, page_num: int, output_dir: str
    ) -> bool:
        """
        Extrae las 4 imágenes más grandes de una página usando coordenadas reales

        Args:
            pdf_path: Ruta del PDF
            page_num: Número de página (0-indexed)
            output_dir: Directorio de salida

        Returns:
            bool: True si se extrajeron exitosamente
        """
        try:
            print(f"📄 Procesando página {page_num + 1} con método avanzado...")

            # Verificar dependencias
            if not self.check_dependencies():
                return False

            # Convertir página a imagen
            page_image = self.pdf_to_image(pdf_path, page_num)
            if page_image is None:
                return False

            # Detectar todas las regiones
            all_regions = self.detect_all_regions(page_image)
            if not all_regions:
                print(f"⚠️ No se detectaron regiones en página {page_num + 1}")
                return False

            # Filtrar las 4 más grandes
            largest_regions = self.filter_largest_images(all_regions, 4)
            if len(largest_regions) < 4:
                print(
                    f"⚠️ Solo se detectaron {len(largest_regions)} regiones grandes, se necesitan 4"
                )
                return False

            # Determinar posiciones por coordenadas reales
            position_mapping = self.determine_positions_by_coordinates(
                largest_regions, page_image.shape
            )
            if not position_mapping:
                return False

            # Crear directorio de salida
            page_dir = os.path.join(output_dir, f"page_{page_num + 1}")
            os.makedirs(page_dir, exist_ok=True)

            # Extraer y guardar cada región
            saved_count = 0
            for i, region in enumerate(largest_regions):
                position = position_mapping.get(i, "unknown")
                filename = f"{position}"

                # Extraer región
                region_image = self.extract_region_as_image(page_image, region)
                if region_image.size == 0:
                    continue

                # Guardar imagen
                output_path = os.path.join(page_dir, f"{filename}.png")
                if self.save_opencv_image(region_image, output_path):
                    saved_count += 1

            print(
                f"✅ Página {page_num + 1}: {saved_count}/4 imágenes extraídas con coordenadas reales"
            )
            return saved_count == 4

        except Exception as e:
            print(f"❌ Error procesando página {page_num + 1}: {e}")
            return False

    def extract_images_from_pdf(self, pdf_path: str, output_dir: str) -> bool:
        """
        Extrae imágenes de todas las páginas de un PDF usando método avanzado

        Args:
            pdf_path: Ruta del PDF
            output_dir: Directorio de salida

        Returns:
            bool: True si se procesó exitosamente
        """
        try:
            print(f"🖼️ Extrayendo imágenes con método avanzado de: {pdf_path}")

            # Verificar dependencias
            if not self.check_dependencies():
                return False

            # Obtener número total de páginas del PDF
            try:
                # Obtener el número total de páginas usando PyMuPDF
                import pymupdf

                pdf_doc = pymupdf.open(pdf_path)
                total_pages = len(pdf_doc)
                pdf_doc.close()

                print(f"📖 PDF tiene {total_pages} páginas")

            except Exception as e:
                print(f"❌ Error obteniendo número de páginas: {e}")
                return False

            # Procesar cada página
            successful_pages = 0

            for page_num in range(total_pages):
                try:
                    # Intentar procesar la página
                    if self.extract_images_from_page(pdf_path, page_num, output_dir):
                        successful_pages += 1
                    else:
                        print(
                            f"⚠️ Página {page_num + 1} no se pudo procesar correctamente"
                        )
                except Exception as e:
                    print(f"❌ Error procesando página {page_num + 1}: {e}")
                    continue

            print(
                f"✅ Extracción avanzada completada: {successful_pages}/{total_pages} páginas procesadas"
            )
            return successful_pages > 0

        except Exception as e:
            print(f"❌ Error en extracción avanzada: {e}")
            return False
