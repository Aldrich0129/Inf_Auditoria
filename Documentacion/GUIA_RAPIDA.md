# ⚡ Guía Rápida de Uso

## 🚀 Inicio Rápido (5 minutos)

### 1️⃣ Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Ejecutar Aplicación

```bash
streamlit run report_platform/ui/app.py
```

### 3️⃣ Abrir en Navegador

```
http://localhost:8501
```

---

## 🎯 Uso Básico

### Paso 1: Seleccionar Tipo de Informe

```
Sidebar → "Seleccionar tipo de informe"
           └─ Informe de Auditoría de Cuentas Anuales
```

### Paso 2: Configurar el Informe

```
⚙️ Configuración del Informe
├─ 📋 Información general
│   ├─ Tipo de cuentas anuales [Radio]
│   ├─ Tipo de auditoría [Radio]
│   └─ Tipo de entidad [Radio]
│
├─ 📋 Características de las cuentas
│   └─ ...
│
└─ 📋 Opinión de auditoría
    ├─ Tipo de opinión [Radio]
    └─ ...
```

### Paso 3: Completar Datos

```
📝 Datos del Informe
├─ 📋 Información general
│   ├─ Tipo de administradores [Lista]
│   ├─ Tipo de órgano [Lista]
│   └─ ...
│
├─ 📋 Información de la entidad
│   ├─ Nombre de la entidad [Texto]
│   └─ ...
│
├─ 📋 Fechas del ejercicio
│   ├─ Día de cierre [Número]
│   ├─ Mes de cierre [Texto]
│   └─ Año de cierre [Número]
│
└─ 📋 Información del auditor
    ├─ Ciudad [Texto]
    ├─ Nombre del auditor [Texto]
    └─ Número ROAC [Texto]
```

### Paso 4: Generar Informe

```
[🚀 Generar Informe]
    ↓
✅ Informe generado exitosamente
    ↓
[📥 Descargar Informe]
```

---

## 🎨 Interfaz de Usuario

### Vista General

```
┌─────────────────────────────────────────────────────────────┐
│  📄 Plataforma de Generación de Informes                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ✅ Plugin cargado: Informe de Auditoría v1.0.0              │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 Estadísticas del plugin                          │   │
│  │  Campos: 70  Variables: 15  Bloques: 50             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                               │
│  ───────────────────────────────────────────────────────     │
│                                                               │
│  ⚙️ Configuración del Informe                                │
│                                                               │
│  ▼ 📋 Información general                                    │
│     ○ Tipo de cuentas: ● Normales ○ Consolidadas           │
│     ○ Tipo de auditoría: ● Obligatoria ○ Voluntaria         │
│                                                               │
│  ───────────────────────────────────────────────────────     │
│                                                               │
│  📝 Datos del Informe                                         │
│                                                               │
│  ▶ 📋 Información general                                    │
│  ▶ 📋 Información de la entidad                              │
│  ▶ 📋 Fechas del ejercicio                                   │
│  ▶ 📋 Información del auditor                                │
│                                                               │
│  ───────────────────────────────────────────────────────     │
│                                                               │
│               [🚀 Generar Informe]                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Sidebar

```
┌──────────────────────────┐
│ 📄 Plataforma de Informes│
├──────────────────────────┤
│                          │
│ Seleccionar tipo de      │
│ informe:                 │
│  [Informe de Auditoría▼] │
│                          │
├──────────────────────────┤
│ ℹ️ Información del plugin│
│                          │
│ ID: informe_auditoria    │
│ Versión: 1.0.0           │
│ Descripción: ...         │
│ Autor: Jimmy             │
└──────────────────────────┘
```

---

## 🔄 Flujo de Trabajo Típico

```
   Usuario
      ↓
   Selecciona Plugin
      ↓
   Carga Configuración
      ↓
   Completa Formulario
      ├─ Variables Condicionales
      │   ↓
      │  (Actualiza campos visibles)
      │   ↓
      └─ Campos Simples
          ↓
   Validación Automática
      ↓
   Genera Informe
      ├─ build_context()
      │   ├─ Evalúa condiciones
      │   ├─ Renderiza bloques
      │   └─ Calcula variables
      │
      └─ render_word_report()
          ├─ Aplica template
          └─ Genera archivo
      ↓
   Descarga Documento
```

---

## 📁 Estructura de Datos

### Input: Datos del Usuario

```json
{
  "tipo_opinion": "favorable",
  "tipo_cuentas": "normales",
  "nombre_entidad": "ABC S.A.",
  "dia_cierre_ejercicio": 31,
  "mes_cierre_ejercicio": "diciembre",
  "ano_cierre_ejercicio": 2024,
  ...
}
```

### Process: build_context()

```python
context = {
  # Datos originales
  **data_in,
  
  # Variables auxiliares calculadas
  "nombre_tipo_cuentas": "cuentas anuales",
  "sufijo_consolidada": "",
  
  # Bloques de texto renderizados
  "parrafo_opinion": "En nuestra opinión, las cuentas...",
  "titulo_tipo_opinion": "Opinión",
  ...
}
```

### Output: Documento Generado

```
Informe de Auditoría de Cuentas Anuales

A los Accionistas de ABC S.A., ...

Opinión

Hemos auditado las cuentas anuales de ABC S.A. ...

