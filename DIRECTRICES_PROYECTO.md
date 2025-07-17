# Directrices del Proyecto: Procesador de Paneles Fotográficos

## Objetivo General

Desarrollar una herramienta que procese archivos PDF que contienen páginas con texto y páginas con 4 imágenes (en posiciones fijas), para:

- ✅ Separar páginas con imágenes de las que solo tienen texto.
- ✅ Extraer las 4 imágenes por página, nombrarlas según su posición (before, during1, during2, after) y guardarlas en carpetas.
- ✅ Extraer el texto de las páginas.
- ✅ Procesar el texto con un LLM (como ChatGPT) usando prompts personalizados para extraer datos relevantes.
- ✅ Guardar los datos extraídos en formato JSON.

---

## Estado Actual del Proyecto

### ✅ **Implementado y Funcionando:**

#### 1. **Estructura del Proyecto** ✅

```
procesador_paneles_fotograficos/
├── src/
│   ├── __init__.py
│   ├── main.py                    # 🎯 Orquestador principal
│   ├── pdf_processor/
│   │   ├── __init__.py
│   │   ├── page_separator.py      # 🔧 Separador de páginas
│   │   ├── image_extractor.py     # 🖼️ Extractor de imágenes
│   │   └── text_extractor.py      # 📄 Extractor de texto
│   └── utils/
│       ├── __init__.py
│       └── file_manager.py        # 📁 Gestor de archivos
├── output/
│   └── images/                    # 📸 Imágenes extraídas + texto + análisis JSON
├── temp/                          # 🗂️ Archivos temporales
├── config/                        # ⚙️ Configuración (completada)
├── .cache/                        # 🗄️ Cache centralizado
├── .gitignore                     # 🚫 Archivos ignorados
├── pyproject.toml                 # 📦 Dependencias y configuración
├── clean_cache.py                 # 🧹 Limpiador de cache
├── run.py                         # 🚀 Script de ejecución
└── DIRECTRICES_PROYECTO.md       # 📋 Este archivo
```

#### 2. **Separación de Páginas** ✅

- **Archivo**: `src/pdf_processor/page_separator.py`
- **Funcionalidad**:
  - Detecta páginas con exactamente 4 imágenes grandes
  - Ignora logos e imágenes pequeñas automáticamente
  - Crea PDF filtrado solo con páginas válidas
  - Guarda en carpeta `temp/`
- **Resultados**: ✅ 11 páginas filtradas exitosamente

#### 3. **Extracción de Imágenes** ✅

- **Archivo**: `src/pdf_processor/image_extractor.py`
- **Funcionalidad**:
  - Identifica las 4 imágenes más grandes por página
  - Asigna nombres según posición: `before`, `during1`, `during2`, `after`
  - Guarda en formato PNG con alta calidad
  - Organiza en carpetas por página: `output/images/page_X/`
- **Resultados**: ✅ 44 imágenes extraídas exitosamente (11 páginas × 4 imágenes)

#### 4. **Extracción de Texto** ✅

- **Archivo**: `src/pdf_processor/text_extractor.py`
- **Funcionalidad**:
  - Extrae texto real de páginas PDF usando `pdfplumber`
  - Preserva saltos de línea y estructura jerárquica
  - Limpia texto manteniendo formato original
  - Guarda como archivos markdown junto a las imágenes
- **Resultados**: ✅ 11 archivos `text.md` creados exitosamente
- **Estructura**: Cada página tiene su `text.md` con información del proyecto

#### 5. **Gestión de Archivos** ✅

- **Archivo**: `src/utils/file_manager.py`
- **Funcionalidad**:
  - Limpieza automática de archivos temporales
  - Gestión de directorios y archivos
  - Operaciones de copia y movimiento
- **Resultados**: ✅ Funcionando correctamente

#### 6. **Configuración de Entorno** ✅

- **Cache Centralizado**: Los archivos `__pycache__` se generan en `.cache/`
- **Gestión de Dependencias**: Configurado con `uv`
- **Scripts de Ejecución**: `run.py` y `clean_cache.py`
- **Resultados**: ✅ Entorno optimizado

