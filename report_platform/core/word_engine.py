"""
Word Engine - Motor de renderizado de documentos Word

Genera documentos Word a partir de plantillas con variables Jinja2.
Implementación placeholder que puede extenderse para soportar
renderizado completo de Word con formato preservado.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, BaseLoader
from report_platform.core.utils import setup_logger, get_outputs_dir, safe_filename

logger = setup_logger(__name__)


# ==============================================================================
# RENDERIZADO BÁSICO DE PLANTILLAS
# ==============================================================================

def render_template_string(template_content: str, context: Dict[str, Any]) -> str:
    """
    Renderiza una plantilla como string con Jinja2.
    
    Args:
        template_content: Contenido de la plantilla
        context: Diccionario con variables
    
    Returns:
        Texto renderizado
    """
    try:
        env = Environment(loader=BaseLoader())
        template = env.from_string(template_content)
        return template.render(**context)
    except Exception as e:
        logger.error(f"Error renderizando plantilla: {e}")
        return ""


# ==============================================================================
# RENDERIZADO DE DOCUMENTOS WORD (PLACEHOLDER)
# ==============================================================================

def render_word_report(template_path: Path, context: Dict[str, Any], 
                      output_filename: str) -> Optional[Path]:
    """
    Renderiza un informe Word desde una plantilla.
    
    NOTA: Esta es una implementación placeholder. Para renderizado completo
    de Word con preservación de formato, se recomienda usar bibliotecas como:
    - python-docx-template
    - docxtpl
    - mailmerge
    
    Args:
        template_path: Path a la plantilla Word
        context: Diccionario con todas las variables
        output_filename: Nombre del archivo de salida
    
    Returns:
        Path al archivo generado o None si hay error
    """
    logger.info(f"Renderizando informe desde: {template_path}")
    
    try:
        # Verificar que la plantilla existe
        if not template_path.exists():
            logger.error(f"Plantilla no encontrada: {template_path}")
            return None
        
        # Obtener directorio de salida
        output_dir = get_outputs_dir()
        
        # Nombre seguro del archivo
        safe_name = safe_filename(output_filename)
        if not safe_name.endswith('.docx'):
            safe_name += '.docx'
        
        output_path = output_dir / safe_name
        
        # TODO: Implementar renderizado real de Word
        # Por ahora, generamos un archivo de texto con el contexto renderizado
        
        # Leer plantilla como texto
        with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
            template_content = f.read()
        
        # Renderizar con Jinja2
        rendered_content = render_template_string(template_content, context)
        
        # Guardar como texto (placeholder)
        with open(output_path.with_suffix('.txt'), 'w', encoding='utf-8') as f:
            f.write(rendered_content)
        
        logger.info(f"Informe generado (placeholder): {output_path.with_suffix('.txt')}")
        logger.warning("NOTA: Actualmente se genera un archivo .txt. " 
                      "Para generación real de Word, implementar con python-docx-template")
        
        return output_path.with_suffix('.txt')
    
    except Exception as e:
        logger.error(f"Error generando informe: {e}")
        return None


# ==============================================================================
# RENDERIZADO AVANZADO (FUTURO)
# ==============================================================================

def render_word_with_docxtpl(template_path: Path, context: Dict[str, Any], 
                             output_path: Path) -> bool:
    """
    Renderiza documento Word usando docxtpl (implementación futura).
    
    Esta función es un placeholder para una implementación futura que use
    la biblioteca docxtpl para renderizado completo de Word con formato.
    
    Args:
        template_path: Path a la plantilla Word
        context: Diccionario con variables
        output_path: Path del archivo de salida
    
    Returns:
        True si se generó correctamente
    """
    logger.warning("render_word_with_docxtpl: Función no implementada aún")
    return False


def render_word_with_python_docx(template_path: Path, context: Dict[str, Any], 
                                 output_path: Path) -> bool:
    """
    Renderiza documento Word usando python-docx (implementación futura).
    
    Esta función es un placeholder para una implementación futura que use
    python-docx para manipulación directa del documento.
    
    Args:
        template_path: Path a la plantilla Word
        context: Diccionario con variables
        output_path: Path del archivo de salida
    
    Returns:
        True si se generó correctamente
    """
    logger.warning("render_word_with_python_docx: Función no implementada aún")
    return False


# ==============================================================================
# VALIDACIÓN DE PLANTILLAS
# ==============================================================================

def validate_template(template_path: Path) -> bool:
    """
    Valida que una plantilla Word sea accesible.
    
    Args:
        template_path: Path a la plantilla
    
    Returns:
        True si la plantilla es válida
    """
    if not template_path.exists():
        logger.error(f"Plantilla no encontrada: {template_path}")
        return False
    
    if not template_path.is_file():
        logger.error(f"La ruta no es un archivo: {template_path}")
        return False
    
    # TODO: Agregar validaciones adicionales (formato Word, sintaxis Jinja2, etc.)
    
    return True


def get_template_variables(template_path: Path) -> list:
    """
    Extrae las variables utilizadas en una plantilla.
    
    Args:
        template_path: Path a la plantilla
    
    Returns:
        Lista de nombres de variables encontradas
    """
    import re
    
    try:
        with open(template_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Pattern para {{ variable }}
        pattern = r'\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}'
        variables = set(re.findall(pattern, content))
        
        return sorted(list(variables))
    
    except Exception as e:
        logger.error(f"Error extrayendo variables de plantilla: {e}")
        return []


# ==============================================================================
# UTILIDADES
# ==============================================================================

def create_sample_template(output_path: Path, variables: list) -> bool:
    """
    Crea una plantilla de ejemplo con las variables proporcionadas.
    
    Args:
        output_path: Path donde guardar la plantilla
        variables: Lista de nombres de variables
    
    Returns:
        True si se creó correctamente
    """
    try:
        content = "# Plantilla de Ejemplo\n\n"
        for var in variables:
            content += f"{{ {var} }}\n\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Plantilla de ejemplo creada: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error creando plantilla de ejemplo: {e}")
        return False
