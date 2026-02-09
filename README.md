# 🎬 Grabador de pantalla

Una aplicación profesional de grabación de pantalla desarrollada en Python con interfaz gráfica PyQt6, diseñada para capturar, procesar y guardar videos de alta calidad.

## 📋 Características

### 🎥 Grabación de video
- ✅ Soporte para múltiples pantallas/monitores
- ✅ Grabación en tiempo real con FPS ajustable (hasta 60 FPS)
- ✅ Múltiples formatos de salida: MP4, AVI, MOV
- ✅ Captura de región completa de la pantalla
- ✅ **Novedad**: Superposición de cámara web integrada durante la grabación

### 🎙️ Audio
- ✅ Grabación de audio del micrófono
- ✅ Soporte para micrófono de múltiples canales
- ✅ Control de volumen del micrófono
- ✅ Prueba de micrófono integrada
- ✅ Grabación de audio del sistema (cuando está disponible)
- ✅ Normalización y compresión de audio

### 🖱️ Personalización del cursor
- ✅ Mostrar/ocultar cursor durante grabación
- ✅ Múltiples estilos: Predeterminado, círculos (blanco, rojo, verde, azul), cruz

### ⌨️ Atajos de teclado
- ✅ Atajos de teclado personalizables para iniciar/detener grabación
- ✅ Configuración global del atajo
- ✅ Minimizar ventana automáticamente al iniciar

### 📊 Interfaz de usuario
- ✅ Interfaz moderna con 3 pestañas (Grabación, Configuración, Registro)
- ✅ Previsualizaciones de pantallas disponibles
- ✅ Contador de tiempo en vivo
- ✅ Barra de progreso de audio
- ✅ Registro de eventos detallado con soporte UTF-8

## 🚀 Requisitos previos

### Sistema operativo
- Windows 10/11 (Optimizado para Windows)

### Python
- Python 3.10 o superior

### Dependencias del sistema
- **FFmpeg (Obligatorio)**: Debe estar en la carpeta raíz del proyecto.
  - 📥 **Descargar desde aquí**: [Enlace a Google Drive](https://drive.google.com/drive/folders/1LldbJ0mdY4YXQpSTvOXh2dFk8FeLKUj-?usp=drive_link)
  - Descomprima los archivos `ffmpeg.exe`, `ffplay.exe` y `ffprobe.exe` directamente en la carpeta principal del grabador.

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/MixDark/GrabadorPantalla.git
cd GrabadorPantalla
```

### 2. Crear entorno virtual (Recomendado)
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

## 🎯 Uso

### Ejecutar la aplicación
```bash
python main.py
```

### Flujo básico:
1. **Seleccionar pantalla**: Elige la pantalla/monitor a grabar.
2. **Configurar opciones**: Ajusta nombre, formato, audio y cámara web.
3. **Iniciar grabación**: Presiona "Iniciar" o usa el atajo de teclado (`Ctrl+Alt+R` por defecto).
4. **Detener grabación**: Presiona "Detener" o usa el atajo.
5. **Esperar procesamiento**: El video se combina con el audio automáticamente.

---

**Última actualización**: 9 febrero 2026  
**Versión**: 1.2.0
