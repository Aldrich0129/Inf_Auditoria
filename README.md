# Plataforma de Generación de Informes

Sistema modular y extensible para la generación automática de informes basados en plantillas Word, configuraciones YAML y lógica Python.

## 🏗️ Arquitectura

La plataforma sigue una arquitectura de tres capas:

```
report_platform/
├── core/           # Núcleo genérico (independiente del dominio)
├── reports/        # Plugins de informes (cada tipo de informe es un plugin)
└── ui/             # Interfaz unificada (Streamlit)
```

### Core (Núcleo)

El núcleo proporciona capacidades genéricas reutilizables:

- **Carga de configuración**: Lectura y validación de manifests y YAMLs
- **Motor de condiciones**: Evaluación de expresiones lógicas
- **Renderizado de documentos**: Generación de Word con variables Jinja2
- **Runtime de UI**: Generación dinámica de controles desde schemas
- **Validación de datos**: Verificación de campos y tablas

### Reports (Plugins)

Cada plugin representa un tipo de informe e incluye:

- `manifest.yaml`: Metadatos del plugin
- `templates/`: Plantilla Word del informe
- `config/`: Archivos YAML de configuración
- `logic.py`: Función `build_context()` específica del informe

Para agregar un nuevo tipo de informe, simplemente:
1. Crea una carpeta en `reports/`
2. Añade manifest, template, configs y logic
3. La UI lo detectará automáticamente

### UI (Interfaz)

Interfaz web unificada que:
- Descubre plugins disponibles automáticamente
- Genera formularios dinámicos según los schemas YAML
- Recolecta datos del usuario y genera el informe

## 🚀 Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

## 📖 Uso

### Ejecutar la aplicación

```bash
streamlit run report_platform/ui/app.py
```

La aplicación se abrirá en el navegador en `http://localhost:8501`

### Flujo de trabajo

1. **Seleccionar tipo de informe**: Elige el plugin en el selector
2. **Completar formulario**: Rellena los campos requeridos
3. **Generar informe**: Haz clic en "Generar Informe"
4. **Descargar**: El documento se generará en `/mnt/user-data/outputs/`

## 🔧 Configuración de Plugins

### Estructura de un plugin

```
reports/mi_informe/
├── manifest.yaml              # Metadatos del plugin
├── templates/
│   └── plantilla.docx        # Template Word con {{ variables }}
├── config/
│   ├── variables_simples.yaml      # Campos de entrada
│   ├── variables_condicionales.yaml # Selectores condicionales
│   └── bloques_texto.yaml          # Bloques de texto con lógica
└── logic.py                   # build_context(data_in) -> context
```

### Archivo manifest.yaml

```yaml
id: mi_informe
nombre: Mi Informe Personalizado
version: "1.0"
descripcion: Descripción del informe
paths:
  template: templates/plantilla.docx
  config_dir: config
```

### Archivo logic.py

Debe exportar la función:

```python
def build_context(data_in: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye el contexto final para la plantilla.
    
    Args:
        data_in: Datos de entrada del usuario
    
    Returns:
        Contexto completo con todas las variables
    """
    # Tu lógica aquí
    return context
```

## 📚 Tecnologías

- **Python 3.11+**: Lenguaje base
- **Streamlit**: Framework de UI
- **Pydantic**: Validación de datos
- **Jinja2**: Motor de templates
- **python-docx**: Manipulación de Word
- **PyYAML**: Parsing de configuración

## 🎯 Características

### ✅ Implementadas

- Arquitectura modular y extensible
- Carga dinámica de plugins
- Generación de UI desde YAML
- Motor de condiciones lógicas
- Renderizado de bloques de texto

### 🔄 Próximas

- Renderizado completo de Word (actualmente es placeholder)
- Soporte para tablas dinámicas
- Validaciones avanzadas
- Exportación a otros formatos (PDF, HTML)

## 📝 Ejemplo: Plugin de Informe de Auditoría

El plugin `informe_auditoria` incluido demuestra todas las capacidades:

- **70+ campos configurables**: Desde información general hasta notas técnicas
- **Lógica condicional compleja**: Bloques de texto que se adaptan según el tipo de opinión
- **Variables calculadas**: Año anterior, sufijos, textos derivados
- **Validación de dependencias**: Campos que aparecen solo cuando son relevantes

## 🤝 Contribución

Para agregar nuevas funcionalidades al core:

1. Mantén la independencia del dominio
2. Añade tests unitarios
3. Actualiza esta documentación

## 📄 Licencia

[Definir licencia según tu organización]

## 👥 Autores

Jimmy - Forvis Mazars España

---

**Versión**: 1.0  
**Fecha**: Diciembre 2024
