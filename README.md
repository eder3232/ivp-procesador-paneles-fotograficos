# 📸 Procesador de Paneles Fotográficos

Una herramienta avanzada para procesar archivos PDF que contienen paneles fotográficos de proyectos de ingeniería civil. Extrae automáticamente imágenes, texto y analiza el contenido usando inteligencia artificial.

## 🎯 ¿Qué hace este proyecto?

Este procesador está diseñado específicamente para PDFs que contienen:

- **Páginas con texto** (información del proyecto)
- **Páginas con 4 imágenes** en posiciones fijas (antes, durante1, durante2, después)

### ✨ Funcionalidades principales:

1. **🔍 Separación inteligente** de páginas con imágenes vs texto
2. **🖼️ Extracción automática** de 4 imágenes por página con nombres posicionales
3. **📄 Extracción de texto** preservando estructura y formato
4. **🤖 Análisis con IA** usando OpenAI GPT-4 para extraer información estructurada
5. **📊 Generación de JSON** con datos organizados por actividad
6. **📁 Organización automática** de archivos por página y actividad
7. **📄 Generación de PDFs** por actividad con imágenes y análisis
8. **🔗 Unificación** de todos los PDFs en un archivo final

## 🚀 Instalación

### Prerrequisitos

- **Python 3.12 o superior**
- **uv** (gestor de paquetes moderno para Python)
- **Clave API de OpenAI** (para el análisis con IA)

### Paso 1: Instalar uv

Si no tienes `uv` instalado, puedes instalarlo con:

```bash
# En Windows (PowerShell)
pip install uv

# En macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Paso 2: Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd procesador_paneles_fotograficos
```

### Paso 3: Instalar dependencias

```bash
uv sync
```

### Paso 4: Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# .env
OPENAI_APIKEY=tu_clave_api_de_openai_aqui
```

> **💡 Nota**: Necesitas una cuenta en [OpenAI](https://platform.openai.com/) para obtener tu API key.

## 📋 Uso

### Ejecución básica

```bash
# Ejecutar el procesador completo
uv run python run.py
```

### Ejecución directa

```bash
# Alternativa: ejecutar directamente el archivo principal
uv run python src/main.py
```

### Limpiar cache

```bash
# Limpiar archivos temporales y cache
python clean_cache.py
```

## 📁 Estructura del proyecto

```
procesador_paneles_fotograficos/
├── src/                          # Código fuente principal
│   ├── main.py                   # 🎯 Orquestador principal
│   ├── pdf_processor/            # Procesamiento de PDFs
│   │   ├── page_separator.py     # Separador de páginas
│   │   ├── advanced_image_extractor.py  # Extractor de imágenes
│   │   └── text_extractor.py     # Extractor de texto
│   ├── llm_processor/            # Procesamiento con IA
│   │   └── llm_processor.py      # Integración con OpenAI
│   ├── pdf_generator/            # Generación de PDFs
│   │   ├── pdf_generator.py      # Generador de paneles
│   │   └── pdf_unifier.py        # Unificador de PDFs
│   ├── utils/                    # Utilidades
│   │   ├── file_manager.py       # Gestión de archivos
│   │   └── output_organizer.py   # Organización de salida
│   └── data/                     # Archivos de datos
│       └── panel_fotografico_corregido_v2.pdf  # PDF de ejemplo
├── config/                       # Configuración
│   ├── settings.yaml             # Configuración general
│   ├── prompts.yaml              # Prompts para IA
│   └── pdf_settings.yaml         # Configuración de PDFs
├── output/                       # Resultados generados
│   └── images/                   # Imágenes extraídas + análisis
├── temp/                         # Archivos temporales
├── .cache/                       # Cache del sistema
├── pyproject.toml                # Dependencias y configuración
├── uv.lock                       # Lock de dependencias
├── run.py                        # Script de ejecución optimizado
└── clean_cache.py                # Limpiador de cache
```

## 🔧 Configuración

### Archivo de configuración principal (`config/settings.yaml`)

```yaml
# Configuraciones de LLM
llm:
  provider: 'openai'
  api_key_env: 'OPENAI_APIKEY'
  model: 'gpt-4o-mini'
  temperature: 0
  max_tokens: 150
  timeout: 30

