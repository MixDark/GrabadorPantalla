"""
Pestaña de registro de eventos (logs).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import qtawesome as qta
import time


class LogsTab(QWidget):
    """Pestaña de registro de eventos."""

    def __init__(self):
        """Inicializa la pestaña de logs."""
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout()

        # Área de texto de logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: "Courier New", monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.log_text)

        # Botones de control
        buttons_layout = QHBoxLayout()

        self.clear_button = QPushButton("Eliminar logs")
        self.clear_button.setIcon(QIcon(qta.icon('fa.trash')))
        self.clear_button.clicked.connect(self.clear_logs)
        buttons_layout.addWidget(self.clear_button)

        self.copy_button = QPushButton("Copiar todo")
        self.copy_button.setIcon(QIcon(qta.icon('fa.copy')))
        self.copy_button.clicked.connect(self.copy_logs)
        buttons_layout.addWidget(self.copy_button)

        self.export_button = QPushButton("Exportar")
        self.export_button.setIcon(QIcon(qta.icon('fa.download')))
        self.export_button.clicked.connect(self.export_logs)
        buttons_layout.addWidget(self.export_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def add_log(self, message: str):
        """
        Agrega un mensaje al log.
        
        Args:
            message: Mensaje a loguear
        """
        timestamp = time.strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)

    def clear_logs(self):
        """Limpia todos los logs."""
        self.log_text.clear()

    def copy_logs(self):
        """Copia todos los logs al portapapeles."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_text.toPlainText())

    def export_logs(self):
        """Exporta logs a archivo."""
        from PyQt6.QtWidgets import QFileDialog
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar logs",
            "logs.txt",
            "Archivos de texto (*.txt)"
        )
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.add_log(f"Logs exportados a: {filepath}")
            except Exception as e:
                self.add_log(f"Error exportando logs: {e}")
