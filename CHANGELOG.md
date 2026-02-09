# Historial de cambios (CHANGELOG)

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [1.2.0] - 2026-02-09

### 🎉 Agregado
- 📸 **Soporte para cámara web (webcam overlap)**
  - Previsualización en tiempo real integrada en la interfaz
  - Superposición automática en la esquina superior derecha del video grabado
  - Reutilización inteligente del dispositivo para evitar retrasos
- 🌐 **Soporte UTF-8 completo**
  - Los logs ahora guardan correctamente tildes y caracteres especiales
  - Interfaz de registro actualizada con codificación universal

### 🔧 Mejoras técnicas
- ⚡ **Optimización del inicio de grabación**
  - Reducción drástica del retraso al iniciar (traspaso instantáneo de cámara)
  - Mejora en la sincronización de hilos para mayor estabilidad
- 🛡️ **Robustez en el cierre de archivos**
  - Corrección de errores críticos que causaban el cierre inesperado al detener
  - Nuevo flujo secuencial de guardado (video -> audio -> combinación)
- 🎨 **Pulido de interfaz**
  - Textos de la interfaz normalizados con inicial mayúscula
  - Iconos de estado actualizados para mejor visibilidad

## [1.1.0] - 2026-02-07

### 🎉 Agregado
- ✨ **Refactorización completa a arquitectura modular**
  - `logic/`: Módulo de lógica de negocio desacoplado de UI
  - `ui/`: Módulo de interfaz completamente separado
  - `ui/tabs/`: Módulos para cada pestaña de la interfaz
  - `resources/`: Archivos de recursos (CSS, imágenes)

- 🎨 **Gestión centralizada de estilos CSS**
  - CSS externo en `resources/styles.css`
  - Constantes de colores, tamaños y configuración en `ui/styles.py`
  - Estilos consistentes en toda la aplicación
  - Facilita cambio de temas

- ⚙️ **Gestor de configuración persistente** (`logic/config_manager.py`)
  - Guardar/cargar configuración en JSON
  - Soporta notación de punto para valores anidados
  - Configuración por defecto integrada
  - Reinicio a defaults simplificado

- 📸 **Gestor de captura de pantalla** (`logic/screen_handler.py`)
  - Soporte para región personalizada (captura de área)
  - Redimensionado flexible de frames
  - Filtros de calidad básicos
  - Mejor manejo de múltiples monitores

- 🔊 **Gestor de audio mejorado** (`logic/audio_handler.py`)
  - Detección automática de dispositivos de audio
  - Normalización y compresión de audio
  - Control de volumen granular
  - Prueba de micrófono integrada
  - Cálculo de niveles RMS

- ⏸️ **Pausa y reanudación de grabación** (`logic/recorder.py`)
  - Estados claros: IDLE, RECORDING, PAUSED, PROCESSING
  - Sistema de tiempo que excluye duración de pausa
  - Mejor control de flujo

- 🎯 **interfaz de usuario mejorada** (`ui/main_window.py`)
  - Mejor separación de responsabilidades
  - Sistema de señales para comunicación entre componentes
  - Atajos de teclado configurables
  - Mejora de experiencia de usuario

- 📋 **Pestañas de UI modularizadas**
  - `ui/tabs/recording_tab.py`: Grabación y selección de pantalla
  - `ui/tabs/settings_tab.py`: Configuración de opciones
  - `ui/tabs/logs_tab.py`: Visualización y exportación de logs
  - Cada pestaña es independiente y reutilizable

### 🔧 Mejoras técnicas
- Código más limpio y mantenible
- Mejor separación de concerns (MVC-like)
- Más fácil de testear
- Menos acoplamiento entre componentes
- Mejor documentación del código

### 📦 Nuevas dependencias
- `imageio-ffmpeg`: Mejor soporte de codificación

## [1.0.0] - 2026-02-07

### 🎉 Agregado
- ✨ **Interfaz gráfica completa con PyQt6**
  - Tres pestañas: Grabación, Configuraciones, Registro de eventos
  - Diseño moderno con tema oscuro personalizado
  
- 🎥 **Grabación de pantalla múltiple**
  - Soporte para múltiples monitores/pantallas
  - Previsualizaciones miniatura de pantallas disponibles
  - Selección visual de pantalla
  
- 🎙️ **Captura de audio dual**
  - Grabación de micrófono con múltiples canales
  - Grabación de audio del sistema
  - Control independiente de volumen
  - Normalización y compresión de audio
  - Prueba de micrófono integrada con visualización de nivel
  
- 🖱️ **Personalización del cursor**
  - 5 estilos diferentes (Predeterminado, círculos de colores, cruz)
  - Opción de mostrar/ocultar cursor
  
