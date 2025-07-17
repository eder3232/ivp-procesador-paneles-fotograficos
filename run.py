#!/usr/bin/env python3
"""
Script para ejecutar el proyecto con configuración de cache optimizada
"""

import os
import sys
from pathlib import Path


def setup_environment():
    """Configura las variables de entorno para evitar archivos de cache"""
    # Configurar Python para no escribir archivos .pyc
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

    # Configurar directorio de cache personalizado
    cache_dir = Path(".cache/python")
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ["PYTHONPYCACHEPREFIX"] = str(cache_dir.absolute())

    print(f"🔧 Cache configurado en: {cache_dir.absolute()}")


def main():
    """Ejecuta el proyecto principal"""
    print("🚀 Ejecutando Procesador de Paneles Fotográficos...")

    # Configurar entorno
    setup_environment()

    # Agregar src al path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    # Importar y ejecutar el main
    try:
        from main import main as project_main

        project_main()
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   uv sync")
        print("   Y ejecuta con: uv run python run.py")
    except Exception as e:
        print(f"❌ Error ejecutando el proyecto: {e}")


if __name__ == "__main__":
    main()
