"""
Procesador de LLM
Procesa archivos markdown con OpenAI y genera JSON estructurado
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import openai
from dotenv import load_dotenv
from .activity_validator import ResponseValidator, ActivityMapper


class LLMProcessor:
    """
    Clase para procesar texto con LLM y extraer información estructurada
    """

    def __init__(self):
        # Cargar variables de entorno
        load_dotenv()

        # Cargar configuraciones
        self.config = self._load_config()
        self.prompts = self._load_prompts()

        # Configurar OpenAI
        self._setup_openai()

    def _load_config(self) -> Dict[str, Any]:
        """
        Carga las configuraciones desde settings.yaml

        Returns:
            Dict con las configuraciones
        """
        try:
            config_path = Path("config/settings.yaml")
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error cargando configuraciones: {e}")
            return {}

    def _load_prompts(self) -> Dict[str, Any]:
        """
        Carga los prompts desde prompts.yaml

        Returns:
            Dict con los prompts
        """
        try:
            prompts_path = Path("config/prompts.yaml")
            with open(prompts_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error cargando prompts: {e}")
            return {}

    def _setup_openai(self):
        """
        Configura la API de OpenAI
        """
        try:
            api_key = os.getenv(
                self.config.get("llm", {}).get("api_key_env", "OPENAI_APIKEY")
            )
            if not api_key:
                raise ValueError(
                    "API key de OpenAI no encontrada en variables de entorno"
                )

            openai.api_key = api_key
            print("✅ OpenAI configurado correctamente")

        except Exception as e:
            print(f"❌ Error configurando OpenAI: {e}")
            raise

    def _get_llm_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración del LLM

        Returns:
            Dict con configuración del LLM
        """
        return self.config.get("llm", {})

    def _get_system_prompt(self) -> str:
        """
        Obtiene el prompt del sistema

        Returns:
            str: Prompt del sistema
        """
        return self.prompts.get("llm_analysis", {}).get("system_prompt", "")

    def _format_prompt(self, text_content: str) -> str:
        """
        Formatea el prompt con el contenido del texto

        Args:
            text_content: Contenido del archivo markdown

        Returns:
            str: Prompt formateado
        """
        system_prompt = self._get_system_prompt()
        return system_prompt.replace("{texto_del_pdf}", text_content)

    def _call_openai(self, prompt: str, model: Optional[str] = None) -> Optional[str]:
        """
        Llama a la API de OpenAI

        Args:
            prompt: Prompt completo para enviar al LLM
            model: Modelo específico a usar (opcional)

        Returns:
            Optional[str]: Respuesta del LLM o None si hay error
        """
        try:
            llm_config = self._get_llm_config()
            api_key = os.getenv(
                self.config.get("llm", {}).get("api_key_env", "OPENAI_APIKEY")
            )
            from openai import OpenAI

            client = OpenAI(api_key=api_key)

            # Usar modelo especificado o el configurado
            model_to_use = model or llm_config.get("model", "gpt-4o-mini")
            print(f"🤖 Usando modelo: {model_to_use}")

            response = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de documentos de ingeniería civil.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=llm_config.get("temperature", 0),
                max_tokens=llm_config.get("max_tokens", 150),
            )

            content = response.choices[0].message.content
            if content is not None:
                return content.strip()
            else:
                return None

        except Exception as e:
            print(f"❌ Error llamando a OpenAI: {e}")
            return None

    def _call_openai_with_retries(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Llama a OpenAI con reintentos y validación

        Args:
            prompt: Prompt para enviar al LLM

        Returns:
            Optional[Dict]: Respuesta validada o None si falla
        """
        llm_config = self._get_llm_config()
        max_retries = llm_config.get("validation", {}).get("max_retries", 3)
        fallback_model = llm_config.get("validation", {}).get(
            "fallback_model", "gpt-3.5-turbo"
        )

        # Intentar con el modelo principal
        for attempt in range(max_retries):
            print(f"🔄 Intento {attempt + 1}/{max_retries}")

            response = self._call_openai(prompt)
            if response:
                # Validar respuesta
                validated = ResponseValidator.validate_response(response)
                if validated:
                    print(f"✅ Respuesta validada exitosamente")
                    return validated

            print(f"⚠️ Intento {attempt + 1} falló, reintentando...")

        # Si falló con el modelo principal, intentar con fallback
        print(f"🔄 Intentando con modelo fallback: {fallback_model}")
        response = self._call_openai(prompt, fallback_model)
        if response:
            validated = ResponseValidator.validate_response(response)
            if validated:
                print(f"✅ Respuesta validada con modelo fallback")
                return validated

        print(f"❌ Todos los intentos fallaron")
        return None

    def process_text_file(self, text_file_path: str) -> Optional[Dict[str, Any]]:
        """
        Procesa un archivo markdown y extrae información estructurada

        Args:
            text_file_path: Ruta del archivo markdown

        Returns:
            Optional[Dict]: Información extraída o None si hay error
        """
        try:
            print(f"🤖 Procesando: {text_file_path}")

            # Leer archivo markdown
            with open(text_file_path, "r", encoding="utf-8") as f:
                text_content = f.read()

            if not text_content.strip():
                print(f"⚠️ Archivo vacío: {text_file_path}")
                return None

            # Formatear prompt
            prompt = self._format_prompt(text_content)

            # Llamar a OpenAI con validación y reintentos
            validated_response = self._call_openai_with_retries(prompt)

            if not validated_response:
                print(
                    f"❌ No se obtuvo respuesta válida de OpenAI para: {text_file_path}"
                )
                return None

            # Formatear respuesta final
            final_response = ResponseValidator.format_final_response(validated_response)

            print(f"✅ Procesado exitosamente: {text_file_path}")
            print(f"   Actividad: {final_response['actividad']}")
            print(f"   Progresivas: {final_response['progresivas']}")

            return final_response

        except Exception as e:
            print(f"❌ Error procesando archivo {text_file_path}: {e}")
            return None

    def process_all_text_files(self, base_dir: str) -> Dict[str, Dict[str, Any]]:
        """
        Procesa todos los archivos markdown en el directorio base

        Args:
            base_dir: Directorio base con archivos markdown

        Returns:
            Dict: Resultados por página
        """
        try:
            print(f"🤖 Procesando todos los archivos markdown en: {base_dir}")

            results = {}
            base_path = Path(base_dir)

            # Buscar archivos text.md en subdirectorios
            for text_file in base_path.rglob("text.md"):
                page_name = text_file.parent.name  # page_1, page_2, etc.

                # Procesar archivo
                result = self.process_text_file(str(text_file))

                if result:
                    results[page_name] = result
                else:
                    print(f"⚠️ No se pudo procesar: {page_name}")

            print(f"✅ Procesamiento completado: {len(results)} archivos procesados")
            return results

        except Exception as e:
            print(f"❌ Error procesando archivos: {e}")
            return {}

    def save_results(self, results: Dict[str, Dict[str, Any]], base_dir: str) -> bool:
        """
        Guarda los resultados en archivos JSON dentro de cada carpeta de página

        Args:
            results: Resultados del procesamiento
            base_dir: Directorio base donde están las carpetas de páginas

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            # Guardar resultados por página en sus respectivas carpetas
            for page_name, data in results.items():
                # Construir ruta de la carpeta de la página
                page_dir = os.path.join(base_dir, page_name)

                # Crear directorio si no existe
                os.makedirs(page_dir, exist_ok=True)

                # Guardar archivo JSON en la carpeta de la página
                output_file = os.path.join(page_dir, "analysis.json")

                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                print(f"💾 Guardado: {output_file}")

            # Guardar resumen general en el directorio base
            summary_file = os.path.join(base_dir, "summary.json")
            summary = {
                "total_pages": len(results),
                "pages_processed": list(results.keys()),
                "results": results,
            }

            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            print(f"💾 Resumen guardado: {summary_file}")
            return True

        except Exception as e:
            print(f"❌ Error guardando resultados: {e}")
            return False
