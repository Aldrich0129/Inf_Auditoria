"""
UI Runtime - Motor de generación dinámica de controles UI

Genera automáticamente controles de interfaz Streamlit basándose en
definiciones de campos YAML, permitiendo formularios completamente dinámicos.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import date
from report_platform.core.utils import setup_logger
from report_platform.core.schema_models import SimpleField, ConditionalVariable
from report_platform.core.conditions_engine import evaluate_condition

logger = setup_logger(__name__)


# ==============================================================================
# GENERACIÓN DE CONTROLES INDIVIDUALES
# ==============================================================================

def render_text_field(field: SimpleField, current_value: Any = None) -> Any:
    """
    Renderiza un campo de texto.
    
    Args:
        field: Definición del campo
        current_value: Valor actual (para preservar estado)
    
    Returns:
        Valor introducido por el usuario
    """
    value = st.text_input(
        label=field.nombre,
        value=current_value or "",
        placeholder=field.placeholder or "",
        help=field.ayuda,
        key=f"field_{field.id}"
    )
    return value


def render_long_text_field(field: SimpleField, current_value: Any = None) -> Any:
    """
    Renderiza un campo de texto largo (textarea).
    
    Args:
        field: Definición del campo
        current_value: Valor actual
    
    Returns:
        Valor introducido por el usuario
    """
    value = st.text_area(
        label=field.nombre,
        value=current_value or "",
        placeholder=field.placeholder or "",
        help=field.ayuda,
        key=f"field_{field.id}",
        height=150
    )
    return value


def render_number_field(field: SimpleField, current_value: Any = None) -> Any:
    """
    Renderiza un campo numérico.
    
    Args:
        field: Definición del campo
        current_value: Valor actual
    
    Returns:
        Valor numérico introducido
    """
    # Determinar el paso según si hay decimales
    step = 0.01 if (field.min and isinstance(field.min, float)) else 1
    
    value = st.number_input(
        label=field.nombre,
        value=float(current_value) if current_value is not None else (field.min or 0.0),
        min_value=field.min,
        max_value=field.max,
        step=step,
        help=field.ayuda,
        key=f"field_{field.id}"
    )
    return value


def render_list_field(field: SimpleField, current_value: Any = None) -> Any:
    """
    Renderiza un campo de selección (lista).
    
    Args:
        field: Definición del campo
        current_value: Valor actual
    
    Returns:
        Valor seleccionado
    """
    if not field.opciones:
        st.warning(f"Campo '{field.nombre}' no tiene opciones definidas")
        return None
    
    # Determinar índice por defecto
    default_index = 0
    if current_value and current_value in field.opciones:
        default_index = field.opciones.index(current_value)
    
    value = st.selectbox(
        label=field.nombre,
        options=field.opciones,
        index=default_index,
        help=field.ayuda,
        key=f"field_{field.id}"
    )
    return value


# ==============================================================================
# GENERACIÓN DE VARIABLES CONDICIONALES
# ==============================================================================

def render_conditional_variable(var: ConditionalVariable, 
                               current_value: Any = None) -> Any:
    """
    Renderiza una variable condicional (radio buttons).
    
    Args:
        var: Definición de la variable
        current_value: Valor actual
    
    Returns:
        Valor seleccionado
    """
    if not var.opciones:
        st.warning(f"Variable '{var.nombre}' no tiene opciones definidas")
        return None
    
    # Opciones de la variable
    options = [opt.valor for opt in var.opciones]
    labels = [opt.etiqueta for opt in var.opciones]
    
    # Determinar opción por defecto
    default_idx = 0
    for idx, opt in enumerate(var.opciones):
        if opt.es_default:
            default_idx = idx
            break
    
    if current_value and current_value in options:
        default_idx = options.index(current_value)
    
    # Renderizar según tipo de control
    if var.tipo_control == "radio":
        selected_label = st.radio(
            label=var.nombre,
            options=labels,
            index=default_idx,
            help=var.descripcion,
            key=f"cond_{var.id}"
        )
        # Mapear label a valor
        selected_idx = labels.index(selected_label)
        return options[selected_idx]
    
    elif var.tipo_control == "select":
        selected_label = st.selectbox(
            label=var.nombre,
            options=labels,
            index=default_idx,
            help=var.descripcion,
            key=f"cond_{var.id}"
        )
        selected_idx = labels.index(selected_label)
        return options[selected_idx]
    
    else:
        st.warning(f"Tipo de control desconocido: {var.tipo_control}")
        return options[default_idx]


# ==============================================================================
# GENERACIÓN DE FORMULARIO COMPLETO
# ==============================================================================

def render_field(field: SimpleField, current_value: Any = None) -> Any:
    """
    Renderiza un campo según su tipo.
    
    Args:
        field: Definición del campo
        current_value: Valor actual
    
    Returns:
        Valor introducido por el usuario
    """
    # Mostrar etiqueta de requerido
    label_suffix = " *" if field.requerido else ""
    
    # Renderizar según tipo
    if field.tipo == "texto":
        return render_text_field(field, current_value)
    
    elif field.tipo == "texto_largo":
        return render_long_text_field(field, current_value)
    
    elif field.tipo == "numero":
        return render_number_field(field, current_value)
    
    elif field.tipo == "lista":
        return render_list_field(field, current_value)
    
    else:
        st.warning(f"Tipo de campo no soportado: {field.tipo}")
        return None


def should_show_field_in_ui(field: SimpleField, context: Dict[str, Any]) -> bool:
    """
    Determina si un campo debe mostrarse según su dependencia.
    
    Args:
        field: Definición del campo
        context: Contexto actual con valores
    
    Returns:
        True si el campo debe mostrarse
    """
    # Si el campo es calculado, no se muestra
    if field.calculado:
        return False
    
    # Si tiene condición padre, evaluarla
    if field.condicion_padre:
        return evaluate_condition(field.condicion_padre, context)
    
    # Si tiene dependencia estructurada
    if field.dependencia:
        dep = field.dependencia
        parent_value = context.get(dep.variable)
        
        if dep.valor:
            return parent_value == dep.valor
        elif dep.valor_no:
            return parent_value != dep.valor_no
    
    # Por defecto, mostrar
    return True


def render_section_fields(section_name: str, fields: List[SimpleField], 
                         context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Renderiza todos los campos de una sección.
    
    Args:
        section_name: Nombre de la sección
        fields: Lista de campos de la sección
        context: Contexto actual
    
    Returns:
        Diccionario con valores recolectados {field_id: value}
    """
    st.subheader(section_name)
    
    values = {}
    
    for field in fields:
        # Verificar si debe mostrarse
        if not should_show_field_in_ui(field, context):
            continue
        
        # Renderizar el campo
        value = render_field(field, context.get(field.id))
        
        if value is not None:
            values[field.id] = value
            # Actualizar contexto para campos dependientes
            context[field.id] = value
    
    return values


