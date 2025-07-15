# Directrices del Proyecto: Procesador de Paneles Fotográficos

## Objetivo General

Desarrollar una herramienta que procese archivos PDF que contienen páginas con texto y páginas con 4 imágenes (en posiciones fijas), para:

- Separar páginas con imágenes de las que solo tienen texto.
- Extraer las 4 imágenes por página, nombrarlas según su posición (before, during1, during2, after) y guardarlas en carpetas.
- Extraer el texto de las páginas.
- Procesar el texto con un LLM (como ChatGPT) usando prompts personalizados para extraer datos relevantes.
- Guardar los datos extraídos en formato JSON.

---

## Paso a Paso para la Implementación

### 1. **Estructura del Proyecto**

Organiza el proyecto en carpetas para separar la lógica de procesamiento, extracción y almacenamiento de datos.

```
procesador_paneles_fotograficos/
├── src/
│   ├── pdf_processor/
│   ├── llm_processor/
│   ├── utils/
├── output/
│   ├── images/
│   └── processed_data/
└── config/
```

### 2. **Separación de Páginas**

- Detectar y separar páginas que contienen imágenes de las que solo tienen texto.
- Herramientas sugeridas: `PyMuPDF` (fitz), `pdfplumber`.

### 3. **Extracción de Imágenes**

- Para cada página con imágenes, dividir la página en 4 cuadrantes.
- Extraer cada imagen y guardarla con el nombre correspondiente:
  - Superior izquierda: `before`
  - Superior derecha: `during1`
  - Inferior izquierda: `during2`
  - Inferior derecha: `after`
- Herramientas sugeridas: `PyMuPDF`, `Pillow` (PIL).

### 4. **Extracción de Texto**

- Extraer el texto de todas las páginas (tanto de texto puro como de las que contienen imágenes).
- Herramientas sugeridas: `pdfplumber`, `PyMuPDF`.

### 5. **Procesamiento con LLM**

- Enviar el texto extraído a un LLM (por ejemplo, ChatGPT vía API de OpenAI).
- Diseñar prompts personalizados para extraer la información relevante.
- Herramientas sugeridas: `openai`, `anthropic`, o cualquier API de LLM.

### 6. **Almacenamiento de Resultados**

- Guardar las imágenes extraídas en la carpeta `output/images/`.
- Guardar los datos procesados en formato JSON en `output/processed_data/`.

### 7. **Configuración y Utilidades**

- Usar archivos de configuración (por ejemplo, YAML) para definir prompts y parámetros.
- Implementar utilidades para manejo de archivos y formateo de datos.

---

## Consideraciones Adicionales

- **Calidad de imágenes**: Verificar la resolución y consistencia de las imágenes extraídas.
- **Costos de API**: Considerar el costo de uso de LLMs.
- **Manejo de errores**: Implementar manejo robusto de errores para PDFs malformados o inconsistentes.
- **Procesamiento por lotes**: Permitir procesar múltiples archivos PDF de manera eficiente.

---

## Tecnologías Recomendadas

- Procesamiento PDF: `PyMuPDF`, `pdfplumber`
- Procesamiento de imágenes: `Pillow`
- LLM: `openai`, `anthropic`
- Manejo de datos: `pydantic`, `json`, `pyyaml`

---

## Próximos Pasos

1. Crear la estructura de carpetas y archivos base.
2. Implementar la separación de páginas.
3. Desarrollar el extractor de imágenes.
4. Configurar la extracción de texto.
5. Integrar el procesamiento con LLM.
6. Implementar el guardado de resultados en JSON.
7. Realizar pruebas con archivos PDF reales.

---

¿Dudas o sugerencias? ¡Adáptalo según tus necesidades!
