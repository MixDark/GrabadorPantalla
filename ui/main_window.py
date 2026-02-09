"""
Ventana principal de la aplicación.
"""

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget, QMessageBox
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from screeninfo import get_monitors
import os
import logging
from threading import Thread
from datetime import datetime
from pathlib import Path

from ui.tabs import RecordingTab, SettingsTab, LogsTab
from ui.styles import WINDOW_WIDTH, WINDOW_HEIGHT

logger = logging.getLogger(__name__)


class Communicate(QObject):
    """Objeto para comunicación de señales entre hilos."""
    log_signal = pyqtSignal(str)
    timer_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    recording_state_signal = pyqtSignal(bool)
    paused_state_signal = pyqtSignal(bool)
    webcam_frame_signal = pyqtSignal(object)  # Nueva señal para frames de cámara


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""

    def __init__(self, config_manager, recorder, screen_handler, audio_handler):
        """
        Inicializa la ventana principal.
        
        Args:
            config_manager: Gestor de configuración
            recorder: Grabador de pantalla
            screen_handler: Gestor de pantalla
            audio_handler: Gestor de audio
        """
        super().__init__()

        self.config_manager = config_manager
        self.recorder = recorder
        self.screen_handler = screen_handler
        self.audio_handler = audio_handler
        self.comm = Communicate()
        
        # Variables para control de grabación
        self.recording_thread = None
        self.recording_active = False
        self.current_video_path = None
        self.current_audio_path = None

        # Conectar señales
        self.comm.log_signal.connect(self.log)
        self.comm.timer_signal.connect(self.update_timer)
        self.comm.status_signal.connect(self.update_status)
        self.comm.recording_state_signal.connect(self.on_recording_state_changed)
        self.comm.paused_state_signal.connect(self.on_paused_state_changed)

        # Timer para actualizar contador
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)

        # Obtener monitores
        self.monitors = get_monitors()

        # Crear interfaz
        self.init_ui()

        logger.info("Aplicación iniciada")

    def init_ui(self):
        """Inicializa la interfaz."""
        self.setWindowTitle("Grabador de pantalla")
        self.setWindowIcon(QIcon("favicon.ico") if os.path.exists("favicon.ico") else QIcon())
        self.resize(700, 650)
        
        # Desactivar redimensión y botón de maximizar
        self.setFixedSize(700, 650)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        # Cargar estilos CSS
        self.load_styles()

        # Crear widget central
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Crear pestañas
        self.tabs = QTabWidget()

        self.recording_tab = RecordingTab(self.monitors)
        self.recording_tab.screen_selected.connect(self.on_screen_selected)
        self.recording_tab.recording_toggled.connect(self.on_recording_toggled)
        self.recording_tab.paused_toggled.connect(self.on_paused_toggled)

        self.settings_tab = SettingsTab(self.config_manager, self.audio_handler)
        self.settings_tab.fps_changed.connect(self.on_fps_changed)
        self.settings_tab.location_selected.connect(self.on_location_selected)

        self.logs_tab = LogsTab()

        self.tabs.addTab(self.recording_tab, "🎥 Grabación")
        self.tabs.addTab(self.settings_tab, "⚙️ Configuración")
        self.tabs.addTab(self.logs_tab, "📝 Registro")

        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Configurar atajos de teclado
        self.setup_shortcuts()

        self.show()
        self.comm.log_signal.emit("Interfaz cargada")

    def load_styles(self):
        """Carga los estilos CSS."""
        try:
            css_path = "resources/styles.css"
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                logger.warning(f"Archivo de estilos no encontrado: {css_path}")
        except Exception as e:
            logger.error(f"Error cargando estilos: {e}")

    def setup_shortcuts(self):
        """Configura atajos de teclado."""
        # Atajo por defecto: Ctrl+Alt+R para iniciar/detener
        hotkey = self.config_manager.get("keyboard.hotkey", "Ctrl+Alt+R")
        try:
            shortcut = QShortcut(QKeySequence(hotkey), self)
            shortcut.activated.connect(self.toggle_recording)
            logger.info(f"Atajo configurado: {hotkey}")
        except Exception as e:
            logger.error(f"Error configurando atajo: {e}")

    def log(self, message: str):
        """Agrega mensaje al log."""
        self.logs_tab.add_log(message)
        logger.info(message)

    def update_timer(self, time_str: str):
        """Actualiza el contador de tiempo."""
        self.recording_tab.update_timer(time_str)

    def update_status(self, status: str):
        """Actualiza el status."""
        self.recording_tab.update_status(status)

    def update_elapsed_time(self):
        """Actualiza el tiempo transcurrido."""
        elapsed = self.recorder.get_elapsed_time()
        time_str = self.recorder.format_time(elapsed)
        self.comm.timer_signal.emit(time_str)

    def on_screen_selected(self, monitor, button):
        """Se ejecuta cuando se selecciona una pantalla."""
        logger.info(f"Pantalla seleccionada: {monitor.name}")

    def on_recording_toggled(self, start: bool):
        """Se ejecuta cuando se inicia/detiene grabación."""
        if start:
            self.start_recording()
        else:
            self.stop_recording()

    def on_paused_toggled(self, pause: bool):
        """Se ejecuta cuando se pausa/reanuda."""
        logger.info(f"on_paused_toggled llamado con pause={pause}")
        if pause:
            self.pause_recording()
        else:
            self.resume_recording()

    def on_fps_changed(self, fps: int):
        """Se ejecuta cuando cambia FPS."""
        self.config_manager.set("recording.fps", fps)
        self.comm.log_signal.emit(f"FPS establecidos a: {fps}")

    def on_location_selected(self, location: str):
        """Se ejecuta cuando se selecciona ubicación."""
        self.config_manager.set("files.storage_location", location)
        self.comm.log_signal.emit(f"Ubicación establecida: {location}")

    def on_recording_state_changed(self, recording: bool):
        """Se ejecuta cuando cambia el estado de grabación."""
        state = "grabando" if recording else "detenido"
        logger.info(f"Estado de grabación: {state}")

    def on_paused_state_changed(self, paused: bool):
        """Se ejecuta cuando cambia el estado de pausa."""
        state = "pausado" if paused else "reanudado"
        logger.info(f"Estado de pausa: {state}")

    def start_recording(self):
        """Inicia la grabación."""
        try:
            # Seleccionar pantalla
            monitor = self.recording_tab.get_selected_monitor()
            if not monitor:
                QMessageBox.warning(self, "Error", "Selecciona una pantalla")
                return

            settings = self.settings_tab.get_settings()

            # Crear directorios si no existen
            recordings_dir = Path("grabaciones")
            recordings_dir.mkdir(exist_ok=True)

            tmp_dir = Path("grabaciones/tmp")
            tmp_dir.mkdir(parents=True, exist_ok=True)

            # Crear timestamp para nombres de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = settings.get("filename", "grabacion") or "grabacion"

            # Rutas temporales en carpeta grabaciones/tmp
            video_path = str(tmp_dir / f"tmp_{timestamp}_video.mp4")
            audio_path = str(tmp_dir / f"tmp_{timestamp}_audio.wav")

            # Guardar rutas actuales
            self.current_video_path = video_path
            self.current_audio_path = audio_path

            # Crear bbox del monitor
            bbox = {
                'left': monitor.x,
                'top': monitor.y,
                'width': monitor.width,
                'height': monitor.height
            }

            # Obtener dispositivo de micrófono seleccionado
            mic_device = settings.get("mic_device_index", 0)
            logger.info(f"Usando dispositivo de micrófono: {mic_device}")

            # Obtener si se debe capturar cámara y gestionar el traspaso desde la UI
            capture_camera = settings.get("capture_camera", False)
            webcam_obj = None
            if capture_camera:
                webcam_obj = self.recording_tab.get_camera_object()
                self.recording_tab.camera_in_use = True
                self.recording_tab.stop_camera_preview()
                
                # Conectar señal para actualizar el preview desde el hilo de grabación
                try:
                    self.comm.webcam_frame_signal.disconnect()
                except:
                    pass
                self.comm.webcam_frame_signal.connect(self.recording_tab.update_camera_preview_from_frame)

            # Iniciar grabación en thread
            self.recording_active = True
            self.recording_tab.set_recording_state(True)
            self.comm.log_signal.emit(f"Iniciando grabación de {monitor.name}...")

            self.recording_thread = Thread(
                target=self.recorder.start_recording,
                args=(video_path, audio_path, bbox, mic_device),
                kwargs={
                    "fps": settings.get("fps", 15),
                    "quality": settings.get("quality", 85),
                    "capture_camera": capture_camera,
                    "webcam_object": webcam_obj,
                    "webcam_callback": lambda frame: self.comm.webcam_frame_signal.emit(frame)
                },
                daemon=True
            )
            self.recording_thread.start()
            
            # Iniciar timer para actualizar contador
            self.timer.start(100)
            self.comm.recording_state_signal.emit(True)
            self.comm.log_signal.emit("Grabación iniciada")

        except Exception as e:
            self.comm.log_signal.emit(f"Error iniciando grabación: {e}")
            logger.error(f"Error: {e}", exc_info=True)
            self.recording_active = False
            self.recording_tab.set_recording_state(False)

    def stop_recording(self):
        """Detiene la grabación."""
        try:
            if not self.recording_active:
                return
            
            self.timer.stop()
            self.recording_active = False
            self.comm.log_signal.emit("⏹ Deteniendo grabación...")
            
            # Detener la grabación en el recorder
            video_path, audio_path = self.recorder.stop_recording()
            logger.info(f"Paths from recorder: video={video_path}, audio={audio_path}")
            
            # Ya no esperamos a que termine el thread de grabación aquí para evitar deadlock/cierre inesperado
            # El thread de grabación terminará solo cuando vea el estado IDLE
            
            self.recording_tab.set_recording_state(False)
            self.comm.recording_state_signal.emit(False)
            
            # Liberar cámara para la UI
            if hasattr(self, 'recording_tab'):
                self.recording_tab.camera_in_use = False
                try:
                    self.comm.webcam_frame_signal.disconnect()
                except:
                    pass
                # Pequeño delay para dejar que el hilo de grabación libere el control
                QTimer.singleShot(100, self.recording_tab.start_camera_preview)
            
            # Procesar y combinar video con audio en un thread
            if video_path and os.path.exists(video_path):
                self.comm.log_signal.emit("Procesando video y audio...")
                settings = self.settings_tab.get_settings()
                process_thread = Thread(
                    target=self.process_recording,
                    args=(video_path, audio_path, settings),
                    daemon=True
                )
                process_thread.start()
            else:
                self.comm.log_signal.emit("Error: No se generó archivo de video")

        except Exception as e:
            self.comm.log_signal.emit(f"Error deteniendo grabación: {e}")
            logger.error(f"Error: {e}", exc_info=True)
            self.recording_active = False
            self.recording_tab.set_recording_state(False)
    
    def process_recording(self, video_path: str, audio_path: str, settings: dict):
        """Procesa y finaliza la grabación (corre en thread)."""
        try:
            recordings_dir = Path("grabaciones")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = settings.get("filename", "grabacion") or "grabacion"
            video_format = settings.get("format", ".mp4")

            # Crear nombre del archivo final
            output_path = str(recordings_dir / f"{filename}_{timestamp}{video_format}")
            self.comm.log_signal.emit(f"Combinando audio y video...")
            
            if self.recorder.combine_audio_video(video_path, audio_path, output_path, video_format):
                self.comm.log_signal.emit(f"✓ Grabación completada: {output_path}")
                logger.info(f"Grabación completada en: {output_path}")
                
                # Limpiar archivos temporales
                self.comm.log_signal.emit("Limpiando archivos temporales...")
                self.recorder.cleanup_temp_files(video_path, audio_path)
            else:
                # Si la combinación falla, copiar al menos el video
                import shutil
                try:
                    final_video = str(recordings_dir / f"{filename}_{timestamp}_video{video_format}")
                    shutil.copy(video_path, final_video)
                    self.comm.log_signal.emit(f"⚠ Video guardado sin audio: {final_video}")
                    
                    # Limpiar archivos temporales
                    self.recorder.cleanup_temp_files(video_path, audio_path)
                except Exception as copy_e:
                    self.comm.log_signal.emit(f"Error: {copy_e}")
                    logger.error(f"Error copiando video: {copy_e}")
        except Exception as e:
            self.comm.log_signal.emit(f"Error procesando grabación: {e}")
            logger.error(f"Error procesando: {e}", exc_info=True)

    def pause_recording(self):
        """Pausa la grabación."""
        try:
            logger.info("pause_recording() llamado")
            logger.info(f"recording_active={self.recording_active}, state={self.recorder.state}")
            if self.recorder.pause_recording():
                logger.info("Pausa exitosa en recorder")
                self.timer.stop()  # Detener el timer de contador
                self.recording_tab.set_paused_state(True)
                self.comm.log_signal.emit("⏸ Grabación pausada")
                self.comm.paused_state_signal.emit(True)
            else:
                logger.warning("recorder.pause_recording() retornó False")
                self.comm.log_signal.emit("Error: No se pudo pausar la grabación")
        except Exception as e:
            logger.error(f"Error pausando: {e}", exc_info=True)
            self.comm.log_signal.emit(f"Error pausando: {e}")

    def resume_recording(self):
        """Reanuda la grabación."""
        try:
            if self.recorder.resume_recording():
                self.timer.start(100)  # Reanudar el timer
                self.recording_tab.set_paused_state(False)
                self.comm.log_signal.emit("▶️ Grabación reanudada")
                self.comm.paused_state_signal.emit(False)
            else:
                self.comm.log_signal.emit("Error: No se pudo reanudar la grabación")
        except Exception as e:
            self.comm.log_signal.emit(f"Error reanudando: {e}")
            logger.error(f"Error: {e}", exc_info=True)

    def toggle_recording(self):
        """Alterna entre iniciar/detener grabación."""
        if self.recorder.is_recording() or self.recorder.is_paused():
            self.stop_recording()
        else:
            self.start_recording()

    def closeEvent(self, event):
        """Maneja cierre de ventana."""
        if self.recorder.is_recording():
            reply = QMessageBox.question(
                self,
                "Confirmación",
                "¿Hay una grabación en progreso. ¿Está seguro de salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        self.config_manager.save()
        logger.info("Aplicación cerrada")
        event.accept()
