import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    filename='app.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

try:
    from PyQt6 import QtWidgets

    # Inicializar QApplication antes de otros imports de PyQt6
    app = QtWidgets.QApplication(sys.argv)

    # Imports de lógica y UI
    from logic import (
        ConfigManager,
        ScreenHandler,
        AudioHandler,
        ScreenRecorder,
    )
    from ui.main_window import MainWindow

    def main():
        """Punto de entrada principal."""
        try:
            logger.info("=== INICIANDO APLICACION ===")

            # Crear gestores
            config_manager = ConfigManager("config.json")
            screen_handler = ScreenHandler()
            audio_handler = AudioHandler()
            recorder = ScreenRecorder(screen_handler, audio_handler, config_manager)

            # Crear ventana principal
            window = MainWindow(
                config_manager,
                recorder,
                screen_handler,
                audio_handler
            )

            # Ejecutar aplicación
            sys.exit(app.exec())

        except Exception as e:
            logger.error(f"Error crítico en aplicación: {e}", exc_info=True)
            print(f"Error: {e}")
            sys.exit(1)

except ImportError as e:
    logger.error(f"Error importando módulos: {e}")
    print(f"Error de importación: {e}")
    print("Verifica que todos los módulos están instalados: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    logger.error(f"Error inesperado: {e}", exc_info=True)
    print(f"Error inesperado: {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()
