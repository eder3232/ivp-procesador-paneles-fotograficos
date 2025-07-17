"""
Generador de PDFs de Paneles Fotográficos
Genera PDFs A4 horizontal por actividad basado en la estructura organizada
"""

import os
import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Image as RLImage,
    Spacer,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image as PILImage


class PDFPanelGenerator:
    """
    Generador de PDFs de paneles fotográficos por actividad
    """

    def __init__(self, config_path: str = "config/pdf_settings.yaml"):
        """
        Inicializa el generador

        Args:
            config_path: Ruta al archivo de configuración
        """
        self.config = self._load_config(config_path)
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo YAML

        Args:
            config_path: Ruta al archivo de configuración

        Returns:
            Dict con la configuración
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            return {}

    def _setup_styles(self):
        """
        Configura los estilos para el PDF
        """
        self.title_style = self.styles["Heading2"]
        self.meta_style = self.styles["Normal"]
        self.meta_style.fontSize = 10
        self.label_style = self.styles["Normal"].clone("label_style")
        self.label_style.fontSize = 9
        self.label_style.alignment = 0  # izquierda

    def _get_mes_string(self, numero: int) -> str:
        """
        Convierte número de mes a string

        Args:
            numero: Número del mes (1-12)

        Returns:
            str: Nombre del mes
        """
        meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        if 1 <= numero <= 12:
            return meses[numero - 1].capitalize()
        else:
            return "Mes inválido"

    def _find_image_file(self, folder: Path, base_name: str) -> Optional[Path]:
        """
        Busca un archivo de imagen en la carpeta

        Args:
            folder: Carpeta donde buscar
            base_name: Nombre base del archivo

        Returns:
            Optional[Path]: Ruta del archivo encontrado o None
        """
        supported_ext = self.config.get("pdf_generation", {}).get(
            "supported_extensions", ["png"]
        )

        for ext in supported_ext:
            path = folder / f"{base_name}.{ext}"
            if path.exists():
                return path
        return None

    def _build_scaled_image(
        self, img_path: Path, cell_w: float, cell_h: float
    ) -> RLImage:
        """
        Construye una imagen escalada para ajustarse a las dimensiones de la celda

        Args:
            img_path: Ruta de la imagen
            cell_w: Ancho de la celda
            cell_h: Alto de la celda

        Returns:
            RLImage: Imagen escalada
        """
        padding = self.config.get("pdf_generation", {}).get("padding", 5)

        with PILImage.open(img_path) as img:
            iw, ih = img.size

        max_w = cell_w - 2 * padding
        max_h = cell_h - 2 * padding
        scale = min(max_w / iw, max_h / ih)
        new_w, new_h = iw * scale, ih * scale

        return RLImage(str(img_path), width=new_w, height=new_h)

    def _read_analysis_json(self, folder: Path) -> Optional[Dict[str, Any]]:
        """
        Lee el archivo analysis.json de una carpeta

        Args:
            folder: Carpeta donde buscar el archivo

        Returns:
            Optional[Dict]: Contenido del JSON o None
        """
        analysis_file = folder / "analysis.json"

        if not analysis_file.exists():
            return None

        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error leyendo {analysis_file}: {e}")
            return None

    def _get_progressives_string(self, analysis_data: Dict[str, Any]) -> str:
        """
        Genera el string de progresivas desde el JSON

        Args:
            analysis_data: Datos del análisis

        Returns:
            str: String de progresivas formateado
        """
        progresivas = analysis_data.get("progresivas", {})

        if progresivas.get("is_range", False):
            desde = progresivas.get("desde", 0)
            hasta = progresivas.get("hasta", 0)
            return f"{desde} m - {hasta} m"
        else:
            desde = progresivas.get("desde", 0)
            return f"{desde} m"

    def _create_panel_pdf(self, activity_folder: Path, output_path: Path) -> bool:
        """
        Crea un PDF de panel fotográfico para una actividad

        Args:
            activity_folder: Carpeta de la actividad (contiene carpeta "1")
            output_path: Ruta de salida del PDF

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            # Buscar la carpeta "1" (primer set)
            first_set_folder = activity_folder / "1"
            if not first_set_folder.exists():
                print(f"❌ No se encontró carpeta '1' en {activity_folder}")
                return False

            # Leer análisis JSON
            analysis_data = self._read_analysis_json(first_set_folder)
            if not analysis_data:
                print(f"❌ No se encontró analysis.json en {first_set_folder}")
                return False

            # Buscar imágenes
            photo_keys = self.config.get("pdf_generation", {}).get(
                "photo_keys", ["before", "during1", "during2", "after"]
            )
            img_paths = {}

            for key in photo_keys:
                img_path = self._find_image_file(first_set_folder, key)
                if not img_path:
                    print(f"❌ No se encontró imagen {key} en {first_set_folder}")
                    return False
                img_paths[key] = img_path

            # Configuración del PDF
            pdf_config = self.config.get("pdf_generation", {})
            page_w, page_h = landscape(A4)
            margin = pdf_config.get("margin", 20)
            table_scale = pdf_config.get("table_scale", 0.72)
            caption_height = pdf_config.get("caption_height", 12)

            # Área útil
            total_w = page_w - 2 * margin
            total_h = page_h - 2 * margin

            # Tamaño del grid
            grid_w = total_w * table_scale
            grid_h = total_h * table_scale

            # Proporciones para layout 2×2
            sep_w = grid_w * 0.015
            sep_h = grid_h * 0.015
            img_w = (grid_w - sep_w) / 2
            img_h = (grid_h - sep_h) / 2 - caption_height

            # Crear documento
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=(page_w, page_h),
                leftMargin=margin,
                rightMargin=margin,
                topMargin=margin,
                bottomMargin=margin,
            )

            # Construir elementos
            elements = []

            # Título
            elements.append(
                Paragraph(
                    pdf_config.get("page_title", "Anexo VI Panel fotográfico"),
                    self.title_style,
                )
            )
            elements.append(Spacer(1, 8))

            # Metadatos
            elements.append(
                Paragraph(
                    f"Unidad ejecutora: {pdf_config.get('unidad_ejecutora', 'N/A')}",
                    self.meta_style,
                )
            )
            elements.append(
                Paragraph(
                    f"Tramo: {pdf_config.get('tramo_full_name', 'N/A')}",
                    self.meta_style,
                )
            )

            # Actividad
            actividad = analysis_data.get("actividad", "N/A")
            elements.append(Paragraph(f"Actividad: {actividad}", self.meta_style))

            # Progresivas
            progresivas_str = self._get_progressives_string(analysis_data)
            elements.append(
                Paragraph(f"Progresiva: {progresivas_str}", self.meta_style)
            )

            # Mes
            mes_num = pdf_config.get("mes_ejecutado", 1)
            mes_string = self._get_mes_string(mes_num)
            elements.append(Paragraph(f"Mes ejecutado: {mes_string}", self.meta_style))
            elements.append(Spacer(1, 12))

            # Construir imágenes escaladas
            photo_labels = pdf_config.get(
                "photo_labels",
                [
                    " 01 (antes).-",
                    " 02 (durante).-",
                    " 03 (durante).-",
                    " 04 (después).-",
                ],
            )

            img_flows = [
                self._build_scaled_image(img_paths[photo_keys[0]], img_w, img_h),
                self._build_scaled_image(img_paths[photo_keys[1]], img_w, img_h),
                self._build_scaled_image(img_paths[photo_keys[2]], img_w, img_h),
                self._build_scaled_image(img_paths[photo_keys[3]], img_w, img_h),
            ]

            labels = [
                Paragraph(f"Fotografía{photo_labels[0]}", self.label_style),
                Paragraph(f"Fotografía{photo_labels[1]}", self.label_style),
                Paragraph(f"Fotografía{photo_labels[2]}", self.label_style),
                Paragraph(f"Fotografía{photo_labels[3]}", self.label_style),
            ]

            # Construir tabla 2×2
            data = [
                [img_flows[0], "", img_flows[1]],
                [labels[0], "", labels[1]],
                ["", "", ""],  # separación
                [img_flows[2], "", img_flows[3]],
                [labels[2], "", labels[3]],
            ]

            colWidths = [img_w, sep_w, img_w]
            rowHeights = [img_h, caption_height, sep_h, img_h, caption_height]

            main_table = Table(
                data, colWidths=colWidths, rowHeights=rowHeights, hAlign="CENTER"
            )

            # Estilos de la tabla
            style_cmds = []
            # Bordes para imágenes y labels
            for r in [0, 1, 3, 4]:
                for c in [0, 2]:
                    style_cmds.append(("BOX", (c, r), (c, r), 1, colors.black))
            # Centrado vertical/horizontal
            for r in [0, 3]:
                for c in [0, 2]:
                    style_cmds.append(("VALIGN", (c, r), (c, r), "MIDDLE"))
                    style_cmds.append(("ALIGN", (c, r), (c, r), "CENTER"))
            for r in [1, 4]:
                for c in [0, 2]:
                    style_cmds.append(("VALIGN", (c, r), (c, r), "MIDDLE"))
                    style_cmds.append(("ALIGN", (c, r), (c, r), "LEFT"))

            main_table.setStyle(TableStyle(style_cmds))
            elements.append(main_table)

            # Generar PDF
            doc.build(elements)
            return True

        except Exception as e:
            print(f"❌ Error creando PDF para {activity_folder}: {e}")
            return False

    def generate_pdfs(self, organized_dir: str = "output/organized") -> bool:
        """
        Genera PDFs para todas las actividades con al menos un set de datos

        Args:
            organized_dir: Directorio con la estructura organizada

        Returns:
            bool: True si se generaron exitosamente
        """
        try:
            print("📄 Iniciando generación de PDFs...")

            organized_path = Path(organized_dir)
            if not organized_path.exists():
                print(f"❌ No se encontró el directorio: {organized_dir}")
                return False

            # Crear directorio de salida
            output_dir = Path(
                self.config.get("pdf_generation", {}).get(
                    "output_dir", "output/pdf_panels"
                )
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            generated_count = 0

            # Procesar cada carpeta de actividad
            for activity_folder in organized_path.iterdir():
                if not activity_folder.is_dir():
                    continue

                # Verificar que existe carpeta "1" (primer set)
                first_set_folder = activity_folder / "1"
                if not first_set_folder.exists():
                    print(f"⚠️ No se encontró primer set para: {activity_folder.name}")
                    continue

                # Generar nombre del archivo PDF (sin espacios)
                activity_name = activity_folder.name.replace(" ", "_").replace("-", "_")
                pdf_filename = f"{activity_name}.pdf"
                output_path = output_dir / pdf_filename

                print(f"📄 Generando PDF para: {activity_folder.name}")

                if self._create_panel_pdf(activity_folder, output_path):
                    print(f"✅ Generado: {pdf_filename}")
                    generated_count += 1
                else:
                    print(f"❌ Error generando PDF para: {activity_folder.name}")

            print(f"🎉 Generación completada: {generated_count} PDFs creados")
            return True

        except Exception as e:
            print(f"❌ Error durante la generación: {e}")
            return False


def main():
    """
    Función principal para generar PDFs
    """
    parser = argparse.ArgumentParser(description="Generar PDFs de paneles fotográficos")
    parser.add_argument(
        "--config",
        default="config/pdf_settings.yaml",
        help="Ruta al archivo de configuración",
    )
    parser.add_argument(
        "--input",
        default="output/organized",
        help="Directorio con estructura organizada",
    )

    args = parser.parse_args()

    generator = PDFPanelGenerator(args.config)
    success = generator.generate_pdfs(args.input)

    if success:
        print("✅ Proceso completado exitosamente!")
    else:
        print("❌ Error en el proceso")
        exit(1)


if __name__ == "__main__":
    main()