def render_all_fields(fields_by_section: Dict[str, List[SimpleField]], 
                     sections_order: Optional[List[str]] = None,
                     initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Renderiza todos los campos organizados por secciones.
    
    Args:
        fields_by_section: Diccionario {seccion: [campos]}
        sections_order: Orden de las secciones (opcional)
        initial_context: Contexto inicial con valores
    
    Returns:
        Diccionario con todos los valores recolectados
    """
    context = initial_context.copy() if initial_context else {}
    all_values = {}
    
    # Determinar orden de secciones
    if sections_order:
        sections = [s for s in sections_order if s in fields_by_section]
        # Agregar secciones no listadas al final
        sections.extend([s for s in fields_by_section.keys() if s not in sections])
    else:
        sections = list(fields_by_section.keys())
    
    # Renderizar cada sección
    for section in sections:
        if section not in fields_by_section:
            continue
        
        section_values = render_section_fields(
            section, 
            fields_by_section[section],
            context
        )
        all_values.update(section_values)
        context.update(section_values)
    
    return all_values


# ==============================================================================
# VALIDACIÓN DE FORMULARIO
# ==============================================================================

def validate_form_data(fields: List[SimpleField], 
                      data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valida datos del formulario.
    
    Args:
        fields: Lista de definiciones de campos
        data: Datos introducidos por el usuario
    
    Returns:
        Tupla (es_válido, lista_de_errores)
    """
    errors = []
    
    for field in fields:
        # Verificar campos requeridos
        if field.requerido and field.id not in data:
            errors.append(f"Campo requerido faltante: {field.nombre}")
            continue
        
        if field.id not in data:
            continue
        
        value = data[field.id]
        
        # Validar rangos numéricos
        if field.tipo == "numero":
            try:
                num_value = float(value)
                if field.min is not None and num_value < field.min:
                    errors.append(f"{field.nombre}: valor mínimo es {field.min}")
                if field.max is not None and num_value > field.max:
                    errors.append(f"{field.nombre}: valor máximo es {field.max}")
            except (ValueError, TypeError):
                errors.append(f"{field.nombre}: debe ser un número")
        
        # Validar opciones de lista
        if field.tipo == "lista" and field.opciones:
            if value not in field.opciones:
                errors.append(f"{field.nombre}: valor no válido")
    
    is_valid = len(errors) == 0
    return is_valid, errors


# ==============================================================================
# UTILIDADES DE UI
# ==============================================================================

def show_validation_errors(errors: List[str]) -> None:
    """
    Muestra errores de validación en la UI.
    
    Args:
        errors: Lista de mensajes de error
    """
    if errors:
        st.error("**Errores de validación:**")
        for error in errors:
            st.write(f"- {error}")


def show_success_message(message: str) -> None:
    """
    Muestra mensaje de éxito en la UI.
    
    Args:
        message: Mensaje a mostrar
    """
    st.success(message)


def show_info_message(message: str) -> None:
    """
    Muestra mensaje informativo en la UI.
    
    Args:
        message: Mensaje a mostrar
    """
    st.info(message)


def create_download_button(file_path, button_label: str = "Descargar informe") -> None:
    """
    Crea un botón de descarga para un archivo.
    
    Args:
        file_path: Path al archivo
        button_label: Texto del botón
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        st.download_button(
            label=button_label,
            data=file_data,
            file_name=file_path.name,
            mime='application/octet-stream'
        )
    except Exception as e:
        st.error(f"Error creando botón de descarga: {e}")
