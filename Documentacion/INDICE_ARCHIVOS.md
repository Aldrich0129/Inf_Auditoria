# 📑 Índice Completo de Archivos

## Documentación

### README.md
**Descripción:** Documentación principal del proyecto  
**Contenido:**
- Descripción general de la arquitectura
- Guía de uso
- Características principales
- Información de contacto

### requirements.txt
**Descripción:** Lista de dependencias Python  
**Contenido:**
- streamlit >= 1.28.0
- pydantic >= 2.4.0
- python-docx >= 0.8.11
- jinja2 >= 3.1.2
- pyyaml >= 6.0.1
- python-dateutil >= 2.8.2
- colorlog >= 6.7.0

### ESTRUCTURA_PROYECTO.txt
**Descripción:** Documentación detallada de la arquitectura  
**Contenido:**
- Árbol de directorios completo
- Descripción de cada módulo
- Flujo de datos
- Guía para agregar plugins

### INSTRUCCIONES_INSTALACION.md
**Descripción:** Guía paso a paso de instalación  
**Contenido:**
- Requisitos previos
- Instalación de dependencias
- Ejecución de la aplicación
- Solución de problemas
- Despliegue en producción

---

## 🔷 Core (Núcleo)

### report_platform/__init__.py
**Tipo:** Módulo raíz  
**Funciones exportadas:**
- `load_manifest()`
- `load_yaml_config()`
- `SimpleField`
- `BlockDefinition`
- `Manifest`

**Propósito:** Punto de entrada del paquete, exporta componentes principales

---

### report_platform/core/__init__.py
**Tipo:** Módulo del core  
**Funciones exportadas:**
- `load_manifest()`
- `load_yaml_config()`
- `SimpleField`
- `BlockDefinition`
- `Manifest`

**Propósito:** Agrupa y exporta funcionalidad del núcleo

---

### report_platform/core/utils.py
**Tipo:** Utilidades  
**Funciones principales:**
- `setup_logger(name, level)` → Logger configurado
- `get_project_root()` → Path al directorio raíz
- `get_reports_dir()` → Path al directorio de reports
- `get_outputs_dir()` → Path al directorio de salida
- `safe_filename(filename)` → Nombre de archivo sanitizado
- `load_text_file(filepath)` → Contenido del archivo
- `ensure_directory(directory)` → Crea directorio si no existe

**Dependencias:** logging, pathlib

**Propósito:** Funciones auxiliares para logging, manejo de paths y archivos

---

### report_platform/core/schema_models.py
**Tipo:** Modelos de datos  
**Clases principales:**
- `SimpleField` - Campo simple de entrada
- `ConditionalVariable` - Variable condicional
- `BlockDefinition` - Bloque de texto condicional
- `TableDefinition` - Definición de tabla
- `Manifest` - Manifest de plugin

**Funciones de validación:**
- `validate_field_dict(data)` → SimpleField
- `validate_block_dict(data)` → BlockDefinition
- `validate_manifest_dict(data)` → Manifest

**Dependencias:** pydantic

**Propósito:** Estructuras de datos validadas con Pydantic para garantizar integridad

---

### report_platform/core/config_loader.py
**Tipo:** Carga de configuración  
**Funciones principales:**
- `load_manifest(plugin_dir)` → Manifest | None
- `load_yaml_config(filepath)` → Dict | None
- `load_simple_fields(config_dir)` → List[SimpleField]
- `load_conditional_variables(config_dir)` → List[ConditionalVariable]
- `load_text_blocks(config_dir)` → List[BlockDefinition]
- `load_tables(config_dir)` → List[TableDefinition]
- `load_plugin_config(plugin_dir)` → Dict | None
- `get_general_config(config_dir)` → Dict
- `get_fields_by_section(fields)` → Dict[str, List[SimpleField]]

**Dependencias:** yaml, pathlib, schema_models, utils

**Propósito:** Cargar y parsear archivos de configuración YAML

---

### report_platform/core/conditions_engine.py
**Tipo:** Motor de condiciones  
**Funciones principales:**
- `evaluate_condition(condition, context)` → bool
- `evaluate_any(conditions, context)` → bool
- `evaluate_all(conditions, context)` → bool
- `should_show_field(field_id, dependency_condition, context)` → bool
- `evaluate_block(block, context)` → str | None
- `evaluate_all_blocks(blocks, context)` → Dict[str, str]
- `is_valid_expression(expression)` → bool
- `get_variables_in_expression(expression)` → List[str]
- `build_condition_from_dict(cond_dict)` → str
- `debug_condition_evaluation(condition, context)` → Dict

**Dependencias:** schema_models, utils

**Propósito:** Evaluación segura de expresiones condicionales usando eval()

---

### report_platform/core/word_engine.py
**Tipo:** Motor de renderizado  
**Funciones principales:**
- `render_template_string(template_content, context)` → str
- `render_word_report(template_path, context, output_filename)` → Path | None
- `validate_template(template_path)` → bool
- `get_template_variables(template_path)` → List[str]
- `create_sample_template(output_path, variables)` → bool

