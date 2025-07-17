"""
Unificador de PDFs
Combina todos los PDFs generados en un único archivo
"""

import os
from pathlib import Path
from typing import List, Optional
from PyPDF2 import PdfMerger


class PDFUnifier:
    """
    Clase para unificar múltiples PDFs en uno solo
    """

    def __init__(
        self, input_dir: str = "output/pdf_panels", output_dir: str = "output/unified"
    ):
        """
        Inicializa el unificador

        Args:
            input_dir: Directorio con los PDFs individuales
            output_dir: Directorio de salida para el PDF unificado
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

    def _get_pdf_files(self) -> List[Path]:
        """
        Obtiene la lista de archivos PDF en el directorio de entrada

        Returns:
            List[Path]: Lista de archivos PDF encontrados
        """
        pdf_files = []

        if not self.input_dir.exists():
            print(f"❌ No se encontró el directorio: {self.input_dir}")
            return pdf_files

        # Buscar archivos PDF
        for file_path in self.input_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == ".pdf":
                pdf_files.append(file_path)

        # Ordenar por nombre para mantener consistencia
        pdf_files.sort(key=lambda x: x.name)

        return pdf_files

    def _create_output_directory(self) -> bool:
        """
        Crea el directorio de salida si no existe

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Error creando directorio de salida: {e}")
            return False

    def unify_pdfs(
        self, output_filename: str = "paneles_fotograficos_unificados.pdf"
    ) -> bool:
        """
        Unifica todos los PDFs en un solo archivo

        Args:
            output_filename: Nombre del archivo de salida

        Returns:
            bool: True si se unificó exitosamente
        """
        try:
            print("📄 Iniciando unificación de PDFs...")

            # Obtener archivos PDF
            pdf_files = self._get_pdf_files()

            if not pdf_files:
                print("❌ No se encontraron archivos PDF para unificar")
                return False

            print(f"📋 Encontrados {len(pdf_files)} archivos PDF:")
            for pdf_file in pdf_files:
                print(f"   - {pdf_file.name}")

            # Crear directorio de salida
            if not self._create_output_directory():
                return False

            # Crear el merger
            merger = PdfMerger()

            # Agregar cada PDF al merger
            for pdf_file in pdf_files:
                try:
                    print(f"📄 Agregando: {pdf_file.name}")
                    merger.append(str(pdf_file))
                except Exception as e:
                    print(f"❌ Error agregando {pdf_file.name}: {e}")
                    continue

            # Guardar el PDF unificado
            output_path = self.output_dir / output_filename

            print(f"💾 Guardando PDF unificado: {output_path}")
            merger.write(str(output_path))
            merger.close()

            print(f"✅ PDF unificado guardado exitosamente: {output_path}")
            print(f"📊 Total de páginas: {len(pdf_files)}")

            return True

        except Exception as e:
            print(f"❌ Error durante la unificación: {e}")
            return False

    def get_unified_pdf_path(
        self, output_filename: str = "paneles_fotograficos_unificados.pdf"
    ) -> Path:
        """
        Obtiene la ruta del PDF unificado

        Args:
            output_filename: Nombre del archivo de salida

        Returns:
            Path: Ruta del PDF unificado
        """
        return self.output_dir / output_filename


def main():
    """
    Función principal para unificar PDFs
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Unificar PDFs de paneles fotográficos"
    )
    parser.add_argument(
        "--input", default="output/pdf_panels", help="Directorio con PDFs individuales"
    )
    parser.add_argument(
        "--output", default="output/unified", help="Directorio de salida"
    )
    parser.add_argument(
        "--filename",
        default="paneles_fotograficos_unificados.pdf",
        help="Nombre del archivo de salida",
    )

    args = parser.parse_args()

    unifier = PDFUnifier(args.input, args.output)
    success = unifier.unify_pdfs(args.filename)

    if success:
        print("✅ Unificación completada exitosamente!")
    else:
        print("❌ Error en la unificación")
        exit(1)


if __name__ == "__main__":
    main()
