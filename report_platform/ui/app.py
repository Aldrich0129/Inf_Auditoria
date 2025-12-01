"""
App - Aplicación principal Streamlit

Interfaz web unificada que se adapta dinámicamente a los plugins disponibles.
"""

import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from report_platform.core.utils import setup_logger, get_outputs_dir, safe_filename
from report_platform.core.config_loader import get_fields_by_section, get_general_config
from report_platform.core.word_engine import render_word_report
from report_platform.core.ui_runtime import (
    render_field,
    render_conditional_variable,
    should_show_field_in_ui,
    validate_form_data,
    show_validation_errors,
    show_success_message,
)
from report_platform.ui.router import (
    list_available_reports,
    load_report_plugin,
    get_build_context_function,
    get_template_path,
    get_plugin_info,
)

logger = setup_logger(__name__)


# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================

st.set_page_config(
    page_title="Plataforma de Generación de Informes",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# ESTADO DE SESIÓN
# ==============================================================================

def init_session_state():
    """Inicializa el estado de sesión de Streamlit."""
    if 'selected_report' not in st.session_state:
        st.session_state.selected_report = None
    
    if 'plugin_config' not in st.session_state:
        st.session_state.plugin_config = None
    
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}


# ==============================================================================
# SELECCIÓN DE PLUGIN
# ==============================================================================

def render_report_selector():
    """Renderiza el selector de tipo de informe en el sidebar."""
    st.sidebar.title("📄 Plataforma de Informes")
    st.sidebar.markdown("---")
    
    # Obtener plugins disponibles
    available_reports = list_available_reports()
    
    if not available_reports:
        st.sidebar.error("No se encontraron plugins de informes")
        return None
    
    # Selector de informe
    report_names = [r.nombre for r in available_reports]
    report_ids = [r.id for r in available_reports]
    
    selected_name = st.sidebar.selectbox(
        "Seleccionar tipo de informe",
        options=report_names,
        key="report_selector"
    )
    
    # Obtener ID del informe seleccionado
    selected_idx = report_names.index(selected_name)
    selected_id = report_ids[selected_idx]
    
    # Mostrar información del plugin
    selected_manifest = available_reports[selected_idx]
    
    with st.sidebar.expander("ℹ️ Información del plugin"):
        st.write(f"**ID:** {selected_manifest.id}")
        st.write(f"**Versión:** {selected_manifest.version}")
        if selected_manifest.descripcion:
            st.write(f"**Descripción:** {selected_manifest.descripcion}")
        if selected_manifest.autor:
            st.write(f"**Autor:** {selected_manifest.autor}")
    
    return selected_id


# ==============================================================================
# RENDERIZADO DE FORMULARIO
# ==============================================================================