**Funciones futuras (placeholder):**
- `render_word_with_docxtpl(...)` → bool
- `render_word_with_python_docx(...)` → bool

**Dependencias:** jinja2, pathlib, utils

**Propósito:** Renderizado de documentos Word (actualmente genera .txt, preparado para Word real)

---

### report_platform/core/tables_engine.py
**Tipo:** Motor de tablas  
**Funciones principales:**
- `validate_table_data(table_def, data)` → (bool, List[str])
- `validate_table_row(table_def, row, row_idx)` → List[str]
- `validate_column_value(column, value, row_idx)` → str | None
- `create_empty_table_row(table_def)` → Dict
- `create_table_template(table_def, num_rows)` → List[Dict]
- `table_to_dict_list(table_data, column_ids)` → List[Dict]
- `dict_list_to_table(data, column_ids)` → List[List]
- `filter_table_rows(data, condition)` → List[Dict]
- `sort_table_rows(data, sort_by, reverse)` → List[Dict]
- `aggregate_table_column(data, column_id, operation)` → Any
- `table_to_markdown(table_def, data)` → str
- `table_to_html(table_def, data)` → str

**Dependencias:** schema_models, conditions_engine, utils

**Propósito:** Validación, manipulación y exportación de estructuras de tabla

---

### report_platform/core/ui_runtime.py
**Tipo:** Generador de UI  
**Funciones principales:**
- `render_text_field(field, current_value)` → Any
- `render_long_text_field(field, current_value)` → Any
- `render_number_field(field, current_value)` → Any
- `render_list_field(field, current_value)` → Any
- `render_conditional_variable(var, current_value)` → Any
- `render_field(field, current_value)` → Any
- `should_show_field_in_ui(field, context)` → bool
- `render_section_fields(section_name, fields, context)` → Dict
- `render_all_fields(fields_by_section, sections_order, initial_context)` → Dict
- `validate_form_data(fields, data)` → (bool, List[str])
- `show_validation_errors(errors)` → None
- `show_success_message(message)` → None
- `show_info_message(message)` → None
- `create_download_button(file_path, button_label)` → None

**Dependencias:** streamlit, schema_models, conditions_engine, utils

**Propósito:** Generación dinámica de controles Streamlit desde definiciones YAML

---

## 🔷 Reports (Plugins)

### report_platform/reports/__init__.py
**Tipo:** Módulo de plugins  
**Contenido:** Directorio contenedor para plugins

---

### report_platform/reports/informe_auditoria/__init__.py
**Tipo:** Plugin  
**Funciones exportadas:**
- `build_context(data_in, config_dir)` → Dict

**Propósito:** Punto de entrada del plugin de informe de auditoría

---

### report_platform/reports/informe_auditoria/manifest.yaml
**Tipo:** Configuración  
**Contenido:**
- `id`: informe_auditoria
- `nombre`: Informe de Auditoría de Cuentas Anuales
- `version`: 1.0.0
- `paths`: Rutas a template y config
- `features`: Lista de características
- `tags`: auditoría, cuentas anuales, normativa española

**Propósito:** Metadatos del plugin para descubrimiento y carga

---

### report_platform/reports/informe_auditoria/templates/plantilla_informe.txt
**Tipo:** Plantilla  
**Formato:** Texto con variables Jinja2 `{{ variable }}`  
**Contenido:**
- Encabezado del informe
- Secciones de opinión
- Fundamento de la opinión
- Incertidumbres y énfasis
- Cuestiones clave (KAM/AMRA)
- Responsabilidades
- Firma

**Variables principales:** ~100 variables Jinja2

**Propósito:** Template del informe de auditoría con placeholders

---

### report_platform/reports/informe_auditoria/config/variables_simples.yaml
**Tipo:** Configuración  
**Contenido:**
- 70+ definiciones de campos simples
- Tipos: texto, numero, lista, texto_largo
- Secciones organizadas
- Campos con dependencias
- Validaciones (min, max, requerido)

**Estructura:**
```yaml
variables_simples:
  - id: nombre_entidad
    nombre: "Nombre de la entidad"
    tipo: texto
    requerido: true
    ...
```

**Propósito:** Define todos los campos de entrada del formulario

---

### report_platform/reports/informe_auditoria/config/variables_condicionales.yaml
**Tipo:** Configuración  
**Contenido:**
- Variables que controlan el flujo
- Tipos: tipo_cuentas, tipo_opinion, tipo_entidad, etc.
- Opciones con etiquetas y descripciones
- Dependencias entre variables

**Estructura:**
```yaml
variables_condicionales:
  - id: tipo_opinion
    nombre: "Tipo de opinión de auditoría"
    tipo_control: radio
    opciones:
      - valor: "favorable"
        etiqueta: "Opinión favorable"
        ...
```

**Propósito:** Define variables condicionales que afectan el comportamiento

---

### report_platform/reports/informe_auditoria/config/bloques_texto.yaml
**Tipo:** Configuración  
**Contenido:**
- 50+ definiciones de bloques de texto
- Cada bloque con múltiples reglas condicionales
- Plantillas Jinja2 para cada regla

