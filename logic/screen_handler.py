"""
Gestor de captura de pantalla con soporte para región personalizada.
"""

import mss
import cv2
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ScreenHandler:
    """Maneja la captura de pantalla, incluyendo regiones personalizadas."""

    def __init__(self):
        """Inicializa el gestor de pantalla."""
        self.sct = mss.mss()
        self.region: Optional[dict] = None

    def capture_frame(self, bbox: dict) -> Optional[np.ndarray]:
        """
        Captura un frame de la pantalla.
        
        Args:
            bbox: Bounding box {'left', 'top', 'width', 'height'}
            
        Returns:
            Frame capturado como array numpy o None si falla
        """
        try:
            img = self.sct.grab(bbox)
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            return frame
        except Exception as e:
            logger.error(f"Error capturando pantalla: {e}")
            return None

    def get_screen_bbox(self, monitor) -> dict:
        """
        Obtiene el bounding box de una pantalla.
        
        Args:
            monitor: Objeto monitor de screeninfo
            
        Returns:
            Dict con coordenadas {'left', 'top', 'width', 'height'}
        """
        return {
            'left': monitor.x,
            'top': monitor.y,
            'width': monitor.width,
            'height': monitor.height
        }

    def set_custom_region(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Establece una región personalizada para grabación.
        
        Args:
            x1, y1: Coordenadas superior izquierda
            x2, y2: Coordenadas inferior derecha
        """
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        # Validar límites mínimos
        if width < 100 or height < 100:
            logger.warning("Región muy pequeña (mín 100x100)")
            return
        
        self.region = {
            'left': min(x1, x2),
            'top': min(y1, y2),
            'width': width,
            'height': height
        }
        logger.info(f"Región personalizada establecida: {self.region}")

    def clear_custom_region(self) -> None:
        """Limpia la región personalizada."""
        self.region = None

    def get_custom_region(self) -> Optional[dict]:
        """Retorna la región personalizada actual."""
        return self.region

    def calculate_resolution(self, bbox: dict) -> Tuple[int, int]:
        """
        Calcula la resolución basada en bbox.
        
        Args:
            bbox: Bounding box de la región
            
        Returns:
            Tupla (width, height) de la región
        """
        return (bbox['width'], bbox['height'])

    @staticmethod
    def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        Redimensiona un frame.
        
        Args:
            frame: Frame a redimensionar
            width: Ancho destino
            height: Alto destino
            
        Returns:
            Frame redimensionado
        """
        try:
            return cv2.resize(frame, (width, height))
        except Exception as e:
            logger.error(f"Error redimensionando frame: {e}")
            return frame

    @staticmethod
    def apply_quality_filter(frame: np.ndarray, quality: int = 85) -> np.ndarray:
        """
        Aplica filtro de calidad básico.
        
        Args:
            frame: Frame a procesar
            quality: Calidad (1-100)
            
        Returns:
            Frame procesado
        """
        try:
            if quality < 100:
                # Aplicar ligera compresión para calidad
                factor = quality / 100
                # Pequeño blur gaussiano para reducir ruido
                kernel_size = 3 if quality < 50 else 1
                if kernel_size > 1:
                    frame = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
            return frame
        except Exception as e:
            logger.error(f"Error aplicando filtro de calidad: {e}")
            return frame
