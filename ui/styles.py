"""
Constantes de estilos y colores para la aplicación.
"""

# ==================== COLORES ====================

# Colores principales
PRIMARY_COLOR = "#3498db"           # Azul
PRIMARY_DARK = "#2980b9"            # Azul oscuro
HOVERLIGHT_COLOR = "#5dade2"        # Azul claro
SECONDARY_COLOR = "#ecf0f1"         # Blanco/Gris claro
TEXT_COLOR = "#ecf0f1"              # Texto principal
BG_DARK = "rgba(20, 30, 40, 0.7)"   # Fondo oscuro

# Colores de estado
SUCCESS_COLOR = "#27ae60"            # Verde
ERROR_COLOR = "#e74c3c"              # Rojo
WARNING_COLOR = "#f39c12"            # Amarillo/Naranja
INFO_COLOR = "#3498db"               # Azul

# Colores de fondo
BG_PRIMARY = "rgba(30, 45, 60, 0.8)"
BG_SECONDARY = "rgba(40, 55, 70, 0.8)"
BG_TERTIARY = "rgba(20, 30, 40, 0.9)"

# ==================== TAMAÑOS ====================

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700

# Tamaños de fuente
FONT_SIZE_SMALL = 11
FONT_SIZE_NORMAL = 12
FONT_SIZE_LARGE = 14
FONT_SIZE_TITLE = 16
FONT_SIZE_HEADER = 18

# Tamaños de iconos
ICON_SIZE_SMALL = 16
ICON_SIZE_NORMAL = 24
ICON_SIZE_LARGE = 32

# Padding y márgenes
PADDING_SMALL = 5
PADDING_NORMAL = 8
PADDING_LARGE = 15

MARGIN_SMALL = 2
MARGIN_NORMAL = 5
MARGIN_LARGE = 10

# Radio de bordes
BORDER_RADIUS_SMALL = 3
BORDER_RADIUS_NORMAL = 5
BORDER_RADIUS_LARGE = 8

# ==================== CONFIGURACIÓN DE GRABACIÓN ====================

# FPS predeterminados
DEFAULT_FPS = 15
MIN_FPS = 10
MAX_FPS = 60

# Resoluciones predefinidas
RESOLUTIONS = {
    "Full": (1920, 1080),
    "1280x720": (1280, 720),
    "1024x768": (1024, 768),
    "800x600": (800, 600),
}

# Formatos de video soportados
VIDEO_FORMATS = [".mp4", ".avi", ".mov"]

# Codecs de video
VIDEO_CODEC = {
    ".mp4": "libx264",
    ".avi": "mpeg4",
    ".mov": "libx264",
}

# Codecs de audio
AUDIO_CODEC = {
    ".mp4": "aac",
    ".avi": "pcm_s16le",
    ".mov": "aac",
}

# ==================== AUDIO ====================

# Frecuencia de muestreo
SAMPLE_RATE = 44100

# Canales de audio
AUDIO_CHANNELS = 2

# Frames por buffer
FRAMES_PER_BUFFER = 2048

# ==================== RUTAS ====================

DEFAULT_RECORDINGS_PATH = "grabaciones"
TEMP_FOLDER = "tmp"
LOG_FILE = "app.log"
CONFIG_FILE = "config.json"

# ==================== CURSOR ====================

CURSOR_STYLES = [
    "Predeterminado",
    "Círculo blanco",
    "Círculo rojo",
    "Círculo verde",
    "Círculo azul",
    "Cruz"
]

CURSOR_COLORS = {
    "Círculo blanco": (255, 255, 255),
    "Círculo rojo": (0, 0, 255),
    "Círculo verde": (0, 255, 0),
    "Círculo azul": (255, 0, 0),
}

CURSOR_RADIUS = 10

# ==================== TIEMPOS ====================

# Timeout para intentos de eliminación de archivos
FILE_DELETE_TIMEOUT = 5
FILE_DELETE_RETRY_DELAY = 1

# ==================== VALORES POR DEFECTO ====================

DEFAULT_FILENAME = "grabacion"
DEFAULT_MINIMIZE_ON_START = True
DEFAULT_SHOW_CURSOR = True
DEFAULT_RECORD_MIC = True
DEFAULT_MIC_VOLUME = 1000
DEFAULT_SYSTEM_AUDIO_VOLUME = 700

# ==================== MENSAJES ====================

# Mensajes de error
ERROR_NO_SCREEN_SELECTED = "Error: No hay una pantalla seleccionada."
ERROR_FILE_EXISTS = f"El archivo ya existe. ¿Desea reemplazarlo?"
ERROR_RECORDING_FAILED = "Error durante la grabación"
ERROR_PROCESSING_VIDEO = "Error al procesar el video"

# Mensajes de info
INFO_RECORDING_STARTED = "Grabación iniciada."
INFO_RECORDING_STOPPED = "Grabación detenida."
INFO_PROCESSING = "Procesando grabación..."
INFO_SAVED = "Grabación guardada en:"
