"""
Organizador de Output
Reorganiza el output basado en las actividades encontradas en los JSON
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional


class OutputOrganizer:
    """
    Clase para reorganizar el output basado en actividades
    """

    # Lista de actividades válidas
    VALID_ACTIVITIES = [
        "MR101-Limpieza de Calzada",
        "MR102-Bacheo",
        "MR103-Desquinche",
        "MR104-Remoción de Derrumbes",
        "MR201-Limpieza de Cunetas",
        "MR202-Limpieza de Alcantarillas",
        "MR203-Limpieza de Badén",
        "MR204-Limpieza de Zanjas de Coronación",
        "MR205-Limpieza de Pontones",
        "MR206-Encauzamiento Pequeños cursos Agua",
        "MR301-Roce y limpieza",
        "MR401-Conservación de Señales",
        "MR501-Reforestación",
        "MR601-Vigilancia y Control",
        "MR701-Reparación de muros secos",
        "MR702-Reparación de Pontones",
    ]

    def __init__(
        self, source_dir: str = "output/images", target_dir: str = "output/organized"
    ):
        """
        Inicializa el organizador

        Args:
            source_dir: Directorio fuente con las páginas originales
            target_dir: Directorio destino para la organización
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.organization_stats = {
            "total_pages_processed": 0,
            "activities_found": {},
            "organization_stats": {
                "total_activity_folders": 0,
                "total_sets_organized": 0,
            },
        }

    def _is_valid_activity(self, activity: str) -> bool:
        """
        Verifica si una actividad es válida

        Args:
            activity: Nombre de la actividad

        Returns:
            bool: True si es válida, False en caso contrario
        """
        return activity in self.VALID_ACTIVITIES

    def _get_activity_folder_name(self, activity: str) -> str:
        """
        Obtiene el nombre de la carpeta para una actividad

        Args:
            activity: Nombre de la actividad

        Returns:
            str: Nombre de la carpeta
        """
        if self._is_valid_activity(activity):
            return activity
        else:
            return "actividades_no_reconocidas"

    def _read_analysis_json(self, page_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Lee el archivo analysis.json de una página

        Args:
            page_dir: Directorio de la página

        Returns:
            Optional[Dict]: Contenido del JSON o None si no existe
        """
        analysis_file = page_dir / "analysis.json"

        if not analysis_file.exists():
            return None

        try:
            with open(analysis_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error leyendo {analysis_file}: {e}")
            return None

    def _copy_page_content(self, source_page: Path, target_folder: Path) -> bool:
        """
        Copia todo el contenido de una página a la carpeta destino

        Args:
            source_page: Directorio fuente de la página
            target_folder: Directorio destino

        Returns:
            bool: True si se copió exitosamente
        """
        try:
            # Crear directorio destino si no existe
            target_folder.mkdir(parents=True, exist_ok=True)

            # Copiar todos los archivos de la página
            for file_path in source_page.iterdir():
                if file_path.is_file():
                    shutil.copy2(file_path, target_folder / file_path.name)

            print(f"📁 Copiado: {source_page.name} → {target_folder}")
            return True

        except Exception as e:
            print(f"❌ Error copiando {source_page}: {e}")
            return False

    def _organize_pages(self) -> Dict[str, List[Path]]:
        """
        Organiza las páginas por actividad

        Returns:
            Dict: Actividades con sus páginas correspondientes
        """
        organized_pages = {}

        # Buscar todas las carpetas de páginas
        for page_dir in self.source_dir.iterdir():
            if not page_dir.is_dir() or not page_dir.name.startswith("page_"):
                continue

            # Leer el JSON de análisis
            analysis_data = self._read_analysis_json(page_dir)

            if not analysis_data or "actividad" not in analysis_data:
                print(f"⚠️ No se encontró actividad en: {page_dir.name}")
                continue

            activity = analysis_data["actividad"]
            folder_name = self._get_activity_folder_name(activity)

            # Agrupar por actividad
            if folder_name not in organized_pages:
                organized_pages[folder_name] = []

            organized_pages[folder_name].append(page_dir)

            # Actualizar estadísticas
            if folder_name not in self.organization_stats["activities_found"]:
                self.organization_stats["activities_found"][folder_name] = 0
            self.organization_stats["activities_found"][folder_name] += 1
            self.organization_stats["total_pages_processed"] += 1

        return organized_pages

    def _create_organized_structure(
        self, organized_pages: Dict[str, List[Path]]
    ) -> bool:
        """
        Crea la estructura organizada

        Args:
            organized_pages: Páginas organizadas por actividad

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            total_sets = 0

            for activity_folder, pages in organized_pages.items():
                if not pages:  # No crear carpetas vacías
                    continue

                # Crear carpeta de actividad
                activity_dir = self.target_dir / activity_folder
                activity_dir.mkdir(parents=True, exist_ok=True)

                print(f"📂 Creando carpeta: {activity_folder}")

                # Crear carpetas numeradas para cada set
                for i, page_dir in enumerate(pages, 1):
                    set_folder = activity_dir / str(i)

                    if self._copy_page_content(page_dir, set_folder):
                        total_sets += 1

                self.organization_stats["organization_stats"][
                    "total_activity_folders"
                ] += 1

            self.organization_stats["organization_stats"][
                "total_sets_organized"
            ] = total_sets
            return True

        except Exception as e:
            print(f"❌ Error creando estructura organizada: {e}")
            return False

    def _save_summary(self) -> bool:
        """
        Guarda el archivo de resumen

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            summary_file = self.target_dir / "summary.json"

            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(self.organization_stats, f, indent=2, ensure_ascii=False)

            print(f"💾 Resumen guardado: {summary_file}")
            return True

        except Exception as e:
            print(f"❌ Error guardando resumen: {e}")
            return False

    def organize_output(self) -> bool:
        """
        Organiza el output completo

        Returns:
            bool: True si se organizó exitosamente
        """
        try:
            print("🔄 Iniciando reorganización del output...")

            # Verificar que existe el directorio fuente
            if not self.source_dir.exists():
                print(f"❌ No se encontró el directorio fuente: {self.source_dir}")
                return False

            # Organizar páginas por actividad
            organized_pages = self._organize_pages()

            if not organized_pages:
                print("❌ No se encontraron páginas para organizar")
                return False

            # Crear estructura organizada
            if not self._create_organized_structure(organized_pages):
                return False

            # Guardar resumen
            if not self._save_summary():
                return False

            print("✅ Reorganización completada exitosamente!")
            return True

        except Exception as e:
            print(f"❌ Error durante la reorganización: {e}")
            return False

    def get_organization_stats(self) -> Dict[str, Any]:
        """
        Obtiene las estadísticas de organización

        Returns:
            Dict: Estadísticas de la organización
        """
        return self.organization_stats.copy()