#### 7. **Procesamiento con LLM** ✅

- **Archivo**: `src/llm_processor/llm_processor.py`
- **Funcionalidad**:
  - Procesa archivos markdown con OpenAI GPT-4
  - Extrae información estructurada: actividad y progresivas
  - Genera JSON con formato específico
  - Maneja errores y respuestas del LLM
- **Configuración**: Archivos YAML para prompts y settings
- **Resultados**: ✅ 11 archivos JSON generados exitosamente

#### 8. **Configuración de Prompts** ✅

- **Archivo**: `config/prompts.yaml`
- **Funcionalidad**:
  - Prompt detallado para análisis de documentos de ingeniería civil
  - Instrucciones específicas para extraer actividades y progresivas
  - Ejemplos de formato de salida JSON
  - Lista de actividades de mantenimiento vial válidas
- **Resultados**: ✅ Prompt optimizado para extracción precisa

#### 9. **Configuración General** ✅

- **Archivo**: `config/settings.yaml`
- **Funcionalidad**:
  - Configuración del modelo LLM (GPT-4)
  - Parámetros de temperatura y tokens
  - Rutas de archivos y directorios
  - Configuración de cache y limpieza
- **Resultados**: ✅ Configuración centralizada y flexible

---

## Paso a Paso para la Implementación

### ✅ 1. **Estructura del Proyecto** - COMPLETADO

Organiza el proyecto en carpetas para separar la lógica de procesamiento, extracción y almacenamiento de datos.

### ✅ 2. **Separación de Páginas** - COMPLETADO

- ✅ Detectar y separar páginas que contienen imágenes de las que solo tienen texto.
- ✅ Herramientas utilizadas: `PyMuPDF` (pymupdf), `pdfplumber`.
- ✅ **Resultado**: 11 páginas filtradas exitosamente

### ✅ 3. **Extracción de Imágenes** - COMPLETADO

- ✅ Para cada página con imágenes, dividir la página en 4 cuadrantes.
- ✅ Extraer cada imagen y guardarla con el nombre correspondiente:
  - ✅ Superior izquierda: `before`
  - ✅ Superior derecha: `during1`
  - ✅ Inferior izquierda: `during2`
  - ✅ Inferior derecha: `after`
- ✅ Herramientas utilizadas: `PyMuPDF`, `Pillow` (PIL).
- ✅ **Resultado**: 44 imágenes extraídas y organizadas

### ✅ 4. **Extracción de Texto** - COMPLETADO

- ✅ Extraer el texto de todas las páginas (tanto de texto puro como de las que contienen imágenes).
- ✅ Herramientas utilizadas: `pdfplumber`.
- ✅ **Resultado**: 11 archivos markdown creados con información del proyecto
- ✅ **Información Extraída**:
  - Nombre del proyecto: "MANTENIMIENTO VIAL RUTINARIO..."
  - Ubicación: "CABANACONDE, PROVINCIA DE CAYLLOMA..."
  - Tipo de trabajo: "ROCE Y LIMPIEZA", "LIMPIEZA DE CUNETAS"
  - Progresivas: "0+900 A 0+1800", "1+378 A 1+756"
  - Etapas: "ANTES – DURANTE - DESPUES"

### ✅ 5. **Procesamiento con LLM** - COMPLETADO

- ✅ Enviar el texto extraído a un LLM (OpenAI GPT-4 vía API).
- ✅ Diseñar prompts personalizados para extraer la información relevante.
- ✅ Herramientas utilizadas: `openai`, `yaml`, `dotenv`.
- ✅ **Resultado**: 11 archivos JSON generados exitosamente

### ✅ 6. **Almacenamiento de Resultados** - COMPLETADO

- ✅ Guardar las imágenes extraídas en la carpeta `output/images/`.
- ✅ Guardar el texto extraído en archivos markdown.
- ✅ Guardar los datos procesados en formato JSON dentro de cada carpeta de página.
- ✅ **Resultado**: Estructura organizada por página con imágenes + texto + análisis

### ✅ 7. **Configuración y Utilidades** - COMPLETADO