- ⌨️ **Atajos de teclado**
  - Atajos personalizables para iniciar/detener grabación
  - Configuración global del atajo en la interfaz
  - Minimizar ventana automática al iniciar grabación
  
- 📁 **Gestión de archivos**
  - Seleccionar ubicación personalizada para grabaciones
  - Acceso rápido a carpeta de grabaciones
  - Validación de archivos existentes con confirmación de sobrescritura
  - Nombres de archivo personalizables
  
- 📊 **Formatos de salida múltiples**
  - Soporte para MP4, AVI y MOV
  - Codificación con libx264 (MP4)
  
- ⏱️ **Monitoreo en vivo**
  - Contador de tiempo formateado (HH:MM:SS)
  - Barra de progreso de micrófono
  - Indicador de grabación activa
  
- 📝 **Sistema de registro**
  - Registro en tiempo real en la interfaz
  - Log persistente en archivo `app.log`
  - Timestamps en cada evento
  
- 🛡️ **Manejo de errores**
  - Captura y reporte de errores
  - Reintentos automáticos para procesos fallidos
  - Mensajes informativos al usuario

### 🔧 Técnico
- Arquitectura multihilo para grabación sin bloqueos
- Procesamiento de video con OpenCV
- Integración de MoviePy para composición audio-video
- Uso de mss para captura de pantalla eficiente
- APIs de Windows para captura de cursor (win32)
- Gestión de recursos y limpieza de archivos temporales

### 📦 Dependencias iniciales
- PyQt6 (UI)
- OpenCV (procesamiento de video)
- MoviePy (composición de audio/video)
- NumPy (operaciones numéricas)
- SoundDevice (captura de audio)
- PyAudio (gestión de dispositivos de audio)
- MSS (captura de pantalla)
- Pywin32 (APIs de Windows)
- Screeninfo (información de monitores)
- Qtawesome (iconos)

---

## [2.0.0] - En desarrollo (Futuro)

### 🎉 Planeado - Mejoras Mayores

#### 🎬 Grabación avanzada
- [ ] Grabación de región personalizada (captura de área/ventana)
- [ ] Pausa/Reanuda sin detener la grabación
- [ ] Grabación con múltiples pantallas simultáneamente
- [ ] Opciones de calidad: resolución, FPS, bitrate personalizables

#### 🎨 Edición de video
- [ ] Editor integrado: corte, recorte, ajustes básicos
- [ ] Agregar watermark/marca de agua
- [ ] Efectos: zoom, transiciones
- [ ] Filtros básicos

#### 📊 Historial y estadísticas
- [ ] Historial de grabaciones con thumbnails
- [ ] Estadísticas: duración, tamaño, calidad
- [ ] Acceso directo a archivos recientes
- [ ] Base de datos de grabaciones

#### 🌍 Compatibilidad
- [ ] Soporte completo para Linux (GTK/X11)
- [ ] Soporte completo para macOS (Cocoa)
- [ ] Codificadores de hardware: NVIDIA NVENC, Intel Quick Sync, AMD VCE
- [ ] Soporte para más formatos: WebM, Matroska (MKV)

#### 🎛️ Configuración y temas
- [ ] Configuración persistente (guardar/cargar entre sesiones)
- [ ] Tema claro/oscuro intercambiable
- [ ] Perfiles de configuración predefinidos
- [ ] Validación automática de dependencias

#### 🔌 Integración y API
- [ ] API REST para grabación remota
- [ ] Webhooks para notificaciones
- [ ] Exportación a plataformas (YouTube, Twitch)
- [ ] Integración con OneDrive/Google Drive

#### 🎯 Mejoras UX
- [ ] Notificaciones del sistema
- [ ] Indicador de estado en bandeja del sistema
- [ ] Gestos personalizados del ratón
- [ ] Atajos de teclado adicionales

#### 🔒 Características avanzadas
- [ ] Grabación con encriptación
- [ ] Autenticación para acceso remoto
- [ ] Control de acceso por usuario
- [ ] Auditoría de grabaciones

### 🐛 Correcciones futuras
- Mejora de rendimiento con buffer de video
- Optimización de memoria para grabaciones largas
- Mejor manejo de desconexiones de dispositivos
- Soporte para resoluciones ultra-altas (4K, 8K)

---

## Notas sobre versionado

- **MAYOR**: Cambios incompatibles con versiones anteriores
- **MENOR**: Nuevas características compatibles hacia atrás
- **PARCHE**: Correcciones de errores compatibles hacia atrás

## Cómo reportar cambios

Para sugerir cambios o nuevas características:
1. Abre un issue en el repositorio
2. Describe el cambio propuesto
3. Proporciona ejemplos de uso si es aplicable
4. Participa en la discusión comunitaria

---

**Última actualización**: 7 febrero 2026
**Mantenedor principal**: [Tu Nombre]
