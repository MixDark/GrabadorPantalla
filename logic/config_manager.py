"""
Gestor de configuración persistente.
Guarda y carga configuraciones de la aplicación en JSON.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Gestor centralizado de configuración."""

    def __init__(self, config_file: str = "config.json"):
        """
        Inicializa el gestor de configuración.
        
        Args:
            config_file: Ruta del archivo de configuración
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Carga la configuración del archivo JSON."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Configuración cargada desde: {self.config_file}")
            else:
                logger.info("Archivo de configuración no encontrado. Usando defaults.")
                self.config = self._get_default_config()
        except Exception as e:
            logger.error(f"Error al cargar configuración: {e}")
            self.config = self._get_default_config()

    def save(self) -> None:
        """Guarda la configuración en archivo JSON."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuración guardada en: {self.config_file}")
        except Exception as e:
            logger.error(f"Error al guardar configuración: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.
        
        Args:
            key: Clave de configuración (soporta notación de punto para anidados)
            default: Valor por defecto si no existe
            
        Returns:
            El valor de configuración o el default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """
        Establece un valor de configuración.
        
        Args:
            key: Clave de configuración (soporta notación de punto)
            value: Valor a guardar
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuración por defecto."""
        return {
            "recording": {
                "fps": 15,
                "resolution": "Full",
                "format": ".mp4",
                "show_cursor": True,
                "cursor_style": "Predeterminado",
                "minimize_on_start": True,
            },
            "audio": {
                "record_microphone": True,
                "microphone_volume": 1000,
                "record_system_audio": False,
                "system_audio_volume": 700,
            },
            "files": {
                "default_filename": "grabacion",
                "storage_location": "grabaciones",
            },
            "keyboard": {
                "hotkey": "Ctrl+Alt+R",
                "enabled": True,
            },
            "ui": {
                "theme": "dark",
                "window_width": 900,
                "window_height": 700,
            },
        }

    def reset_to_defaults(self) -> None:
        """Reinicia la configuración a los valores por defecto."""
        self.config = self._get_default_config()
        self.save()
        logger.info("Configuración reiniciada a valores por defecto.")

    def get_all(self) -> Dict[str, Any]:
        """Retorna toda la configuración."""
        return self.config.copy()

    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Actualiza la configuración con un diccionario.
        
        Args:
            config_dict: Diccionario con configuraciones a actualizar
        """
        self._deep_update(self.config, config_dict)
        self.save()

    @staticmethod
    def _deep_update(d: Dict, u: Dict) -> Dict:
        """Actualiza recursivamente un diccionario anidado."""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = ConfigManager._deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
