"""
Conditions Engine - Motor de evaluación de expresiones condicionales

Evalúa expresiones lógicas de forma segura para determinar qué bloques
de texto o campos deben mostrarse según el contexto.
"""

from typing import Dict, Any, List, Optional
from report_platform.core.utils import setup_logger
from report_platform.core.schema_models import BlockDefinition, BlockRule

logger = setup_logger(__name__)


# ==============================================================================
# EVALUACIÓN SEGURA DE CONDICIONES
# ==============================================================================

def evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
    """
    Evalúa una condición en un contexto dado de forma segura.
    
    Args:
        condition: Expresión de condición como string (ej: "tipo_opinion == 'favorable'")
        context: Diccionario con las variables disponibles
    
    Returns:
        True si la condición se cumple, False en caso contrario
    
    Ejemplo:
        >>> ctx = {'tipo_opinion': 'favorable', 'tipo_cuentas': 'normales'}
        >>> evaluate_condition("tipo_opinion == 'favorable'", ctx)
        True
    """
    try:
        # Entorno seguro para eval: solo valores del contexto y constantes básicas
        safe_globals = {
            '__builtins__': {},
            'True': True,
            'False': False,
            'None': None,
        }
        
        # Agregar variables del contexto al entorno
        safe_locals = dict(context)
        
        # Evaluar la expresión
        result = eval(condition, safe_globals, safe_locals)
        return bool(result)
    
    except Exception as e:
        logger.warning(f"Error evaluando condición '{condition}': {e}")
        return False


# ==============================================================================
# EVALUACIÓN DE MÚLTIPLES CONDICIONES
# ==============================================================================

def evaluate_any(conditions: List[str], context: Dict[str, Any]) -> bool:
    """
    Evalúa múltiples condiciones con lógica OR.
    
    Args:
        conditions: Lista de expresiones de condición
        context: Diccionario con las variables
    
    Returns:
        True si al menos una condición se cumple
    """
    return any(evaluate_condition(cond, context) for cond in conditions)


def evaluate_all(conditions: List[str], context: Dict[str, Any]) -> bool:
    """
    Evalúa múltiples condiciones con lógica AND.
    
    Args:
        conditions: Lista de expresiones de condición
        context: Diccionario con las variables
    
    Returns:
        True si todas las condiciones se cumplen
    """
    return all(evaluate_condition(cond, context) for cond in conditions)


# ==============================================================================
# EVALUACIÓN DE DEPENDENCIAS DE CAMPOS
# ==============================================================================

def should_show_field(field_id: str, dependency_condition: Optional[str], 
                     context: Dict[str, Any]) -> bool:
    """
    Determina si un campo debe mostrarse según su condición de dependencia.
    
    Args:
        field_id: ID del campo
        dependency_condition: Expresión de condición de dependencia
        context: Contexto actual
    
    Returns:
        True si el campo debe mostrarse
    """
    # Si no hay condición de dependencia, siempre se muestra
    if not dependency_condition:
        return True
    
    # Evaluar la condición
    return evaluate_condition(dependency_condition, context)


# ==============================================================================
# PROCESAMIENTO DE BLOQUES DE TEXTO
# ==============================================================================

def evaluate_block(block: BlockDefinition, context: Dict[str, Any]) -> Optional[str]:
    """
    Evalúa un bloque de texto y devuelve la plantilla de la primera regla que coincida.
    
    Args:
        block: Definición del bloque
        context: Contexto con variables
    
    Returns:
        Plantilla (string) de la regla que coincidió, o None si ninguna coincide
    """
    for rule in block.reglas:
        if evaluate_condition(rule.cuando, context):
            logger.debug(f"Bloque '{block.id}': condición '{rule.cuando}' = True")
            return rule.plantilla
    
    logger.debug(f"Bloque '{block.id}': ninguna condición coincidió")
    return None


