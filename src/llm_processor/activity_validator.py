"""
Validador de Actividades para LLM
Maneja el mapeo de códigos a nombres y validación de respuestas
"""

from typing import Dict, Optional, Any
from pydantic import BaseModel, Field, validator
import json


class Progresivas(BaseModel):
    """Modelo para validar progresivas"""

    is_range: bool = Field(..., description="Indica si es un rango de progresivas")
    desde: int = Field(..., description="Progresiva inicial en metros")
    hasta: int = Field(..., description="Progresiva final en metros (0 si no es rango)")


class LLMResponse(BaseModel):
    """Modelo para validar respuesta del LLM"""

    actividad: str = Field(..., description="Código de actividad (ej: MR203)")
    progresivas: Progresivas = Field(..., description="Información de progresivas")

    @validator("actividad")
    def validate_actividad(cls, v):
        """Valida que la actividad sea un código válido"""
        valid_codes = [
            "MR101",
            "MR102",
            "MR103",
            "MR104",
            "MR201",
            "MR202",
            "MR203",
            "MR204",
            "MR205",
            "MR206",
            "MR301",
            "MR401",
            "MR501",
            "MR601",
            "MR701",
            "MR702",
            "NO_ACTIVIDAD",
        ]
        if v not in valid_codes:
            raise ValueError(
                f"Actividad '{v}' no es un código válido. Códigos válidos: {valid_codes}"
            )
        return v


class ActivityMapper:
    """
    Mapea códigos de actividad a nombres completos
    """

    # Diccionario de actividades
    ACTIVIDADES_MAPPING = {
        "MR101": "Limpieza de Calzada",
        "MR102": "Bacheo",
        "MR103": "Desquinche",
        "MR104": "Remoción de Derrumbes",
        "MR201": "Limpieza de Cunetas",
        "MR202": "Limpieza de Alcantarillas",
        "MR203": "Limpieza de Badén",
        "MR204": "Limpieza de Zanjas de Coronación",
        "MR205": "Limpieza de Pontones",
        "MR206": "Encauzamiento Pequeños cursos Agua",
        "MR301": "Roce y limpieza",
        "MR401": "Conservación de Señales",
        "MR501": "Reforestación",
        "MR601": "Vigilancia y Control",
        "MR701": "Reparación de muros secos",
        "MR702": "Reparación de Pontones",
    }

    @classmethod
    def get_activity_name(cls, code: str) -> str:
        """
        Obtiene el nombre completo de una actividad por su código

        Args:
            code: Código de actividad (ej: MR203)

        Returns:
            str: Nombre completo de la actividad
        """
        if code == "NO_ACTIVIDAD":
            return "No se encontró actividad específica"

        return cls.ACTIVIDADES_MAPPING.get(code, f"Actividad desconocida ({code})")

    @classmethod
    def get_full_activity_string(cls, code: str) -> str:
        """
        Obtiene la cadena completa de actividad (código + nombre)

        Args:
            code: Código de actividad (ej: MR203)

        Returns:
            str: Código + nombre (ej: MR203-Limpieza de Badén)
        """
        if code == "NO_ACTIVIDAD":
            return "No se encontró actividad específica"

        name = cls.get_activity_name(code)
        return f"{code}-{name}"

    @classmethod
    def is_valid_code(cls, code: str) -> bool:
        """
        Verifica si un código de actividad es válido

        Args:
            code: Código a verificar

        Returns:
            bool: True si el código es válido
        """
        return code in cls.ACTIVIDADES_MAPPING or code == "NO_ACTIVIDAD"

    @classmethod
    def get_all_codes(cls) -> list:
        """
        Obtiene todos los códigos válidos

        Returns:
            list: Lista de códigos válidos
        """
        return list(cls.ACTIVIDADES_MAPPING.keys()) + ["NO_ACTIVIDAD"]


class ResponseValidator:
    """
    Valida y procesa respuestas del LLM
    """

    @staticmethod
    def validate_response(response_text: str) -> Optional[Dict[str, Any]]:
        """
        Valida una respuesta del LLM

        Args:
            response_text: Respuesta del LLM como texto

        Returns:
            Optional[Dict]: Respuesta validada o None si es inválida
        """
        try:
            # Limpiar la respuesta
            cleaned_response = ResponseValidator._clean_response(response_text)

            # Parsear JSON
            parsed_data = json.loads(cleaned_response)

            # Validar con Pydantic
            validated_response = LLMResponse(**parsed_data)

            # Convertir a diccionario
            result = validated_response.dict()

            # Agregar nombre completo de la actividad
            result["actividad_completa"] = ActivityMapper.get_full_activity_string(
                result["actividad"]
            )

            return result

        except Exception as e:
            print(f"❌ Error validando respuesta: {e}")
            print(f"Respuesta recibida: {response_text}")
            return None

    @staticmethod
    def _clean_response(response: str) -> str:
        """
        Limpia la respuesta del LLM

        Args:
            response: Respuesta del LLM

        Returns:
            str: Respuesta limpia
        """
        # Eliminar markdown si existe
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        return cleaned.strip()

    @staticmethod
    def format_final_response(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatea la respuesta final para guardar

        Args:
            validated_data: Datos validados

        Returns:
            Dict: Respuesta final formateada
        """
        return {
            "actividad": validated_data["actividad_completa"],
            "progresivas": validated_data["progresivas"],
        }
