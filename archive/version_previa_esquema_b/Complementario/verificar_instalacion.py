#!/usr/bin/env python3
"""
Script de Verificación de Instalación

Verifica que la plataforma esté correctamente instalada y configurada.
"""

import sys
from pathlib import Path
import importlib.util


def check_python_version():
    """Verifica la versión de Python."""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("   ❌ Se requiere Python 3.11 o superior")
        return False
    print("   ✅ Versión correcta")
    return True


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    dependencies = [
        "streamlit",
        "pydantic",
        "jinja2",
        "yaml",
        "docx",
        "dateutil",
    ]
    
    print("\n📦 Dependencias:")
    all_ok = True
    
    for dep in dependencies:
        # Casos especiales de nombres de módulos
        module_name = dep
        if dep == "yaml":
            module_name = "yaml"
        elif dep == "docx":
            module_name = "docx"
        
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"   ❌ {dep} - NO INSTALADO")
            all_ok = False
        else:
            print(f"   ✅ {dep}")
    
    return all_ok


def check_structure():
    """Verifica que la estructura de archivos sea correcta."""
    print("\n📁 Estructura de archivos:")
    
    required_paths = [
        "report_platform/__init__.py",
        "report_platform/core/__init__.py",
        "report_platform/core/utils.py",
        "report_platform/core/schema_models.py",
        "report_platform/core/config_loader.py",
        "report_platform/core/conditions_engine.py",
        "report_platform/core/word_engine.py",
        "report_platform/core/tables_engine.py",
        "report_platform/core/ui_runtime.py",
        "report_platform/reports/__init__.py",
        "report_platform/reports/informe_auditoria/__init__.py",
        "report_platform/reports/informe_auditoria/manifest.yaml",
        "report_platform/reports/informe_auditoria/logic.py",
        "report_platform/reports/informe_auditoria/templates/plantilla_informe.txt",
        "report_platform/reports/informe_auditoria/config/variables_simples.yaml",
        "report_platform/reports/informe_auditoria/config/variables_condicionales.yaml",
        "report_platform/reports/informe_auditoria/config/bloques_texto.yaml",
        "report_platform/ui/__init__.py",
        "report_platform/ui/router.py",
        "report_platform/ui/app.py",
        "requirements.txt",
    ]
    
    all_ok = True
    for path_str in required_paths:
        path = Path(path_str)
        if path.exists():
            print(f"   ✅ {path_str}")
        else:
            print(f"   ❌ {path_str} - NO ENCONTRADO")
            all_ok = False
    
    return all_ok


def check_imports():
    """Verifica que los módulos de la plataforma se puedan importar."""
    print("\n📥 Importación de módulos:")
    
    modules = [
        "report_platform",
        "report_platform.core.utils",
        "report_platform.core.schema_models",
        "report_platform.core.config_loader",
        "report_platform.core.conditions_engine",
        "report_platform.ui.router",
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module} - ERROR: {e}")
            all_ok = False
    
    return all_ok


def check_plugin():
    """Verifica que el plugin de auditoría esté correctamente configurado."""
    print("\n🔌 Plugin de informe de auditoría:")
    
    try:
        from report_platform.ui.router import list_available_reports
        
        reports = list_available_reports()
        
        if not reports:
            print("   ❌ No se encontraron plugins")
            return False
        
        print(f"   ✅ {len(reports)} plugin(s) encontrado(s)")
        
        for report in reports:
            print(f"      • {report.nombre} (ID: {report.id}, v{report.version})")
        
        return True
    
    except Exception as e:
        print(f"   ❌ Error al cargar plugins: {e}")
        return False


def main():
    """Función principal de verificación."""
    print("="*70)
    print("VERIFICACIÓN DE INSTALACIÓN - PLATAFORMA DE GENERACIÓN DE INFORMES")
    print("="*70)
    
    checks = [
        ("Versión de Python", check_python_version),
        ("Dependencias", check_dependencies),
        ("Estructura de archivos", check_structure),
        ("Importación de módulos", check_imports),
        ("Plugin de auditoría", check_plugin),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error en {name}: {e}")
            results.append(False)
    
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPruebas pasadas: {passed}/{total}")
    
    if all(results):
        print("\n✅ ¡TODO CORRECTO! La plataforma está lista para usar.")
        print("\nPara ejecutar la aplicación:")
        print("  streamlit run report_platform/ui/app.py")
        return 0
    else:
        print("\n❌ Hay problemas con la instalación.")
        print("\nPor favor, revisa los errores arriba y consulta:")
        print("  - INSTRUCCIONES_INSTALACION.md")
        print("  - ESTRUCTURA_PROYECTO.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