def evaluate_all_blocks(blocks: List[BlockDefinition], 
                       context: Dict[str, Any]) -> Dict[str, str]:
    """
    Evalúa todos los bloques de texto y devuelve un diccionario con las plantillas.
    
    Args:
        blocks: Lista de definiciones de bloques
        context: Contexto con variables
    
    Returns:
        Diccionario {block_id: plantilla_seleccionada}
    """
    results = {}
    
    for block in blocks:
        plantilla = evaluate_block(block, context)
        if plantilla is not None:
            results[block.id] = plantilla
        else:
            # Si ninguna regla coincide, usar cadena vacía
            results[block.id] = ""
    
    return results


# ==============================================================================
# VALIDACIÓN DE EXPRESIONES
# ==============================================================================

def is_valid_expression(expression: str) -> bool:
    """
    Valida que una expresión sea sintácticamente correcta.
    
    Args:
        expression: Expresión a validar
    
    Returns:
        True si la expresión es válida sintácticamente
    """
    try:
        compile(expression, '<string>', 'eval')
        return True
    except SyntaxError:
        return False


def get_variables_in_expression(expression: str) -> List[str]:
    """
    Extrae las variables referenciadas en una expresión.
    
    Args:
        expression: Expresión a analizar
    
    Returns:
        Lista de nombres de variables
    
    Nota: Esta es una implementación simplificada que puede no detectar
    todos los casos complejos.
    """
    import re
    
    # Pattern para identificar identificadores Python
    pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    
    # Encontrar todos los identificadores
    identifiers = set(re.findall(pattern, expression))
    
    # Filtrar keywords y constantes
    keywords = {'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is'}
    variables = [v for v in identifiers if v not in keywords]
    
    return variables


# ==============================================================================
# CONSTRUCCIÓN DE EXPRESIONES CONDICIONALES
# ==============================================================================

def build_condition_from_dict(cond_dict: Dict[str, Any]) -> str:
    """
    Construye una expresión de condición desde un diccionario estructurado.
    
    Args:
        cond_dict: Diccionario con estructura de condición
    
    Returns:
        Expresión como string
    
    Ejemplo:
        >>> cond = {'campo': 'tipo_opinion', 'igual': 'favorable'}
        >>> build_condition_from_dict(cond)
        "tipo_opinion == 'favorable'"
    """
    # Caso simple: campo == valor
    if 'campo' in cond_dict and 'igual' in cond_dict:
        campo = cond_dict['campo']
        valor = cond_dict['igual']
        return f"{campo} == '{valor}'"
    
    # Caso: campo != valor
    if 'campo' in cond_dict and 'no_igual' in cond_dict:
        campo = cond_dict['campo']
        valor = cond_dict['no_igual']
        return f"{campo} != '{valor}'"
    
    # Caso: AND de múltiples condiciones
    if 'and' in cond_dict:
        subcondiciones = [build_condition_from_dict(c) for c in cond_dict['and']]
        return f"({' and '.join(subcondiciones)})"
    
    # Caso: OR de múltiples condiciones
    if 'or' in cond_dict:
        subcondiciones = [build_condition_from_dict(c) for c in cond_dict['or']]
        return f"({' or '.join(subcondiciones)})"
    
    logger.warning(f"No se pudo construir condición desde: {cond_dict}")
    return "True"


# ==============================================================================
# UTILIDADES DE DEBUG
# ==============================================================================

def debug_condition_evaluation(condition: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evalúa una condición y devuelve información de debug.
    
    Args:
        condition: Expresión a evaluar
        context: Contexto de variables
    
    Returns:
        Diccionario con resultado y detalles
    """
    result = {
        'condition': condition,
        'is_valid': is_valid_expression(condition),
        'variables_used': get_variables_in_expression(condition),
        'result': None,
        'error': None
    }
    
    try:
        result['result'] = evaluate_condition(condition, context)
    except Exception as e:
        result['error'] = str(e)
    
    return result
