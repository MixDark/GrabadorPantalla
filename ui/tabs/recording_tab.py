"""
Pestaña de grabación de pantalla.
"""

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QImage
import qtawesome as qta
import mss
import numpy as np
from threading import Thread

from ui.styles import (
    ICON_SIZE_NORMAL, FONT_SIZE_LARGE, PADDING_NORMAL,
    MARGIN_NORMAL
)


class RecordingTab(QWidget):
    def start_camera_preview(self):
        import cv2
        # Inicializar cámara solo una vez
        if not hasattr(self, 'camera') or self.camera is None:
            self.camera = cv2.VideoCapture(0)
        self.camera_timer = QtCore.QTimer()
        self.camera_timer.timeout.connect(self.update_camera_preview)
        self.camera_timer.start(100)
    def get_camera_object(self):
        # Permite reutilizar el objeto cámara para grabación
        if hasattr(self, 'camera'):
            return self.camera
        return None

    def update_camera_preview(self):
        import cv2
        if hasattr(self, 'camera') and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                frame = cv2.resize(frame, (200, 150))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                self.camera_preview_label.setPixmap(pixmap)
            else:
                self.camera_preview_label.setText("Sin señal de cámara")
        else:
            self.camera_preview_label.setText("Sin cámara")

    def update_camera_preview_from_frame(self, frame):
        """Actualiza el label de preview con un frame capturado externamente (por el recorder)."""
        if frame is not None:
            try:
                import cv2
                # El frame viene en BGR de OpenCV
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img).scaled(self.camera_preview_label.width(), 
                                                     self.camera_preview_label.height(), 
                                                     Qt.AspectRatioMode.KeepAspectRatio)
                self.camera_preview_label.setPixmap(pixmap)
            except Exception as e:
                print(f"Error actualizando preview externo: {e}")

    def stop_camera_preview(self):
        """Detiene el timer de preview y opcionalmente libera la cámara."""
        if hasattr(self, 'camera_timer'):
            self.camera_timer.stop()
        
        # Solo liberar si no está marcada como en uso por la grabación
        if hasattr(self, 'camera') and self.camera is not None:
            if not getattr(self, 'camera_in_use', False):
                self.camera.release()
                self.camera = None
                self.camera_preview_label.setText("Cámara liberada")
    """Pestaña principal de grabación."""

    # Señales
    screen_selected = pyqtSignal(object, object)  # monitor, button
    recording_toggled = pyqtSignal(bool)  # True = iniciar, False = detener
    paused_toggled = pyqtSignal(bool)  # True = pausar, False = reanudar
    stop_recording = pyqtSignal()  # Nueva señal para detener

    def __init__(self, monitors):
        """
        Inicializa la pestaña de grabación.
        
        Args:
            monitors: Lista de monitores disponibles
        """
        super().__init__()
        self.monitors = monitors
        self.screen_buttons = []
        self.selected_button = None
        self.camera = None
        self.camera_in_use = False
        self.init_ui()
        self.start_camera_preview()

    def init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout()

        # Sección de selección de pantalla y preview de cámara
        preview_layout = QHBoxLayout()
        preview_layout.setSpacing(40)
        preview_layout.setAlignment(Qt.AlignCenter)

        # Pantalla (label encima del preview)
        screen_preview_layout = QVBoxLayout()
        screen_label = QLabel("Selecciona una pantalla:")
        screen_label.setFont(QFont("Arial", FONT_SIZE_LARGE))
        screen_label.setAlignment(Qt.AlignCenter)
        screen_preview_layout.addWidget(screen_label)
        screen_preview_layout.setSpacing(8)

        self.screen_grid = QGridLayout()
        def make_select_callback(monitor, btn):
            return lambda _: self.select_screen(monitor, btn)
        for i, monitor in enumerate(self.monitors):
            btn = QPushButton()
            btn.setMaximumSize(220, 150)
            btn.setMinimumSize(220, 150)
            btn.setToolTip(f"Seleccionar {monitor.name}")
            btn.clicked.connect(make_select_callback(monitor, btn))
            self.screen_buttons.append(btn)
            self.screen_grid.addWidget(btn, i // 2, i % 2)
            thread = Thread(target=self.load_monitor_thumbnail, args=(btn, monitor), daemon=True)
            thread.start()
        if len(self.screen_buttons) == 1:
            btn = self.screen_buttons[0]
            btn.setStyleSheet("border: 3px solid #3498db; border-radius: 5px;")
            self.selected_button = btn
        screen_preview_layout.addLayout(self.screen_grid)
        screen_preview_layout.setAlignment(Qt.AlignCenter)
        preview_layout.addLayout(screen_preview_layout)

        # Preview de cámara (label encima del preview)
        camera_preview_layout = QVBoxLayout()
        camera_label = QLabel("Cámara:")
        camera_label.setFont(QFont("Arial", FONT_SIZE_LARGE))
        camera_label.setAlignment(Qt.AlignCenter)
        camera_preview_layout.addWidget(camera_label)
        camera_preview_layout.setSpacing(8)
        self.camera_preview_label = QLabel("Preview cámara")
        self.camera_preview_label.setAlignment(Qt.AlignCenter)
        self.camera_preview_label.setFixedSize(220, 150)
        self.camera_preview_label.setStyleSheet("border: 2px solid #aaa; border-radius: 5px; background: #222; color: #fff;")
        camera_preview_layout.addWidget(self.camera_preview_label)
        camera_preview_layout.setAlignment(Qt.AlignCenter)

        preview_layout.addLayout(camera_preview_layout)
        layout.addLayout(preview_layout)

        # Sección de controles de grabación
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(MARGIN_NORMAL)

        self.record_button = QPushButton("Iniciar")
        self.record_button.setIcon(QIcon(qta.icon('fa.play-circle')))
        self.record_button.setIconSize(QSize(ICON_SIZE_NORMAL, ICON_SIZE_NORMAL))
        self.record_button.setFixedSize(120, 50)
        self.record_button.clicked.connect(lambda: self.recording_toggled.emit(True))
        controls_layout.addWidget(self.record_button, alignment=Qt.AlignCenter)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.setIcon(QIcon(qta.icon('fa.pause-circle')))
        self.pause_button.setIconSize(QSize(ICON_SIZE_NORMAL, ICON_SIZE_NORMAL))
        self.pause_button.setFixedSize(120, 50)
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(lambda: self.paused_toggled.emit(True))
        controls_layout.addWidget(self.pause_button, alignment=Qt.AlignCenter)

        self.resume_button = QPushButton("Reanudar")
        self.resume_button.setIcon(QIcon(qta.icon('fa.play')))
        self.resume_button.setIconSize(QSize(ICON_SIZE_NORMAL, ICON_SIZE_NORMAL))
        self.resume_button.setFixedSize(120, 50)
        self.resume_button.setEnabled(False)
        self.resume_button.clicked.connect(lambda: self.paused_toggled.emit(False))
        controls_layout.addWidget(self.resume_button, alignment=Qt.AlignCenter)

        self.stop_button = QPushButton("Detener")
        self.stop_button.setIcon(QIcon(qta.icon('fa.stop-circle')))
        self.stop_button.setIconSize(QSize(ICON_SIZE_NORMAL, ICON_SIZE_NORMAL))
        self.stop_button.setFixedSize(120, 50)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(lambda: self.recording_toggled.emit(False))
        controls_layout.addWidget(self.stop_button, alignment=Qt.AlignCenter)

        layout.addLayout(controls_layout)

        # Contador de tiempo
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.timer_label.setVisible(False)
        layout.addWidget(self.timer_label, alignment=Qt.AlignCenter)

        # Indicador de estado
        self.status_label = QLabel("Listo para grabar")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_screen(self, monitor, button):
        """Selecciona una pantalla."""
        if self.selected_button:
            self.selected_button.setStyleSheet("")
        
        self.selected_button = button
        button.setStyleSheet("border: 3px solid #3498db; border-radius: 5px;")
        
        self.screen_selected.emit(monitor, button)

    def update_timer(self, time_str: str):
        """Actualiza el contador de tiempo."""
        self.timer_label.setText(time_str)
        self.timer_label.setVisible(True)

    def update_status(self, status: str):
        """Actualiza el label de estado."""
        self.status_label.setText(status)

    def set_recording_state(self, recording: bool):
        """Cambia el estado de los botones según grabación."""
        self.record_button.setEnabled(not recording)
        self.pause_button.setEnabled(recording)
        self.resume_button.setEnabled(False)
        self.stop_button.setEnabled(recording)

    def set_paused_state(self, paused: bool):
        """Cambia el estado de los botones según pausa."""
        self.pause_button.setEnabled(not paused)
        self.resume_button.setEnabled(paused)
        self.stop_button.setEnabled(True)  # Siempre habilitado durante grabación

    def get_selected_monitor(self):
        """Retorna el monitor seleccionado."""
        # Implementar lógica para obtener monitor seleccionado
        return self.monitors[0] if self.monitors else None
    def load_monitor_thumbnail(self, button: QPushButton, monitor):
        """
        Carga una miniatura del monitor y la muestra en el botón, cubriendo todo el tamaño (sin franjas).
        """
        try:
            with mss.mss() as sct:
                bbox = {
                    'left': monitor.x,
                    'top': monitor.y,
                    'width': monitor.width,
                    'height': monitor.height
                }
                screenshot = sct.grab(bbox)
                screenshot_array = np.array(screenshot)
                # Redimensionar exactamente a 300x200 (sin mantener aspecto)
                from cv2 import resize, INTER_LINEAR
                screenshot_resized = resize(screenshot_array, (300, 200), interpolation=INTER_LINEAR)
                # Convertir a formato RGB
                if screenshot_resized.shape[2] == 4:
                    screenshot_resized = screenshot_resized[:, :, :3]
                h_small, w_small = screenshot_resized.shape[:2]
                bytes_per_line = 3 * w_small
                q_img = QImage(
                    screenshot_resized.tobytes(),
                    w_small,
                    h_small,
                    bytes_per_line,
                    QImage.Format.Format_RGB888
                )
                pixmap = QPixmap.fromImage(q_img)
                icon = QIcon(pixmap)
                button.setIcon(icon)
                button.setIconSize(QSize(300, 200))
        except Exception as e:
            print(f"Error capturando miniatura de {monitor.name}: {e}")