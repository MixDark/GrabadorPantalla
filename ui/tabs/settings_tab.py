"""
Pestaña de configuración.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox,
    QSlider, QSpinBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QIcon
import qtawesome as qta
import os
from pathlib import Path

from ui.styles import (
    ICON_SIZE_NORMAL, VIDEO_FORMATS, DEFAULT_FPS, MIN_FPS, MAX_FPS,
    CURSOR_STYLES, DEFAULT_FILENAME
)



class SettingsTab(QWidget):
    fps_changed = pyqtSignal(int)
    quality_changed = pyqtSignal(int)
    location_selected = pyqtSignal(str)
    mic_test_completed = pyqtSignal(object)  # Señal para resultado del test de micrófono

    def open_folder(self):
        """Abre la carpeta de grabaciones en el explorador de archivos."""
        from PyQt6.QtWidgets import QMessageBox
        import os
        folder = os.path.abspath('grabaciones')
        if os.path.exists(folder):
            if os.name == 'nt':
                os.startfile(folder)
            elif os.name == 'posix':
                import subprocess
                subprocess.Popen(['xdg-open', folder])
        else:
            QMessageBox.warning(self, "Carpeta no encontrada", f"La carpeta {folder} no existe.")

    def __init__(self, config_manager, audio_handler=None):
        super().__init__()
        self.config_manager = config_manager
        self.audio_handler = audio_handler
        self.init_ui()
        # Conectar señal para actualización de UI desde thread
        self.mic_test_completed.connect(self.update_mic_ui_callback)
        # Configurar iconos de checkbox después de crear los widgets
        self.setup_checkbox_icons()
    
    def setup_checkbox_icons(self):
        """Configura iconos personalizados para los checkboxes con checkmark visible."""
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen
        from PyQt6.QtCore import QRect, QStandardPaths
        import tempfile
        
        # Crear directorio temporal para los iconos
        temp_dir = tempfile.gettempdir()
        
        # Color azul del botón "Probar micrófono"
        checkbox_color = QColor(41, 128, 185)  # #2980b9
        
        # Crear icono para checkbox sin marcar
        unchecked_pixmap = QPixmap(22, 22)
        unchecked_pixmap.fill(QColor(0, 0, 0, 0))  # Transparente
        painter = QPainter(unchecked_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor(102, 102, 102), 2))
        painter.setBrush(QColor(30, 30, 30))
        painter.drawRoundedRect(1, 1, 20, 20, 4, 4)
        painter.end()
        
        # Crear icono para checkbox marcado con checkmark
        checked_pixmap = QPixmap(22, 22)
        checked_pixmap.fill(QColor(0, 0, 0, 0))  # Transparente
        painter = QPainter(checked_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(checkbox_color, 2))
        painter.setBrush(checkbox_color)
        painter.drawRoundedRect(1, 1, 20, 20, 4, 4)
        # Dibujar checkmark (✓)
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.drawLine(6, 11, 9, 15)  # Parte corta del check
        painter.drawLine(9, 15, 16, 6)  # Parte larga del check
        painter.end()
        
        # Guardar imágenes temporalmente
        unchecked_path = os.path.join(temp_dir, 'checkbox_unchecked.png')
        checked_path = os.path.join(temp_dir, 'checkbox_checked.png')
        unchecked_pixmap.save(unchecked_path)
        checked_pixmap.save(checked_path)
        
        # Actualizar estilos de los checkboxes con las rutas de las imágenes
        checkbox_style = f"""
            QCheckBox {{
                font-weight: normal;
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
            }}
            QCheckBox::indicator:unchecked {{
                image: url({unchecked_path.replace(os.sep, '/')});
            }}
            QCheckBox::indicator:checked {{
                image: url({checked_path.replace(os.sep, '/')});
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid #2980b9;
            }}
        """
        
        self.show_cursor_checkbox.setStyleSheet(checkbox_style)
        self.minimize_checkbox.setStyleSheet(checkbox_style)
        self.capture_camera_checkbox.setStyleSheet(checkbox_style)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # ========== Ubicación de grabaciones ==========
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Ubicación de grabaciones:"))

        self.location_button = QPushButton("Seleccionar carpeta")
        self.location_button.setIcon(QIcon(qta.icon('fa.folder-open')))
        self.location_button.setIconSize(QSize(ICON_SIZE_NORMAL, ICON_SIZE_NORMAL))
        self.location_button.setFixedSize(160, 40)
        self.location_button.clicked.connect(self.select_location)
        location_layout.addWidget(self.location_button)

        self.open_folder_button = QPushButton("Abrir carpeta")
        self.open_folder_button.setIcon(QIcon(qta.icon('fa.folder')))
        self.open_folder_button.setIconSize(QSize(ICON_SIZE_NORMAL, ICON_SIZE_NORMAL))
        self.open_folder_button.setFixedSize(160, 40)
        self.open_folder_button.clicked.connect(self.open_folder)
        location_layout.addWidget(self.open_folder_button)

        location_layout.addStretch()
        layout.addLayout(location_layout)

        # ========== Configuración básica ==========
        # Nombre de archivo
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("Nombre de archivo:"))
        
        self.filename_input = QLineEdit(DEFAULT_FILENAME)
        self.filename_input.setFixedWidth(300)
        self.filename_input.setFixedHeight(35)
        filename_layout.addWidget(self.filename_input)
        filename_layout.addStretch()
        layout.addLayout(filename_layout)

        layout.addSpacing(20)

        # ========== FPS, Formato y Calidad en una fila ==========
        video_settings_layout = QHBoxLayout()
        
        # FPS
        video_settings_layout.addWidget(QLabel("FPS:"))
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(MIN_FPS, MAX_FPS)
        self.fps_spinbox.setValue(DEFAULT_FPS)
        self.fps_spinbox.setFixedWidth(80)
        self.fps_spinbox.setFixedHeight(35)
        self.fps_spinbox.valueChanged.connect(self.fps_changed.emit)
        video_settings_layout.addWidget(self.fps_spinbox)
        
        video_settings_layout.addSpacing(20)
        
        # Formato
        video_settings_layout.addWidget(QLabel("Formato:"))
        self.format_combo = QComboBox()
        for fmt in VIDEO_FORMATS:
            self.format_combo.addItem(fmt)
        self.format_combo.setFixedWidth(120)
        self.format_combo.setFixedHeight(35)
        video_settings_layout.addWidget(self.format_combo)
        video_settings_layout.addWidget(QLabel("Calidad de video:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(85)
        self.quality_slider.setFixedWidth(200)
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        video_settings_layout.addWidget(self.quality_slider)
        
        self.quality_label = QLabel("85%")
        self.quality_label.setFixedWidth(35)
        video_settings_layout.addWidget(self.quality_label)
        
        video_settings_layout.addStretch()
        layout.addLayout(video_settings_layout)

        layout.addSpacing(20)

        mic_device_layout = QHBoxLayout()
        mic_device_layout.addSpacing(10)
        mic_device_layout.addWidget(QLabel("Dispositivo:"))
        self.mic_combo = QComboBox()
        self.mic_combo.setFixedWidth(450)
        self.mic_combo.setFixedHeight(35)
        self.load_microphone_devices()
        mic_device_layout.addWidget(self.mic_combo)
        mic_device_layout.addStretch()
        layout.addLayout(mic_device_layout)

        layout.addSpacing(20)

        # ========== Volumen, Probar micrófono y Barra en una fila ==========
        from PyQt6.QtWidgets import QProgressBar
        mic_controls_layout = QHBoxLayout()
        
        # Volumen micrófono
        mic_controls_layout.addWidget(QLabel("Volumen micrófono:"))
        self.mic_volume_slider = QSlider(Qt.Horizontal)
        self.mic_volume_slider.setRange(0, 200)
        self.mic_volume_slider.setValue(100)
        self.mic_volume_slider.setFixedWidth(150)
        self.mic_volume_slider.valueChanged.connect(self.on_mic_volume_changed)
        mic_controls_layout.addWidget(self.mic_volume_slider)
        
        self.mic_volume_label = QLabel("50%")
        self.mic_volume_label.setFixedWidth(35)
        mic_controls_layout.addWidget(self.mic_volume_label)
        # No establecer ancho aquí, se hará al final
        
        # Botón Probar micrófono
        self.test_mic_button = QPushButton("Probar micrófono")
        self.test_mic_button.setIcon(QIcon(qta.icon('fa.microphone')))
        self.test_mic_button.setIconSize(QSize(ICON_SIZE_NORMAL, ICON_SIZE_NORMAL))
        self.test_mic_button.clicked.connect(self.on_test_mic)
        mic_controls_layout.addWidget(self.test_mic_button)
        
        # Barra de nivel de micrófono
        self.mic_level_bar = QProgressBar()
        self.mic_level_bar.setRange(0, 100)
        self.mic_level_bar.setValue(0)
        self.mic_level_bar.setTextVisible(True)
        self.mic_level_bar.setFixedWidth(150)
        mic_controls_layout.addWidget(self.mic_level_bar)
        
        mic_controls_layout.addStretch()
        layout.addLayout(mic_controls_layout)

        layout.addSpacing(20)

        # ========== Mostrar cursor ========== 
        # Checkbox mostrar cursor
        self.show_cursor_checkbox = QCheckBox("Mostrar cursor")
        self.show_cursor_checkbox.setChecked(True)
        layout.addWidget(self.show_cursor_checkbox)

        # ========== Capturar cámara ========== 
        self.capture_camera_checkbox = QCheckBox("Capturar cámara")
        self.capture_camera_checkbox.setChecked(True)
        # Quitar negrilla del texto
        self.capture_camera_checkbox.setStyleSheet("font-weight: normal;")
        layout.addWidget(self.capture_camera_checkbox)

        # Estilo del cursor
        cursor_style_layout = QHBoxLayout()
        cursor_style_layout.addWidget(QLabel("Estilo del cursor:"))
        
        self.cursor_style_combo = QComboBox()
        self.cursor_style_combo.setFixedWidth(250)
        self.cursor_style_combo.setFixedHeight(35)
        self.cursor_style_combo.addItems(CURSOR_STYLES)
        cursor_style_layout.addWidget(self.cursor_style_combo)
        cursor_style_layout.addStretch()
        layout.addLayout(cursor_style_layout)

        layout.addSpacing(20)

        # ========== Opciones ==========
        self.minimize_checkbox = QCheckBox("Minimizar al iniciar grabación")
        self.minimize_checkbox.setChecked(True)
        layout.addWidget(self.minimize_checkbox)

        layout.addStretch()

        self.setLayout(layout)
        # Eliminar llamada a set_uniform_combobox_size, ya no es necesaria


    def on_quality_changed(self, value: int):
        self.quality_label.setText(f"{value}%")
        self.quality_changed.emit(value)

    def on_mic_volume_changed(self, value: int):
        percentage = int((value / 200) * 100)
        self.mic_volume_label.setText(f"{percentage}%")

    def load_microphone_devices(self):
        self.mic_combo.clear()
        if self.audio_handler:
            devices = self.audio_handler.get_microphone_devices()
            # Filtrar solo dispositivos realmente activos (con canales de entrada > 0)
            active_devices = [d for d in devices if d.get('channels', 0) > 0]
            if active_devices:
                for device in active_devices:
                    # Guardar el nombre como texto y el índice como userData
                    self.mic_combo.addItem(device.get('name', 'Desconocido'), device.get('index', 0))
            else:
                self.mic_combo.addItem("Sin dispositivos activos", 0)
        else:
            self.mic_combo.addItem("Sin dispositivos", 0)

    def on_test_mic(self):
        from PyQt6.QtCore import QTimer
        from PyQt6.QtWidgets import QMessageBox
        import threading
        import traceback
        
        # Resetear barra y mostrar que está probando
        self.mic_level_bar.setValue(0)
        self.mic_level_bar.setFormat("Probando...")
        
        if not self.audio_handler:
            self.mic_level_bar.setFormat(None)
            self.mic_level_bar.setValue(0)
            QMessageBox.warning(self, "Error", "No hay gestor de audio disponible.")
            return
        idx = self.mic_combo.currentIndex()
        if idx < 0:
            self.mic_level_bar.setFormat(None)
            self.mic_level_bar.setValue(0)
            QMessageBox.warning(self, "Error", "Selecciona un dispositivo de micrófono.")
            return
        devices = self.audio_handler.get_microphone_devices()
        active_devices = [d for d in devices if d.get('channels', 0) > 0]
        if not active_devices or idx >= len(active_devices):
            self.mic_level_bar.setFormat(None)
            self.mic_level_bar.setValue(0)
            QMessageBox.warning(self, "Error", "No hay dispositivo activo seleccionado.")
            return
        device = active_devices[idx]
        
        # Deshabilitar botón y cambiar texto
        self.test_mic_button.setEnabled(False)
        original_text = self.test_mic_button.text()
        self.test_mic_button.setText("Probando...")
        
        # Seguridad: reactivar el botón después de 3 segundos pase lo que pase
        def restore_button():
            self.test_mic_button.setEnabled(True)
            self.test_mic_button.setText(original_text)
        
        QTimer.singleShot(3000, restore_button)
        
        def run_test():
            level = None
            try:
                print(f"Probando micrófono idx={device['index']}")
                level = self.audio_handler.test_microphone(device['index'])
                print(f"Nivel recibido: {level}")
            except Exception as e:
                print("Error en test_microphone:", e)
                print(traceback.format_exc())
            
            # Emitir señal con el resultado
            self.mic_test_completed.emit(level)
        
        threading.Thread(target=run_test, daemon=True).start()
    
    @pyqtSlot(object)
    def update_mic_ui_callback(self, level):
        """Callback para actualizar la UI desde el hilo principal."""
        from PyQt6.QtWidgets import QMessageBox
        print(f"[UI Thread] Actualizando UI con nivel: {level}")
        
        if level is None:
            QMessageBox.warning(self, "Error", "No se pudo probar el micrófono. Revisa permisos o drivers.")
            self.mic_level_bar.setFormat(None)
            self.mic_level_bar.setValue(0)
        else:
            val = float(level)
            print(f"[UI Thread] Valor crudo para barra: {val}")
            bar_value = int(round(val))
            if bar_value < 0:
                bar_value = 0
            if bar_value > 100:
                bar_value = 100
            print(f"[UI Thread] Valor final barra: {bar_value}")
            
            # Resetear formato y actualizar valor
            self.mic_level_bar.setFormat(None)
            self.mic_level_bar.setValue(bar_value)
            self.mic_level_bar.update()
            print(f"[UI Thread] Barra actualizada a {bar_value}%")
            
            if bar_value == 0:
                QMessageBox.warning(self, "Micrófono sin señal", "No se detectó señal de audio. Prueba hablar o revisa el dispositivo.")
            elif bar_value < 15:
                QMessageBox.information(self, "Señal baja", f"Se detectó una señal muy baja ({bar_value}%). Intenta hablar más fuerte o acerca el micrófono.")

    def select_location(self):
        location = QFileDialog.getExistingDirectory(self, "Seleccionar ubicación")
        if location:
            self.location_selected.emit(location)

    def get_settings(self) -> dict:
        # Obtener el índice del dispositivo de micrófono seleccionado
        mic_device_index = self.mic_combo.currentData() if self.mic_combo.currentData() is not None else 0
        return {
            "filename": self.filename_input.text(),
            "format": self.format_combo.currentText(),
            "fps": self.fps_spinbox.value(),
            "quality": self.quality_slider.value(),
            "record_mic": True,
            "mic_device_index": mic_device_index,
            "mic_volume": self.mic_volume_slider.value(),
            "show_cursor": self.show_cursor_checkbox.isChecked(),
            "cursor_style": self.cursor_style_combo.currentText(),
            "minimize": self.minimize_checkbox.isChecked(),
            "capture_camera": self.capture_camera_checkbox.isChecked(),
        }