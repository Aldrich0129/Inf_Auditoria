"""
Utils - Utilidades generales de la plataforma

Funciones auxiliares para logging, manejo de paths y otras operaciones comunes.
"""

import logging
from pathlib import Path
from typing import Optional
import sys


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura y devuelve un logger con formato estándar.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (default: INFO)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formato del log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_project_root() -> Path:
    """
    Obtiene el directorio raíz del proyecto.
    
    Returns:
        Path al directorio raíz (donde está report_platform/)
    """
    # Desde este archivo (core/utils.py), subir dos niveles
    return Path(__file__).parent.parent.parent


def get_reports_dir() -> Path:
    """
    Obtiene el directorio de plugins de informes.
    
    Returns:
        Path al directorio reports/
    """
    return get_project_root() / "report_platform" / "reports"


def get_outputs_dir() -> Path:
    """
    Obtiene (y crea si no existe) el directorio de salida.
    
    Returns:
        Path al directorio de outputs
    """
    output_dir = Path("/mnt/user-data/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def safe_filename(filename: str) -> str:
    """
    Convierte un string en un nombre de archivo seguro.
    
    Args:
        filename: Nombre de archivo original
    
    Returns:
        Nombre de archivo sanitizado
    """
    # Reemplazar caracteres problemáticos
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limitar longitud
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()


def load_text_file(filepath: Path, encoding: str = 'utf-8') -> Optional[str]:
    """
    Carga un archivo de texto de forma segura.
    
    Args:
        filepath: Path al archivo
        encoding: Codificación del archivo
    
    Returns:
        Contenido del archivo o None si hay error
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger = setup_logger(__name__)
        logger.error(f"Error leyendo archivo {filepath}: {e}")
        return None


def ensure_directory(directory: Path) -> bool:
    """
    Asegura que un directorio existe, creándolo si es necesario.
    
    Args:
        directory: Path al directorio
    
    Returns:
        True si el directorio existe o fue creado exitosamente
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger = setup_logger(__name__)
        logger.error(f"Error creando directorio {directory}: {e}")
        return False
