"""
App - Aplicación principal Streamlit

Interfaz web unificada que se adapta dinámicamente a los plugins disponibles.
Incluye funcionalidad de metadatos para guardar y cargar configuraciones.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

import streamlit as st

# Ensure the project root is in the Python path when running directly with Streamlit
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
from report_platform.core.metadata import (
    create_metadata,
    save_metadata,
    load_all_metadata,
    load_metadata_by_report_id,
    get_metadata_summary,
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

    if 'work_mode' not in st.session_state:
        st.session_state.work_mode = 'nuevo'  # 'nuevo' o 'cargar'

    if 'loaded_metadata_id' not in st.session_state:
        st.session_state.loaded_metadata_id = None


# ==============================================================================
# SELECCIÓN DE PLUGIN Y MODO DE TRABAJO
# ==============================================================================

def render_sidebar():
    """Renderiza el sidebar con selección de informe y modo de trabajo."""
    st.sidebar.title("📄 Plataforma de Informes")
    st.sidebar.markdown("---")

    # Selector de modo de trabajo
    st.sidebar.subheader("🔧 Modo de trabajo")
    work_mode = st.sidebar.radio(
        "Selecciona el modo",
        options=['nuevo', 'cargar'],
        format_func=lambda x: "✨ Crear nuevo informe" if x == 'nuevo' else "📂 Cargar desde metadatos",
        key="work_mode_selector"
    )

    # Actualizar modo si cambió
    if st.session_state.work_mode != work_mode:
        st.session_state.work_mode = work_mode
        st.session_state.form_data = {}
        st.session_state.loaded_metadata_id = None
        st.rerun()

    st.sidebar.markdown("---")

    # Obtener plugins disponibles
    available_reports = list_available_reports()

    if not available_reports:
        st.sidebar.error("No se encontraron plugins de informes")
        return None, None

    # Modo: Crear nuevo informe
    if st.session_state.work_mode == 'nuevo':
        st.sidebar.subheader("📋 Seleccionar tipo de informe")

        report_names = [r.nombre for r in available_reports]
        report_ids = [r.id for r in available_reports]

        selected_name = st.sidebar.selectbox(
            "Tipo de informe",
            options=report_names,
            key="report_selector_nuevo"
        )

        selected_idx = report_names.index(selected_name)
        selected_id = report_ids[selected_idx]
        selected_manifest = available_reports[selected_idx]

        # Mostrar info del plugin
        with st.sidebar.expander("ℹ️ Información del plugin"):
            st.write(f"**ID:** {selected_manifest.id}")
            st.write(f"**Versión:** {selected_manifest.version}")
            if selected_manifest.descripcion:
                st.write(f"**Descripción:** {selected_manifest.descripcion}")
            if selected_manifest.autor:
                st.write(f"**Autor:** {selected_manifest.autor}")

        return selected_id, None

    # Modo: Cargar desde metadatos
    else:
        st.sidebar.subheader("📂 Cargar desde metadatos")

        # Cargar todos los metadatos
        all_metadata = load_all_metadata()

        if not all_metadata:
            st.sidebar.warning("No hay metadatos guardados")
            return None, None

        # Primero seleccionar tipo de informe
        report_ids_with_meta = list(set([m.report_id for m in all_metadata]))
        report_names_map = {r.id: r.nombre for r in available_reports}

        selected_report_id = st.sidebar.selectbox(
            "Tipo de informe",
            options=report_ids_with_meta,
            format_func=lambda rid: report_names_map.get(rid, rid),
            key="report_selector_cargar"
        )

        # Filtrar metadatos por tipo de informe
        filtered_metadata = [m for m in all_metadata if m.report_id == selected_report_id]

        if not filtered_metadata:
            st.sidebar.warning(f"No hay metadatos para '{selected_report_id}'")
            return None, None

        # Seleccionar registro específico
        metadata_options = {get_metadata_summary(m): m.id for m in filtered_metadata}

        selected_summary = st.sidebar.selectbox(
            "Seleccionar configuración",
            options=list(metadata_options.keys()),
            key="metadata_selector"
        )

        selected_metadata_id = metadata_options[selected_summary]

        # Encontrar el metadata completo
        selected_metadata = next((m for m in filtered_metadata if m.id == selected_metadata_id), None)

        if selected_metadata:
            with st.sidebar.expander("📊 Detalles del metadata"):
                st.write(f"**Generado:** {selected_metadata.timestamp}")
                st.write(f"**Por:** {selected_metadata.generated_by}")
                st.write(f"**Archivo:** {selected_metadata.output_filename}")
                if selected_metadata.description:
                    st.write(f"**Descripción:** {selected_metadata.description}")

        return selected_report_id, selected_metadata


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

def generate_report(plugin_config: Dict[str, Any], form_data: Dict[str, Any],
                   save_meta: bool = True) -> Optional[Path]:
    """
    Genera el informe usando el plugin y los datos del formulario.

    Args:
        plugin_config: Configuración del plugin
        form_data: Datos del formulario
        save_meta: Si debe guardar metadatos

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

        # Guardar metadatos si se solicita
        if save_meta:
            metadata = create_metadata(
                report_id=manifest.id,
                report_name=manifest.nombre,
                template_version=manifest.version,
                input_data=form_data,
                output_path=output_path,
                generated_by="usuario",
                description=None
            )
            save_metadata(metadata)
            logger.info(f"Metadatos guardados: {metadata.id}")

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

    # Renderizar sidebar y obtener selección
    selected_report_id, selected_metadata = render_sidebar()

    if not selected_report_id:
        st.warning("Por favor, selecciona un tipo de informe en el menú lateral")
        st.stop()

    # Cargar plugin si cambió la selección o es nueva
    if (st.session_state.selected_report != selected_report_id or
        st.session_state.plugin_config is None):

        with st.spinner(f"Cargando configuración de {selected_report_id}..."):
            plugin_config = load_report_plugin(selected_report_id)

        if not plugin_config:
            st.error(f"Error cargando plugin: {selected_report_id}")
            st.stop()

        st.session_state.selected_report = selected_report_id
        st.session_state.plugin_config = plugin_config

        # Si estamos en modo cargar y tenemos metadata, prellenar form_data
        if st.session_state.work_mode == 'cargar' and selected_metadata:
            st.session_state.form_data = selected_metadata.input_data.copy()
            st.session_state.loaded_metadata_id = selected_metadata.id
        else:
            st.session_state.form_data = {}
            st.session_state.loaded_metadata_id = None

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

    # Si estamos en modo cargar y el metadata cambió, actualizar form_data
    elif (st.session_state.work_mode == 'cargar' and selected_metadata and
          st.session_state.loaded_metadata_id != selected_metadata.id):
        st.session_state.form_data = selected_metadata.input_data.copy()
        st.session_state.loaded_metadata_id = selected_metadata.id
        st.info("✅ Datos cargados desde metadatos")

    plugin_config = st.session_state.plugin_config

    # Mostrar indicador si estamos en modo cargar
    if st.session_state.work_mode == 'cargar' and st.session_state.loaded_metadata_id:
        st.info(f"📂 **Modo:** Cargado desde metadatos (ID: {st.session_state.loaded_metadata_id[:20]}...)")

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
                    output_path = generate_report(plugin_config, context, save_meta=True)

                if output_path:
                    show_success_message(f"✅ Informe generado exitosamente")

                    st.info(f"**Archivo:** `{output_path.name}`")
                    st.info(f"**Ubicación:** `{output_path}`")
                    st.success("💾 Metadatos guardados para futura reutilización")

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
        "Plataforma de Generación de Informes v2.0 | "
        "Desarrollado por Jimmy - Forvis Mazars España | "
        "Con funcionalidad de metadatos para reutilización"
        "</div>",
        unsafe_allow_html=True
    )


# ==============================================================================
# PUNTO DE ENTRADA
# ==============================================================================

if __name__ == "__main__":
    main()
