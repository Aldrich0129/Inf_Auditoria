# 🚀 Guía de Instalación y Puesta en Marcha

## Requisitos Previos

- **Python 3.11 o superior**
- **pip** (gestor de paquetes de Python)
- **git** (opcional, para control de versiones)

## Paso 1: Estructura de Archivos

Asegúrate de tener la siguiente estructura en tu directorio de trabajo:

```
tu_proyecto/
├── README.md
├── requirements.txt
└── report_platform/
    ├── __init__.py
    ├── core/
    ├── reports/
    └── ui/
```

## Paso 2: Crear Entorno Virtual (Recomendado)

### En Windows:

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

### En macOS/Linux:

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

## Paso 3: Instalar Dependencias

```bash
# Instalar todas las dependencias del proyecto
pip install -r requirements.txt
```

**Lista de dependencias instaladas:**
- streamlit
- pydantic
- python-docx
- jinja2
- pyyaml
- python-dateutil
- colorlog

## Paso 4: Verificar Instalación

Verifica que todos los módulos se hayan instalado correctamente:

```bash
python -c "import streamlit; import pydantic; import jinja2; import yaml; print('✅ Todas las dependencias instaladas correctamente')"
```

## Paso 5: Ejecutar la Aplicación

Desde el directorio raíz del proyecto (donde está `report_platform/`):

```bash
streamlit run report_platform/ui/app.py
```

**Resultado esperado:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

## Paso 6: Usar la Aplicación

1. **Abre tu navegador** en `http://localhost:8501`

2. **Selecciona un tipo de informe** en el menú lateral

3. **Completa el formulario:**
   - Configuración del informe (variables condicionales)
   - Datos del informe (campos simples)

4. **Genera el informe:**
   - Click en "🚀 Generar Informe"
   - Descarga el archivo generado

## Solución de Problemas Comunes

### Error: "Module not found"

```bash
# Asegúrate de estar en el directorio correcto
pwd  # Debes estar donde está report_platform/

# Verifica que Python encuentre el módulo
python -c "import report_platform; print('OK')"
```

### Error: "Streamlit command not found"

```bash
# Verifica que streamlit esté instalado
pip list | grep streamlit

# Si no está, instálalo
pip install streamlit
```

### Error: "Port already in use"

```bash
# Usa un puerto diferente
streamlit run report_platform/ui/app.py --server.port 8502
```

### Error al cargar plugins

```bash
# Verifica que los plugins tengan la estructura correcta
ls -la report_platform/reports/informe_auditoria/

# Debe mostrar:
# - manifest.yaml
# - logic.py
# - templates/
# - config/
```

## Configuración Avanzada

### Cambiar Puerto por Defecto

Crea un archivo `.streamlit/config.toml` en el directorio raíz:

```toml
[server]
port = 8502
```

### Modo de Desarrollo

Para desarrollo con auto-reload:

```bash
streamlit run report_platform/ui/app.py --server.runOnSave true
```

### Configurar Tema

En `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#0066cc"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## Despliegue en Producción

### Opción 1: Streamlit Cloud (Recomendado para prototipos)

1. Sube tu código a GitHub
2. Conecta en https://share.streamlit.io
3. Selecciona el repositorio y la rama
4. La app se desplegará automáticamente

### Opción 2: Servidor Propio

```bash
# Instalar en servidor Ubuntu
sudo apt update
sudo apt install python3-pip python3-venv

# Clonar proyecto
git clone tu-repositorio.git
cd tu-proyecto

# Crear entorno virtual e instalar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Ejecutar con nohup
nohup streamlit run report_platform/ui/app.py --server.port 8501 &
```

### Opción 3: Docker (Para entornos corporativos)

Crear `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY report_platform/ ./report_platform/

EXPOSE 8501

CMD ["streamlit", "run", "report_platform/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Construir y ejecutar:

```bash
docker build -t report-platform .
docker run -p 8501:8501 report-platform
```

## Actualizar la Aplicación

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate  # Windows

# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Reiniciar aplicación
# (Ctrl+C para detener, luego volver a ejecutar)
streamlit run report_platform/ui/app.py
```

## Agregar un Nuevo Plugin

### Método Rápido:

1. **Copiar estructura de plugin existente:**

```bash
cd report_platform/reports/
cp -r informe_auditoria mi_nuevo_informe
```

2. **Editar archivos del nuevo plugin:**
   - `manifest.yaml`: Cambiar ID, nombre, versión
   - `templates/`: Reemplazar plantilla Word
   - `config/`: Actualizar YAMLs con tus campos
   - `logic.py`: Adaptar función build_context

3. **Reiniciar aplicación:**
   
```bash
# Detener app (Ctrl+C)
# Volver a ejecutar
streamlit run report_platform/ui/app.py
```

¡El nuevo plugin aparecerá automáticamente en el selector!

## Respaldo y Migración

### Hacer Respaldo:

```bash
# Crear archivo comprimido con todo el proyecto
tar -czf report-platform-backup.tar.gz report_platform/ requirements.txt README.md

# O en Windows con PowerShell
Compress-Archive -Path report_platform,requirements.txt,README.md -DestinationPath report-platform-backup.zip
```

### Restaurar desde Respaldo:

```bash
# Extraer archivos
tar -xzf report-platform-backup.tar.gz

# O en Windows
Expand-Archive -Path report-platform-backup.zip -DestinationPath .

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run report_platform/ui/app.py
```

## Logs y Debug

### Ver logs detallados:

```bash
# Ejecutar con nivel de log DEBUG
export STREAMLIT_LOG_LEVEL=debug
streamlit run report_platform/ui/app.py
```

### Logs de plugins:

Los logs de cada plugin se muestran en la consola donde ejecutas Streamlit.

### Debug de condiciones:

Puedes usar la función `debug_condition_evaluation` de `conditions_engine`:

```python
from report_platform.core.conditions_engine import debug_condition_evaluation

result = debug_condition_evaluation("tipo_opinion == 'favorable'", context)
print(result)
```

## Recursos Adicionales

- **Documentación de Streamlit:** https://docs.streamlit.io
- **Documentación de Pydantic:** https://docs.pydantic.dev
- **Documentación de Jinja2:** https://jinja.palletsprojects.com

## Contacto y Soporte

**Desarrollador:** Jimmy  
**Organización:** Forvis Mazars España  
**Versión:** 1.0.0

Para reportar problemas o solicitar funcionalidades, contactar al equipo de desarrollo.

---

¡Disfruta de la Plataforma de Generación de Informes! 🚀
