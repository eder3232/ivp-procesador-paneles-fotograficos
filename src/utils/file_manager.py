"""
Gestor de Archivos
Maneja operaciones de archivos y limpieza de archivos temporales
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional


class FileManager:
    """
    Clase para gestionar archivos y directorios del proyecto
    """
    
    def __init__(self):
        self.temp_extensions = ['.pdf', '.jpg', '.png', '.jpeg']
    
    def create_directory(self, directory_path: str) -> bool:
        """
        Crea un directorio si no existe
        
        Args:
            directory_path: Ruta del directorio a crear
            
        Returns:
            bool: True si se creó exitosamente o ya existía
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Error creando directorio {directory_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Verifica si un archivo existe
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            bool: True si el archivo existe
        """
        return os.path.isfile(file_path)
    
    def directory_exists(self, directory_path: str) -> bool:
        """
        Verifica si un directorio existe
        
        Args:
            directory_path: Ruta del directorio
            
        Returns:
            bool: True si el directorio existe
        """
        return os.path.isdir(directory_path)
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Obtiene el tamaño de un archivo en bytes
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Optional[int]: Tamaño del archivo en bytes o None si no existe
        """
        try:
            if self.file_exists(file_path):
                return os.path.getsize(file_path)
            return None
        except Exception as e:
            print(f"❌ Error obteniendo tamaño de archivo {file_path}: {e}")
            return None
    
    def list_files_in_directory(self, directory_path: str, extensions: List[str] = None) -> List[str]:
        """
        Lista archivos en un directorio con extensiones específicas
        
        Args:
            directory_path: Ruta del directorio
            extensions: Lista de extensiones a filtrar (ej: ['.pdf', '.jpg'])
            
        Returns:
            List[str]: Lista de rutas de archivos encontrados
        """
        try:
            if not self.directory_exists(directory_path):
                return []
            
            files = []
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    if extensions is None:
                        files.append(file_path)
                    else:
                        file_ext = Path(file).suffix.lower()
                        if file_ext in extensions:
                            files.append(file_path)
            
            return files
        except Exception as e:
            print(f"❌ Error listando archivos en {directory_path}: {e}")
            return []
    
    def cleanup_temp_files(self, temp_directory: str) -> bool:
        """
        Limpia archivos temporales de un directorio
        
        Args:
            temp_directory: Ruta del directorio temporal
            
        Returns:
            bool: True si se limpió exitosamente
        """
        try:
            if not self.directory_exists(temp_directory):
                print(f"⚠️ Directorio temporal {temp_directory} no existe")
                return True
            
            files_to_delete = self.list_files_in_directory(temp_directory, self.temp_extensions)
            
            if not files_to_delete:
                print(f"📁 No hay archivos temporales para limpiar en {temp_directory}")
                return True
            
            deleted_count = 0
            for file_path in files_to_delete:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"🗑️ Eliminado: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"⚠️ Error eliminando {file_path}: {e}")
            
            print(f"✅ Limpieza completada: {deleted_count} archivos eliminados")
            return True
            
        except Exception as e:
            print(f"❌ Error durante la limpieza de archivos temporales: {e}")
            return False
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copia un archivo de una ubicación a otra
        
        Args:
            source_path: Ruta del archivo origen
            destination_path: Ruta del archivo destino
            
        Returns:
            bool: True si se copió exitosamente
        """
        try:
            if not self.file_exists(source_path):
                print(f"❌ Archivo origen no existe: {source_path}")
                return False
            
            # Crear directorio destino si no existe
            dest_dir = os.path.dirname(destination_path)
            if dest_dir and not self.directory_exists(dest_dir):
                self.create_directory(dest_dir)
            
            shutil.copy2(source_path, destination_path)
            print(f"📋 Copiado: {os.path.basename(source_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error copiando archivo: {e}")
            return False
    
    def move_file(self, source_path: str, destination_path: str) -> bool:
        """
        Mueve un archivo de una ubicación a otra
        
        Args:
            source_path: Ruta del archivo origen
            destination_path: Ruta del archivo destino
            
        Returns:
            bool: True si se movió exitosamente
        """
        try:
            if not self.file_exists(source_path):
                print(f"❌ Archivo origen no existe: {source_path}")
                return False
            
            # Crear directorio destino si no existe
            dest_dir = os.path.dirname(destination_path)
            if dest_dir and not self.directory_exists(dest_dir):
                self.create_directory(dest_dir)
            
            shutil.move(source_path, destination_path)
            print(f"📦 Movido: {os.path.basename(source_path)}")
            return True
            
        except Exception as e:
            print(f"❌ Error moviendo archivo: {e}")
            return False 