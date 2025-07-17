#!/usr/bin/env python3
"""
Script para limpiar archivos de cache y configurar el entorno
"""

import os
import shutil
import subprocess
from pathlib import Path


def clean_pycache():
    """Limpia todos los archivos __pycache__ del proyecto"""
    print("🧹 Limpiando archivos de cache...")

    # Buscar y eliminar __pycache__
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                print(f"🗑️ Eliminado: {cache_path}")
            except Exception as e:
                print(f"⚠️ Error eliminando {cache_path}: {e}")

    # Eliminar archivos .pyc
    for pyc_file in Path(".").rglob("*.pyc"):
        try:
            pyc_file.unlink()
            print(f"🗑️ Eliminado: {pyc_file}")
        except Exception as e:
            print(f"⚠️ Error eliminando {pyc_file}: {e}")

    print("✅ Limpieza completada")


def setup_cache_dir():
    """Configura el directorio de cache fuera del proyecto"""
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)

    # Crear subdirectorios para diferentes tipos de cache
    (cache_dir / "mypy").mkdir(exist_ok=True)
    (cache_dir / "pytest").mkdir(exist_ok=True)
    (cache_dir / "python").mkdir(exist_ok=True)

    print(f"📁 Directorio de cache configurado: {cache_dir.absolute()}")


def set_python_cache_env():
    """Configura variables de entorno para el cache de Python"""
    env_vars = {
        "PYTHONPYCACHEPREFIX": ".cache/python",
        "PYTHONDONTWRITEBYTECODE": "1",  # Evita crear .pyc
    }

    print("🔧 Configurando variables de entorno para cache:")
    for var, value in env_vars.items():
        print(f"  {var}={value}")

    # Crear archivo .env si no existe
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            for var, value in env_vars.items():
                f.write(f"{var}={value}\n")
        print("📝 Archivo .env creado")


def main():
    """Función principal"""
    print("🚀 Configurando entorno de desarrollo...")

    # Limpiar cache existente
    clean_pycache()

    # Configurar directorio de cache
    setup_cache_dir()

    # Configurar variables de entorno
    set_python_cache_env()

    print("\n✅ Configuración completada!")
    print("\n💡 Para usar esta configuración:")
    print("  1. Ejecuta: source .env (Linux/Mac) o .env (Windows)")
    print("  2. O agrega las variables a tu shell")
    print("  3. Los archivos de cache se generarán en .cache/")


if __name__ == "__main__":
    main()