def render_conditional_variables_section(plugin_config: Dict[str, Any], 
                                        context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Renderiza las variables condicionales.
    
    Args:
        plugin_config: Configuración del plugin
        context: Contexto actual
    
    Returns:
        Diccionario con valores de variables condicionales
    """
    st.header("⚙️ Configuración del Informe")
    
    conditional_vars = plugin_config['conditional_variables']
    values = {}
    
    if not conditional_vars:
        st.info("Este informe no tiene variables condicionales")
        return values
    
    # Agrupar por sección
    vars_by_section = {}
    for var in conditional_vars:
        section = var.seccion or "General"
        if section not in vars_by_section:
            vars_by_section[section] = []
        vars_by_section[section].append(var)
    
    # Renderizar cada sección
    for section, variables in vars_by_section.items():
        with st.expander(f"📋 {section}", expanded=True):
            for var in variables:
                # Verificar dependencia
                if var.dependencia:
                    dep = var.dependencia
                    parent_value = context.get(dep.variable)
                    
                    if dep.valor and parent_value != dep.valor:
                        continue
                    if dep.valor_no and parent_value == dep.valor_no:
                        continue
                
                # Renderizar variable
                value = render_conditional_variable(var, context.get(var.id))
                if value is not None:
                    values[var.id] = value
                    context[var.id] = value
    
    return values


def render_simple_fields_section(plugin_config: Dict[str, Any], 
                                 context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Renderiza los campos simples organizados por secciones.
    
    Args:
        plugin_config: Configuración del plugin
        context: Contexto actual con variables condicionales
    
    Returns:
        Diccionario con valores de campos
    """
    st.header("📝 Datos del Informe")
    
    simple_fields = plugin_config['simple_fields']
    
    if not simple_fields:
        st.info("Este informe no tiene campos simples")
        return {}
    
    # Agrupar por sección
    fields_by_section = get_fields_by_section(simple_fields)
    
    # Obtener orden de secciones si está definido
    config_dir = plugin_config['config_dir']
    general_config = get_general_config(config_dir)
    sections_order = general_config.get('secciones_orden', [])
    
    # Determinar orden
    if sections_order:
        sections = [s for s in sections_order if s in fields_by_section]
        sections.extend([s for s in fields_by_section.keys() if s not in sections])
    else:
        sections = list(fields_by_section.keys())
    
    # Renderizar campos
    all_values = {}
    
    for section in sections:
        if section not in fields_by_section:
            continue
        
        with st.expander(f"📋 {section}", expanded=False):
            for field in fields_by_section[section]:
                # Verificar si debe mostrarse
                if not should_show_field_in_ui(field, context):
                    continue
                
                # Renderizar campo
                value = render_field(field, context.get(field.id))
                
                if value is not None:
                    all_values[field.id] = value
                    context[field.id] = value
    
    return all_values


# ==============================================================================
# GENERACIÓN DE INFORME
# ==============================================================================

def generate_report(plugin_config: Dict[str, Any], form_data: Dict[str, Any]) -> Optional[Path]:
    """
    Genera el informe usando el plugin y los datos del formulario.
    
    Args:
        plugin_config: Configuración del plugin
        form_data: Datos del formulario
    
    Returns:
        Path al archivo generado o None si hay error
    """
    try:
        # Obtener función build_context
        build_context = get_build_context_function(plugin_config)
        
        # Construir contexto
        logger.info("Construyendo contexto con build_context()...")
        context = build_context(form_data, plugin_config['config_dir'])
        
        # Obtener path de plantilla
        template_path = get_template_path(plugin_config)
        
        # Generar nombre de archivo
        manifest = plugin_config['manifest']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{manifest.id}_{timestamp}"
        
        # Renderizar informe
        logger.info("Renderizando informe...")
        output_path = render_word_report(template_path, context, output_filename)
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error generando informe: {e}")
        st.error(f"Error generando informe: {e}")
        return None


# ==============================================================================
# INTERFAZ PRINCIPAL
# ==============================================================================

def main():
    """Función principal de la aplicación."""
    init_session_state()
    
    # Título principal
    st.title("📄 Plataforma de Generación de Informes")
    st.markdown("Sistema modular para generación automática de documentos")
    st.markdown("---")
    
    # Seleccionar plugin
    selected_report_id = render_report_selector()
    
    if not selected_report_id:
        st.warning("Por favor, selecciona un tipo de informe en el menú lateral")
        st.stop()
    
    # Cargar plugin si cambió la selección
    if (st.session_state.selected_report != selected_report_id or 
        st.session_state.plugin_config is None):
        
        with st.spinner(f"Cargando configuración de {selected_report_id}..."):
            plugin_config = load_report_plugin(selected_report_id)
        
        if not plugin_config:
            st.error(f"Error cargando plugin: {selected_report_id}")
            st.stop()
        
        st.session_state.selected_report = selected_report_id
        st.session_state.plugin_config = plugin_config
        st.session_state.form_data = {}
        
        # Mostrar información del plugin
        plugin_info = get_plugin_info(plugin_config)
        st.success(f"✅ Plugin cargado: {plugin_info['nombre']} (v{plugin_info['version']})")
        
        with st.expander("📊 Estadísticas del plugin"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Campos", plugin_info['num_campos'])
            with col2:
                st.metric("Variables condicionales", plugin_info['num_condicionales'])
            with col3:
                st.metric("Bloques de texto", plugin_info['num_bloques'])
    
    plugin_config = st.session_state.plugin_config
    
    # Contexto para seguimiento de valores
    context = dict(st.session_state.form_data)
    
    # Renderizar variables condicionales
    cond_values = render_conditional_variables_section(plugin_config, context)
    context.update(cond_values)
    
    st.markdown("---")
    
    # Renderizar campos simples
    field_values = render_simple_fields_section(plugin_config, context)
    context.update(field_values)
    
    # Guardar datos en sesión
    st.session_state.form_data = context
    
    st.markdown("---")
    
    # Botón de generación
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Generar Informe", type="primary", use_container_width=True):
            
            # Validar formulario
            all_fields = plugin_config['simple_fields']
            is_valid, errors = validate_form_data(all_fields, context)
            
            if not is_valid:
                show_validation_errors(errors)
            else:
                # Generar informe
                with st.spinner("Generando informe..."):
                    output_path = generate_report(plugin_config, context)
                
                if output_path:
                    show_success_message(f"✅ Informe generado exitosamente")
                    
                    st.info(f"**Archivo:** `{output_path.name}`")
                    st.info(f"**Ubicación:** `{output_path}`")
                    
                    # Botón de descarga
                    try:
                        with open(output_path, 'rb') as f:
                            file_data = f.read()
                        
                        st.download_button(
                            label="📥 Descargar Informe",
                            data=file_data,
                            file_name=output_path.name,
                            mime='application/octet-stream',
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error al preparar descarga: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Plataforma de Generación de Informes v1.0 | "
        "Desarrollado por Jimmy - Forvis Mazars España"
        "</div>",
        unsafe_allow_html=True
    )


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================

if __name__ == "__main__":
    main()