# Configuraciones de archivos
files:
  input_pdf: 'src/data/panel_fotografico_corregido_v2.pdf'
  temp_dir: 'temp'
  output_images: 'output/images'
```

### Personalizar prompts (`config/prompts.yaml`)

Puedes modificar los prompts que se envían al LLM para adaptarlos a tus necesidades específicas.

## 📊 Resultados esperados

### Estructura de salida

```
output/images/
├── page_1/
│   ├── before.png          # Imagen antes de la obra
│   ├── during1.png         # Imagen durante la obra (1)
│   ├── during2.png         # Imagen durante la obra (2)
│   ├── after.png           # Imagen después de la obra
│   ├── text.md             # Texto extraído de la página
│   └── analysis.json       # Análisis estructurado por IA
├── page_2/
│   ├── before.png
│   ├── during1.png
│   ├── during2.png
│   ├── after.png
│   ├── text.md
│   └── analysis.json
├── ...
├── activities/              # Organización por actividades
│   ├── roce_y_limpieza/
│   │   ├── panel_1.pdf
│   │   └── panel_2.pdf
│   └── limpieza_cunetas/
│       ├── panel_1.pdf
│       └── panel_2.pdf
└── unified_panels.pdf       # PDF final unificado
```

### Formato del análisis JSON

```json
{
  "actividad": "ROCE Y LIMPIEZA",
  "progresivas": "0+900 A 0+1800",
  "ubicacion": "CABANACONDE, PROVINCIA DE CAYLLOMA",
  "etapa": "ANTES – DURANTE - DESPUES",
  "descripcion": "Trabajos de roce y limpieza en el tramo especificado"
}
```

## ⚙️ Personalización

### Cambiar el archivo PDF de entrada

1. Coloca tu archivo PDF en `src/data/`
2. Actualiza la ruta en `config/settings.yaml`:

```yaml
files:
  input_pdf: 'src/data/tu_archivo.pdf'
```

### Modificar el modelo de IA

En `config/settings.yaml`:

```yaml
llm:
  model: 'gpt-4' # o 'gpt-3.5-turbo' para menor costo
  temperature: 0.1 # Ajustar creatividad (0-1)
```

### Ajustar parámetros de extracción

```yaml
processing:
  min_images_per_page: 4
  max_images_per_page: 5
  min_image_size: 10000 # Tamaño mínimo en bytes
```

## 🐛 Solución de problemas

### Error: "No se encontró el archivo PDF"

- Verifica que el archivo existe en la ruta especificada en `config/settings.yaml`
- Asegúrate de que el archivo no esté corrupto

### Error: "Error de API de OpenAI"

- Verifica que tu clave API esté correctamente configurada en el archivo `.env`
- Comprueba que tienes créditos disponibles en tu cuenta de OpenAI
- Revisa la conectividad a internet

### Error: "No se encontraron páginas con imágenes"

- El PDF debe contener páginas con exactamente 4 imágenes grandes
- Las imágenes deben ser suficientemente grandes (mínimo 10KB por defecto)
- Ajusta `min_image_size` en la configuración si es necesario

### Error de dependencias

```bash
# Reinstalar dependencias
uv sync --reinstall
```

## 📈 Rendimiento

- **Tiempo de procesamiento**: ~45 segundos para 11 páginas
- **Memoria utilizada**: ~200MB
- **Archivos generados**: 44 imágenes + 11 análisis JSON + PDFs finales

## 🔒 Seguridad

- Las claves API se almacenan en variables de entorno
- Los archivos temporales se limpian automáticamente
- No se envían datos sensibles a servicios externos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de [Solución de problemas](#-solución-de-problemas)
2. Consulta las [Directrices del Proyecto](DIRECTRICES_PROYECTO.md)
3. Abre un issue en el repositorio

---

**¡Disfruta procesando tus paneles fotográficos! 🚀**
