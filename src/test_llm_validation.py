"""
Test del LLM Processor con Validación
Prueba la nueva implementación con validación y reintentos
"""

import os
import sys
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent))

from llm_processor.llm_processor import LLMProcessor
from llm_processor.activity_validator import ActivityMapper, ResponseValidator


def test_activity_mapper():
    """
    Prueba el mapeador de actividades
    """
    print("🔍 Probando ActivityMapper...")

    # Probar mapeo de códigos válidos
    test_codes = ["MR203", "MR301", "MR101", "NO_ACTIVIDAD"]

    for code in test_codes:
        name = ActivityMapper.get_activity_name(code)
        full_string = ActivityMapper.get_full_activity_string(code)
        is_valid = ActivityMapper.is_valid_code(code)

        print(f"   {code} -> {name}")
        print(f"   Completo: {full_string}")
        print(f"   Válido: {is_valid}")
        print()

    # Probar código inválido
    invalid_code = "MR999"
    is_valid = ActivityMapper.is_valid_code(invalid_code)
    print(f"   {invalid_code} -> Válido: {is_valid}")

    print("✅ ActivityMapper probado exitosamente")


def test_response_validator():
    """
    Prueba el validador de respuestas
    """
    print("\n🔍 Probando ResponseValidator...")

    # Respuesta válida
    valid_response = """
    {
      "actividad": "MR203",
      "progresivas": {
        "is_range": true,
        "desde": 900,
        "hasta": 1800
      }
    }
    """

    result = ResponseValidator.validate_response(valid_response)
    if result:
        print(f"   ✅ Respuesta válida procesada")
        print(f"   Actividad: {result['actividad']}")
        print(f"   Actividad completa: {result['actividad_completa']}")
        print(f"   Progresivas: {result['progresivas']}")
    else:
        print(f"   ❌ Error validando respuesta válida")

    # Respuesta inválida (código incorrecto)
    invalid_response = """
    {
      "actividad": "MR999",
      "progresivas": {
        "is_range": true,
        "desde": 900,
        "hasta": 1800
      }
    }
    """

    result = ResponseValidator.validate_response(invalid_response)
    if result:
        print(f"   ❌ Respuesta inválida fue aceptada")
    else:
        print(f"   ✅ Respuesta inválida fue rechazada correctamente")

    print("✅ ResponseValidator probado exitosamente")


def test_llm_processor():
    """
    Prueba el procesador LLM con validación
    """
    print("\n🔍 Probando LLMProcessor con validación...")

    try:
        processor = LLMProcessor()

        # Crear un archivo de prueba
        test_content = """
        ROCE Y LIMPIEZA (ANTES – DURANTE - DESPUES)
        • PROGRESIVA: 0+900 A 0+1800
        • UBICACIÓN: CABANACONDE, PROVINCIA DE CAYLLOMA
        """

        test_file = "test_llm_content.md"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_content)

        # Procesar el archivo
        result = processor.process_text_file(test_file)

        if result:
            print(f"   ✅ Procesamiento exitoso")
            print(f"   Actividad: {result['actividad']}")
            print(f"   Progresivas: {result['progresivas']}")
        else:
            print(f"   ❌ Error en el procesamiento")

        # Limpiar archivo de prueba
        os.remove(test_file)

    except Exception as e:
        print(f"   ❌ Error en LLMProcessor: {e}")

    print("✅ LLMProcessor probado")


def main():
    """
    Función principal de prueba
    """
    print("🧪 Iniciando pruebas del LLM con validación...")

    # Probar componentes individuales
    test_activity_mapper()
    test_response_validator()
    test_llm_processor()

    print("\n🎉 Todas las pruebas completadas!")


if __name__ == "__main__":
    main()