En nuestra opinión, las cuentas anuales adjuntas...
```

---

## 🎮 Casos de Uso

### Caso 1: Opinión Favorable Básica

```yaml
Inputs mínimos:
  - tipo_opinion: "favorable"
  - tipo_cuentas: "normales"
  - tipo_entidad: "No EIP"
  - nombre_entidad: "Mi Empresa S.L."
  - fechas de cierre
  - datos del auditor

Resultado:
  - Informe con opinión limpia
  - Sin secciones de incertidumbre
  - Sin KAM/AMRA
```

### Caso 2: Opinión con Salvedades

```yaml
Inputs adicionales:
  - tipo_opinion: "salvedades"
  - motivo_calificacion: "incorreccion"
  - descripcion_incorreccion: "La entidad no ha..."
  - numero_nota_incorreccion: 15

Resultado:
  - Sección "Opinión con salvedades"
  - Fundamento detallado
  - Referencias a notas de memoria
```

### Caso 3: EIP con KAM

```yaml
Inputs adicionales:
  - tipo_entidad: "EIP"
  - otros_kam: "si"
  - descripcion_kam_amra: "Valoración de..."
  - procedimientos_auditoria_kam: "Hemos realizado..."
  - fechas de nombramiento
  - periodo de auditoría

Resultado:
  - Sección de Cuestiones Clave
  - Informe adicional a comisión
  - Declaraciones de independencia
  - Servicios prestados
```

---

## 🛠️ Personalización Rápida

### Modificar Plantilla

```bash
# Editar plantilla
nano report_platform/reports/informe_auditoria/templates/plantilla_informe.txt

# Agregar nueva variable
{{ mi_nueva_variable }}

# Reiniciar app
streamlit run report_platform/ui/app.py
```

### Agregar Campo

```yaml
# En variables_simples.yaml
- id: mi_nuevo_campo
  nombre: "Mi Nuevo Campo"
  tipo: texto
  requerido: true
  seccion: "Mi Sección"
```

### Agregar Bloque Condicional

```yaml
# En bloques_texto.yaml
- id: mi_bloque
  descripcion: "Mi bloque personalizado"
  reglas:
    - cuando: "mi_variable == 'valor'"
      plantilla: "Texto cuando se cumple"
    - cuando: "True"
      plantilla: "Texto por defecto"
```

---

## 🔍 Debug y Troubleshooting

### Ver Logs

```bash
# En la terminal donde ejecutas Streamlit
# Los logs se muestran en tiempo real
INFO - Plugin cargado: informe_auditoria
INFO - Cargados 70 campos simples
INFO - Construyendo contexto...
```

### Verificar Contexto

```python
# En logic.py, al final de build_context()
logger.info(f"Contexto final: {len(context)} variables")
for key in sorted(context.keys()):
    logger.debug(f"  {key}: {context[key][:50]}...")
```

### Verificar Condiciones

```python
# En conditions_engine.py
from report_platform.core.conditions_engine import debug_condition_evaluation

result = debug_condition_evaluation(
    "tipo_opinion == 'favorable'", 
    context
)
print(result)
```

---

## 📊 Estadísticas de Uso

### Plugin de Auditoría

```
Campos totales:           70+
Variables condicionales:  15
Bloques de texto:         50+
Líneas de código:         ~400
Tiempo de generación:     2-5 segundos
```

### Performance

```
Carga de plugin:         < 1 segundo
Renderizado de UI:       < 2 segundos
Generación de informe:   2-5 segundos
```

---

## 💡 Tips y Trucos

### 1. Usar Atajos de Teclado

```
Ctrl+R     Recargar página (refresh)
Ctrl+Shift+R  Limpiar caché y recargar
```

### 2. Modo de Desarrollo

```bash
# Auto-reload al guardar cambios
streamlit run report_platform/ui/app.py --server.runOnSave true
```

### 3. Modo de Presentación

```bash
# Ocultar menú de Streamlit
streamlit run report_platform/ui/app.py --server.headless true
```

### 4. Compartir Temporalmente

```bash
# Hacer app accesible en red local
streamlit run report_platform/ui/app.py --server.address 0.0.0.0
```

---

## 🎓 Recursos de Aprendizaje

### Documentación Oficial
- [Streamlit Docs](https://docs.streamlit.io)
- [Pydantic Docs](https://docs.pydantic.dev)
- [Jinja2 Docs](https://jinja.palletsprojects.com)

### Tutoriales
1. **Crear un Plugin Básico** → Ver ESTRUCTURA_PROYECTO.txt
2. **Entender Bloques de Texto** → Ver bloques_texto.yaml
3. **Personalizar UI** → Ver ui_runtime.py

---

## ⚡ Comandos Esenciales

```bash
# Instalar
pip install -r requirements.txt

# Ejecutar
streamlit run report_platform/ui/app.py

# Debug
export STREAMLIT_LOG_LEVEL=debug
streamlit run report_platform/ui/app.py

# Limpiar caché
rm -rf ~/.streamlit/cache/

# Actualizar
pip install -r requirements.txt --upgrade
```

---

**¡Listo para empezar!** 🚀

Para más información, consulta:
- README.md (documentación completa)
- ESTRUCTURA_PROYECTO.txt (arquitectura)
- INSTRUCCIONES_INSTALACION.md (instalación detallada)

---

**Versión:** 1.0.0  
**Autor:** Jimmy - Forvis Mazars España  
**Fecha:** Diciembre 2024