**Estructura:**
```yaml
bloques_texto:
  - id: parrafo_opinion
    descripcion: "Párrafo de opinión según el tipo"
    reglas:
      - cuando: "tipo_opinion == 'favorable'"
        plantilla: "En nuestra opinión..."
      - cuando: "tipo_opinion == 'salvedades'"
        plantilla: "En nuestra opinión, excepto por..."
```

**Propósito:** Define bloques de texto que se seleccionan según condiciones

---

### report_platform/reports/informe_auditoria/logic.py
**Tipo:** Lógica del plugin  
**Función principal:**
- `build_context(data_in, config_dir)` → Dict

**Clases auxiliares:**
- `BloquesTextoProcessor` - Procesador de bloques

**Funciones auxiliares:**
- `calcular_variables_auxiliares(data_in)` → Dict
- `_evaluar_condicion(condicion, contexto)` → bool
- `_renderizar_plantilla(plantilla, contexto)` → str

**Flujo:**
1. Recibe datos de entrada del usuario
2. Calcula variables auxiliares (sufijos, textos derivados)
3. Carga bloques de texto desde YAML
4. Evalúa condiciones de cada bloque
5. Renderiza plantillas con Jinja2
6. Devuelve contexto completo para Word

**Dependencias:** yaml, pathlib, jinja2, logging

**Propósito:** Construir el contexto final para la generación del informe

---

## 🔷 UI (Interfaz)

### report_platform/ui/__init__.py
**Tipo:** Módulo de UI  
**Funciones exportadas:**
- `list_available_reports()`
- `load_report_plugin(report_id)`

**Propósito:** Punto de entrada de la capa de interfaz

---

### report_platform/ui/router.py
**Tipo:** Enrutador de plugins  
**Funciones principales:**
- `list_available_reports()` → List[Manifest]
- `load_report_plugin(report_id)` → Dict | None
- `import_plugin_logic(plugin_dir)` → Module
- `get_build_context_function(plugin_config)` → Function
- `get_template_path(plugin_config)` → Path
- `get_plugin_info(plugin_config)` → Dict
- `validate_plugin_structure(plugin_dir)` → (bool, List[str])

**Flujo:**
1. Escanea directorio `reports/`
2. Identifica subdirectorios válidos
3. Carga manifest de cada plugin
4. Importa dinámicamente logic.py
5. Devuelve lista de plugins disponibles

**Dependencias:** pathlib, importlib, config_loader, schema_models, utils

**Propósito:** Descubrir y cargar plugins dinámicamente

---

### report_platform/ui/app.py
**Tipo:** Aplicación Streamlit  
**Función principal:**
- `main()` - Punto de entrada de la app

**Funciones auxiliares:**
- `init_session_state()` - Inicializa estado de sesión
- `render_report_selector()` - Selector de plugin en sidebar
- `render_conditional_variables_section(...)` - Renderiza variables condicionales
- `render_simple_fields_section(...)` - Renderiza campos simples
- `generate_report(...)` - Genera el informe

**Flujo completo:**
1. Usuario selecciona plugin
2. App carga configuración del plugin
3. Renderiza variables condicionales (radio buttons)
4. Renderiza campos simples (organizados por secciones)
5. Usuario completa formulario
6. Click en "Generar Informe"
7. Validación de datos
8. Llamada a `build_context()`
9. Renderizado de Word
10. Descarga del archivo

**Estado de sesión:**
- `selected_report` - ID del plugin seleccionado
- `plugin_config` - Configuración cargada
- `form_data` - Datos del formulario

**Dependencias:** streamlit, todas las capas de core y router

**Propósito:** Interfaz web principal de la plataforma

---

## 📊 Resumen por Tipo

### Módulos Core (7 archivos)
- utils.py
- schema_models.py
- config_loader.py
- conditions_engine.py
- word_engine.py
- tables_engine.py
- ui_runtime.py

**Total de funciones:** ~80 funciones

### Plugin de Auditoría (4 archivos + templates/config)
- __init__.py
- manifest.yaml
- logic.py
- templates/plantilla_informe.txt
- config/ (3 YAMLs)

**Total de campos:** 70+ campos configurables  
**Total de bloques:** 50+ bloques de texto

### UI (2 archivos)
- router.py
- app.py

**Total de funciones:** ~15 funciones

---

## 🎯 Archivos por Funcionalidad

### Carga de Datos
- config_loader.py
- router.py

### Validación
- schema_models.py
- tables_engine.py
- ui_runtime.py

### Lógica de Negocio
- conditions_engine.py
- logic.py (en cada plugin)

### Renderizado
- word_engine.py
- ui_runtime.py
- app.py

### Utilidades
- utils.py

---

## 📈 Estadísticas del Proyecto

- **Total de archivos Python:** 15
- **Total de archivos YAML:** 4
- **Total de archivos de documentación:** 4
- **Total de líneas de código (estimado):** ~5,000
- **Total de funciones:** ~100
- **Total de clases Pydantic:** 10
- **Total de campos configurables:** 70+
- **Total de bloques de texto:** 50+

---

**Última actualización:** Diciembre 2024  
**Versión:** 1.0.0  
**Autor:** Jimmy - Forvis Mazars España
