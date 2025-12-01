# REFACTORIZACIÓN DE PLANTILLAS - ESQUEMA A
## Sistema de Generación de Informes de Auditoría

### Resumen de cambios

| Archivo | Antes | Después |
|---------|-------|---------|
| `Plantilla_inf_audi.txt` | 298 líneas, 42 bloques `{% if %}` | 101 líneas, 0 bloques `{% if %}` |
| YAML | Sin `bloques_texto` | 1232 líneas con toda la lógica |
| `logic.py` | No existía | 443 líneas con `build_context()` |

---

## Archivos generados

### 1. `Plantilla_inf_audi_refactorizada.txt`
**Plantilla limpia** que solo contiene variables simples `{{ variable }}`.

Características:
- ✅ Sin lógica condicional (`{% if %}`, `{% elif %}`, `{% endif %}`)
- ✅ Solo comentarios Jinja2 como separadores de sección `{# ... #}`
- ✅ Cada sección condicional ahora es una variable (ej: `{{ parrafo_opinion }}`)

### 2. `bloques_texto.yaml`
**Configuración estructurada** de todos los bloques de texto condicionales.

Estructura de cada bloque:
```yaml
- id: parrafo_opinion              # ID usado en la plantilla {{ parrafo_opinion }}
  descripcion: "Párrafo de opinión según el tipo"
  reglas:
    - cuando: "tipo_opinion == 'favorable' and tipo_cuentas == 'normales'"
      plantilla: >
        En nuestra opinión, las cuentas anuales adjuntas expresan...
    - cuando: "tipo_opinion == 'salvedades'"
      plantilla: >
        En nuestra opinión, excepto por los efectos...
    - cuando: "True"  # Default
      plantilla: ""
```

### 3. `logic.py`
**Motor de procesamiento** que:
1. Carga la configuración YAML
2. Evalúa las condiciones de cada bloque
3. Renderiza las plantillas con Jinja2
4. Calcula variables auxiliares
5. Devuelve el contexto completo

---

## Cómo usar el sistema

### Paso 1: Preparar los datos de entrada
```python
data_in = {
    'tipo_opinion': 'favorable',
    'tipo_cuentas': 'normales',
    'nombre_entidad': 'Empresa ABC S.A.',
    'dia_cierre_ejercicio': 31,
    'mes_cierre_ejercicio': 'diciembre',
    'ano_cierre_ejercicio': 2024,
    # ... resto de campos del formulario
}
```

### Paso 2: Construir el contexto
```python
from logic import build_context
from pathlib import Path

# El directorio donde están los archivos YAML
config_dir = Path('./config')

# Construir el contexto completo
context = build_context(data_in, config_dir)
```

### Paso 3: Renderizar la plantilla Word
```python
from docxtpl import DocxTemplate

doc = DocxTemplate('Plantilla_inf_audi.docx')
doc.render(context)
doc.save('informe_generado.docx')
```

---

## Variables principales generadas

### Bloques de texto (secciones completas)
| Variable | Descripción |
|----------|-------------|
| `titulo_tipo_opinion` | "Opinión" / "Opinión con salvedades" / etc. |
| `descripcion_cuentas_auditadas` | Párrafo inicial describiendo las cuentas |
| `parrafo_opinion` | Párrafo de opinión completo según tipo |
| `titulo_fundamento` | Título de la sección de fundamento |
| `parrafo_fundamento_calificacion` | Fundamento específico (si aplica) |
| `texto_base_fundamento` | Texto normativo sobre conformidad |
| `seccion_incertidumbre_funcionamiento` | Sección completa de incertidumbre |
| `seccion_enfasis` | Párrafo de énfasis |
| `seccion_kam_amra` | Sección KAM/AMRA completa |
| `seccion_otras_cuestiones` | Sección de otras cuestiones |
| `seccion_otra_informacion` | Sección de informe de gestión |
| `seccion_par_abreviadas` | Sección PAR (cuentas abreviadas) |
| `titulo_responsabilidad_administradores` | Título de responsabilidad |
| `texto_responsabilidad_administradores` | Texto de responsabilidad |
| `texto_comision_auditoria` | Texto comisión (solo EIP) |
| `texto_comunicacion_kam_eip` | Comunicación KAM (solo EIP) |
| `seccion_eip_completa` | Sección EIP completa |
| `texto_firma_digital` | Referencia a sello ICJCE |

### Variables auxiliares (calculadas automáticamente)
| Variable | Ejemplo |
|----------|---------|
| `nombre_tipo_cuentas` | "cuentas anuales consolidadas" |
| `nombre_fundamento` | "opinión con salvedades" |
| `sufijo_consolidada` | " consolidada" |
| `sufijo_abreviadas` | " abreviadas" |
| `texto_auditor_continuidad` | "fuimos designados" |
| `texto_servicios_adicionales` | Texto completo o default |

---

## Integración con el sistema existente

### En el plugin de informes de auditoría:

```python
# En tu archivo de plugin (ej: informe_auditoria/plugin.py)

from logic import build_context
from pathlib import Path

class InformeAuditoriaPlugin:
    
    def __init__(self):
        self.config_dir = Path(__file__).parent / 'config'
    
    def generar_informe(self, datos_formulario: dict) -> str:
        """
        Genera el informe de auditoría.
        
        Args:
            datos_formulario: Datos recogidos del UI (Streamlit)
        
        Returns:
            Ruta al archivo generado
        """
        # 1. Construir el contexto
        context = build_context(datos_formulario, self.config_dir)
        
        # 2. Cargar la plantilla
        from docxtpl import DocxTemplate
        template_path = self.config_dir / 'Plantilla_inf_audi.docx'
        doc = DocxTemplate(str(template_path))
        
        # 3. Renderizar
        doc.render(context)
        
        # 4. Guardar
        output_path = f'informe_{datos_formulario["nombre_entidad"]}.docx'
        doc.save(output_path)
        
        return output_path
```

---

## Ventajas del Esquema A

1. **Plantilla limpia**: Fácil de editar en Word sin conocer Jinja2
2. **Lógica centralizada**: Toda la condicionalidad en un solo lugar (YAML + Python)
3. **Mantenibilidad**: Cambiar textos sin tocar código, cambiar lógica sin tocar plantilla
4. **Testeable**: La función `build_context()` se puede probar unitariamente
5. **Extensible**: Añadir nuevos bloques es simplemente añadir entradas al YAML

---

## Notas importantes

- El archivo `bloques_texto.yaml` contiene **1232 líneas** con todas las variantes de texto
- El orden de las reglas importa: **se usa la primera regla cuya condición sea True**
- La condición `"True"` al final de un bloque actúa como **default**
- Las variables auxiliares evitan repetir lógica en las plantillas

---

## Archivos YAML existentes

Los archivos `variables_simples.yaml` y `variables_condicionales.yaml` **se mantienen sin cambios**.
El nuevo `bloques_texto.yaml` complementa a estos, no los reemplaza.

```
config/
├── variables_simples.yaml        # Definición de campos UI (sin cambios)
├── variables_condicionales.yaml  # Opciones y metadatos (sin cambios)  
├── bloques_texto.yaml            # NUEVO: Bloques de texto condicionales
└── Plantilla_inf_audi.docx       # Plantilla Word refactorizada
```

---

Versión: 3.0 - Esquema A (Lógica Externa)
Fecha: Diciembre 2024
