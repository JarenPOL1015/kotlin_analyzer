# Kotlin Analyzer 🔍

Analizador léxico, sintáctico y semántico para código Kotlin con interfaz web interactiva.

## 📋 Descripción

Este proyecto implementa un analizador completo para el lenguaje Kotlin que incluye:

- **Análisis Léxico**: Tokenización del código fuente
- **Análisis Sintáctico**: Construcción del árbol de análisis sintáctico (parse tree)
- **Análisis Semántico**: Verificación de tipos y reglas semánticas
- **Dashboard Web**: Interfaz interactiva desarrollada con Streamlit

## 🚀 Características

- ✅ Análisis de tokens en código Kotlin
- ✅ Detección de errores léxicos, sintácticos y semánticos
- ✅ Visualización del árbol sintáctico
- ✅ Editor de código integrado con resaltado de sintaxis
- ✅ Carga y descarga de archivos `.kt`
- ✅ Generación de logs detallados por fase de análisis
- ✅ Soporte para estructuras de datos (List, Set, Map)
- ✅ Soporte para tipos primitivos y operadores de Kotlin

## 📦 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/JarenPOL1015/kotlin_analyzer.git
cd kotlin_analyzer
```

### 2. Crear un entorno virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## ▶️ Ejecución

### Iniciar el Dashboard Web

```bash
streamlit run dashboard/app.py
```

El dashboard se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Uso desde línea de comandos

También puedes ejecutar los analizadores directamente:

```bash
# Análisis completo
python test.py
```

## 🎯 Uso del Dashboard

1. **Escribir código**: Usa el editor integrado para escribir código Kotlin
2. **Cargar archivo**: Haz clic en "📂 Abrir" para cargar un archivo `.kt` existente
3. **Ejecutar análisis**: Presiona "▶️ Ejecutar" para analizar el código
4. **Ver resultados**: Navega por las pestañas:
   - 🔤 **Léxico**: Tokens y errores léxicos
   - 🌲 **Sintáctico**: Árbol sintáctico y errores sintácticos
   - 🧠 **Semántico**: Errores semánticos
5. **Guardar**: Descarga tu código con el botón "💾 Guardar"
6. **Nuevo**: Limpia el editor con "🆕 Nuevo"

## 📁 Estructura del Proyecto

```
kotlin_analyzer/
├── dashboard/
│   ├── app.py              # Interfaz web Streamlit
│   └── controller.py       # Controlador del análisis
├── logs/
│   ├── lexico/            # Logs del análisis léxico
│   ├── sintactico/        # Logs del análisis sintáctico
│   └── semantico/         # Logs del análisis semántico
├── lexico.py              # Analizador léxico (PLY)
├── sintactico.py          # Analizador sintáctico (PLY)
├── semantico.py           # Analizador semántico
├── test.py                # Script de prueba
├── algoritmo1.kt          # Ejemplos de código Kotlin
├── algoritmo2.kt
├── algoritmo3.kt
└── requirements.txt       # Dependencias del proyecto
```

## 🛠️ Tecnologías Utilizadas

- **Python 3.x**: Lenguaje principal
- **PLY (Python Lex-Yacc)**: Generación de analizadores léxico y sintáctico
- **Streamlit**: Framework para la interfaz web
- **streamlit-ace**: Editor de código integrado

## 📝 Ejemplos de Código Soportado

```kotlin
// Variables
val nombre: String = "Kotlin"
var contador: Int = 0

// Funciones
fun suma(a: Int, b: Int): Int {
    return a + b
}

// Estructuras de control
if (contador > 0) {
    println("Positivo")
} else {
    println("No positivo")
}

// Bucles
for (i in 1..10) {
    println(i)
}

// Estructuras de datos
val lista: List<Int> = listOf(1, 2, 3)
val mapa: Map<String, Int> = mapOf("a" to 1)
```

## 📊 Logs

El proyecto genera logs detallados en la carpeta `logs/` organizados por:
- **Fecha y hora**: Timestamp del análisis
- **Usuario**: Nombre de usuario del sistema
- **Fase**: Léxico, sintáctico o semántico

Formato: `{fase}-{usuario}-{fecha}-{hora}.txt`

## 🤝 Contribuidores

- **Jaren Pazmiño** - Desarrollo del analizador léxico
- **David Xavier** - Desarrollo del analizador sintáctico y semántico
- **Bryan Ortiz** - Testing y validación

## 📄 Licencia

Este proyecto fue desarrollado como parte de un proyecto académico.

## 🐛 Solución de Problemas

### Error al activar el entorno virtual en Windows

Si encuentras errores de permisos al ejecutar scripts en PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error con PLY

Si experimentas problemas con el parser, elimina los archivos de caché:

```bash
# Windows
del parsetab.py
del parser.out

# Linux/macOS
rm parsetab.py parser.out
```

Luego vuelve a ejecutar el análisis.

### Streamlit no se abre automáticamente

Abre manualmente tu navegador y visita: `http://localhost:8501`

## 📞 Contacto

Para preguntas o sugerencias, contacta al equipo de desarrollo a través del repositorio de GitHub.

---

**Nota**: Este analizador está en desarrollo y puede no soportar todas las características del lenguaje Kotlin.
