"""
Router - Descubrimiento y carga de plugins de informes

Escanea el directorio de reports y carga dinámicamente los plugins disponibles.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from report_platform.core.utils import setup_logger, get_reports_dir
from report_platform.core.config_loader import (
    load_manifest, 
    load_plugin_config
)
from report_platform.core.schema_models import Manifest

logger = setup_logger(__name__)


# ==============================================================================
# DESCUBRIMIENTO DE PLUGINS
# ==============================================================================

def list_available_reports() -> List[Manifest]:
    """
    Escanea el directorio reports/ y devuelve la lista de plugins disponibles.
    
    Returns:
        Lista de Manifests de plugins válidos
    """
    reports_dir = get_reports_dir()
    
    if not reports_dir.exists():
        logger.error(f"Directorio de reports no encontrado: {reports_dir}")
        return []
    
    plugins = []
    
    # Escanear subdirectorios
    for plugin_dir in reports_dir.iterdir():
        if not plugin_dir.is_dir():
            continue
        
        # Ignorar directorios que empiezan con _ o .
        if plugin_dir.name.startswith('_') or plugin_dir.name.startswith('.'):
            continue
        
        # Intentar cargar manifest
        manifest = load_manifest(plugin_dir)
        if manifest:
            plugins.append(manifest)
            logger.info(f"Plugin encontrado: {manifest.nombre} (ID: {manifest.id})")
    
    logger.info(f"Total de plugins disponibles: {len(plugins)}")
    return plugins


# ==============================================================================
# CARGA DE PLUGIN ESPECÍFICO
# ==============================================================================

def load_report_plugin(report_id: str) -> Optional[Dict[str, Any]]:
    """
    Carga la configuración completa de un plugin específico.
    
    Args:
        report_id: ID del plugin a cargar
    
    Returns:
        Diccionario con toda la configuración del plugin o None si no se encuentra
    """
    reports_dir = get_reports_dir()
    plugin_dir = reports_dir / report_id
    
    if not plugin_dir.exists():
        logger.error(f"Plugin no encontrado: {report_id}")
        return None
    
    # Cargar configuración completa
    config = load_plugin_config(plugin_dir)
    
    if not config:
        logger.error(f"Error cargando configuración de plugin: {report_id}")
        return None
    
    # Cargar el módulo logic.py del plugin
    try:
        logic_module = import_plugin_logic(plugin_dir)
        config['logic_module'] = logic_module
    except Exception as e:
        logger.error(f"Error importando lógica del plugin {report_id}: {e}")
        return None
    
    return config


# ==============================================================================
# IMPORTACIÓN DINÁMICA DE LÓGICA
# ==============================================================================

def import_plugin_logic(plugin_dir: Path) -> Any:
    """
    Importa dinámicamente el módulo logic.py de un plugin.
    
    Args:
        plugin_dir: Directorio del plugin
    
    Returns:
        Módulo importado
    """
    import importlib.util
    import sys
    
    logic_path = plugin_dir / "logic.py"
    
    if not logic_path.exists():
        raise FileNotFoundError(f"No se encontró logic.py en {plugin_dir}")
    
    # Crear spec del módulo
    spec = importlib.util.spec_from_file_location(
        f"plugin_{plugin_dir.name}_logic", 
        logic_path
    )
    
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo crear spec para {logic_path}")
    
    # Cargar módulo
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    
    return module


# ==============================================================================
# OBTENCIÓN DE FUNCIÓN BUILD_CONTEXT
# ==============================================================================

def get_build_context_function(plugin_config: Dict[str, Any]):
    """
    Obtiene la función build_context de un plugin.
    
    Args:
        plugin_config: Configuración cargada del plugin
    
    Returns:
        Función build_context del plugin
    """
    logic_module = plugin_config.get('logic_module')
    
    if not logic_module:
        raise ValueError("Plugin no tiene módulo de lógica cargado")
    
    if not hasattr(logic_module, 'build_context'):
        raise AttributeError("El módulo logic.py no tiene función 'build_context'")
    
    return logic_module.build_context


# ==============================================================================
# OBTENCIÓN DE PATH DE PLANTILLA
# ==============================================================================

def get_template_path(plugin_config: Dict[str, Any]) -> Path:
    """
    Obtiene el path completo a la plantilla del plugin.
    
    Args:
        plugin_config: Configuración cargada del plugin
    
    Returns:
        Path a la plantilla
    """
    manifest = plugin_config['manifest']
    plugin_dir = plugin_config['plugin_dir']
    
    template_path = plugin_dir / manifest.paths.template
    
    if not template_path.exists():
        raise FileNotFoundError(f"Plantilla no encontrada: {template_path}")
    
    return template_path


# ==============================================================================
# UTILIDADES
# ==============================================================================

def get_plugin_info(plugin_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae información resumida de un plugin.
    
    Args:
        plugin_config: Configuración cargada del plugin
    
    Returns:
        Diccionario con información del plugin
    """
    manifest = plugin_config['manifest']
    
    return {
        'id': manifest.id,
        'nombre': manifest.nombre,
        'version': manifest.version,
        'descripcion': manifest.descripcion,
        'autor': manifest.autor,
        'num_campos': len(plugin_config['simple_fields']),
        'num_condicionales': len(plugin_config['conditional_variables']),
        'num_bloques': len(plugin_config['text_blocks']),
    }


def validate_plugin_structure(plugin_dir: Path) -> tuple[bool, List[str]]:
    """
    Valida que un plugin tenga la estructura correcta.
    
    Args:
        plugin_dir: Directorio del plugin
    
    Returns:
        Tupla (es_válido, lista_de_errores)
    """
    errors = []
    
    # Verificar manifest.yaml
    if not (plugin_dir / "manifest.yaml").exists():
        errors.append("Falta manifest.yaml")
    
    # Verificar logic.py
    if not (plugin_dir / "logic.py").exists():
        errors.append("Falta logic.py")
    
    # Verificar directorio templates
    if not (plugin_dir / "templates").exists():
        errors.append("Falta directorio templates/")
    
    # Verificar directorio config
    if not (plugin_dir / "config").exists():
        errors.append("Falta directorio config/")
    
    is_valid = len(errors) == 0
    return is_valid, errors