- ✅ Implementar utilidades para manejo de archivos y formateo de datos.
- ✅ Usar archivos de configuración (YAML) para definir prompts y parámetros.
- ✅ **Resultado**: Configuración centralizada y flexible

---

## Consideraciones Adicionales

- ✅ **Calidad de imágenes**: Verificar la resolución y consistencia de las imágenes extraídas.
- ✅ **Calidad de texto**: Preservar estructura jerárquica y saltos de línea.
- ⏳ **Costos de API**: Considerar el costo de uso de LLMs.
- ✅ **Manejo de errores**: Implementar manejo robusto de errores para PDFs malformados o inconsistentes.
- ✅ **Procesamiento por lotes**: Permitir procesar múltiples archivos PDF de manera eficiente.

---

## Tecnologías Utilizadas

- ✅ Procesamiento PDF: `PyMuPDF`, `pdfplumber`
- ✅ Procesamiento de imágenes: `Pillow`
- ✅ Extracción de texto: `pdfplumber`
- ✅ LLM: `openai`, `yaml`, `dotenv`
- ✅ Manejo de datos: `json`, `pyyaml`

---

## Próximos Pasos

1. ✅ Crear la estructura de carpetas y archivos base.
2. ✅ Implementar la separación de páginas.
3. ✅ Desarrollar el extractor de imágenes.
4. ✅ Configurar la extracción de texto.
5. ✅ Integrar el procesamiento con LLM.
6. ✅ Implementar el guardado de resultados en JSON.
7. ✅ Realizar pruebas con archivos PDF reales.

---

## Comandos de Ejecución

```bash
# Ejecutar el proyecto completo
uv run python src/main.py

# Limpiar cache
python clean_cache.py

# Ejecutar con configuración optimizada
python run.py
```

---

## Resultados Actuales

- **Páginas Procesadas**: 11 páginas con imágenes
- **Imágenes Extraídas**: 44 imágenes (4 por página)
- **Archivos de Texto**: 11 archivos markdown
- **Archivos JSON**: 11 archivos de análisis + 1 resumen general
- **Formato Imágenes**: PNG de alta calidad
- **Formato Texto**: Markdown con estructura preservada
- **Formato Análisis**: JSON estructurado con actividad y progresivas
- **Organización**: Carpeta por página con imágenes + texto + análisis
- **Cache**: Centralizado en `.cache/`
- **Tiempo de Procesamiento**: ~45 segundos (incluyendo LLM)

### 📁 **Estructura de Salida Actual**:

```
output/images/
├── page_1/
│   ├── before.png
│   ├── during1.png
│   ├── during2.png
│   ├── after.png
│   ├── text.md          # ← Texto extraído
│   └── analysis.json    # ← Análisis LLM
├── page_2/
│   ├── before.png
│   ├── during1.png
│   ├── during2.png
│   ├── after.png
│   ├── text.md
│   └── analysis.json
├── ...
└── summary.json         # ← Resumen general
```

---

## 🎯 **PROYECTO COMPLETADO** ✅

El procesador de paneles fotográficos está **100% funcional** y cumple con todos los objetivos establecidos:

### ✅ **Funcionalidades Implementadas:**

1. **Separación inteligente** de páginas con imágenes
2. **Extracción precisa** de 4 imágenes por página con nombres posicionales
3. **Extracción de texto** preservando estructura y formato
4. **Procesamiento con LLM** usando OpenAI GPT-4
5. **Análisis estructurado** generando JSON con actividad y progresivas
6. **Organización automática** por carpetas de página
7. **Configuración centralizada** con archivos YAML
8. **Gestión de cache** optimizada

### 📊 **Resultados Finales:**

- **11 páginas procesadas** exitosamente
- **44 imágenes extraídas** (4 por página)
- **11 archivos JSON** de análisis generados
- **Estructura organizada** por página
- **Tiempo total**: ~45 segundos

### 🚀 **Listo para Producción:**

El sistema está completamente funcional y puede procesar PDFs similares de manera automática y confiable.

---

¿Dudas o sugerencias? ¡Adáptalo según tus necesidades!
