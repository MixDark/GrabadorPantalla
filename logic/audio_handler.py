"""
Gestor de audio para grabación de micrófono y audio del sistema.
"""

import sounddevice as sd
import pyaudio
import numpy as np
import wave
from typing import List, Optional, Tuple, Callable
import logging

logger = logging.getLogger(__name__)


class AudioHandler:
    """Maneja la grabación y procesamiento de audio."""

    def __init__(self, sample_rate: int = 44100, channels: int = 2):
        """
        Inicializa el gestor de audio.
        
        Args:
            sample_rate: Frecuencia de muestreo
            channels: Número de canales
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_frames: List[bytes] = []
        self.stream = None
        self.recording = False

    def get_microphone_devices(self) -> List[dict]:
        """
        Obtiene lista de dispositivos de micrófono disponibles.
        
        Returns:
            Lista de dispositivos de audio de entrada (diccionarios con 'name' e 'index')
        """
        try:
            devices = sd.query_devices()
            microphones = []
            
            for i, d in enumerate(devices):
                # Verificar si tiene canales de entrada
                try:
                    max_input = d.get('max_input_channels', 0) if isinstance(d, dict) else getattr(d, 'max_input_channels', 0)
                    if max_input > 0:
                        device_name = d.get('name', f'Dispositivo {i}') if isinstance(d, dict) else getattr(d, 'name', f'Dispositivo {i}')
                        microphones.append({
                            'name': device_name,
                            'index': i,
                            'channels': max_input
                        })
                except:
                    continue
            
            logger.info(f"Se encontraron {len(microphones)} micrófonos")
            return microphones
        except Exception as e:
            logger.error(f"Error obteniendo dispositivos de audio: {e}")
            return []

    def start_recording(self, device_index: int, callback: Optional[Callable] = None) -> bool:
        """
        Inicia grabación de audio del micrófono.
        
        Args:
            device_index: Índice del dispositivo
            callback: Función callback para nivel de volumen
            
        Returns:
            True si se inicia exitosamente
        """
        try:
            if self.recording:
                logger.warning("Ya hay una grabación en progreso")
                return False

            # Inicializar PyAudio
            p = pyaudio.PyAudio()
            
            # Obtener información del dispositivo
            device_info = p.get_device_info_by_index(device_index)
            channels = int(device_info['maxInputChannels'])
            
            # Actualizar canales para que save_audio use el valor correcto
            self.channels = channels
            
            # Crear stream
            self.stream = p.open(
                format=pyaudio.paInt16,
                channels=channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=2048
            )
            
            self.recording = True
            self.audio_frames = []
            logger.info(f"Grabación de audio iniciada. Dispositivo: {device_info['name']}, Canales: {channels}")
            return True
            
        except Exception as e:
            logger.error(f"Error al iniciar grabación de audio: {e}")
            return False

    def stop_recording(self) -> None:
        """Detiene la grabación de audio."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            self.recording = False
            logger.info("Grabación de audio detenida")
        except Exception as e:
            logger.error(f"Error al detener grabación: {e}")

    def read_audio_frame(self, frames_per_buffer: int = 2048) -> Optional[bytes]:
        """
        Lee un frame de audio.
        
        Args:
            frames_per_buffer: Número de frames a leer
            
        Returns:
            Datos de audio o None
        """
        try:
            if self.stream and self.recording:
                # Leer con exception_on_overflow=False para evitar errores de buffer
                data = self.stream.read(frames_per_buffer, exception_on_overflow=False)
                if data:
                    self.audio_frames.append(data)
                    return data
        except IOError as e:
            # Ignorar errores de overflow del buffer
            if e.errno != pyaudio.paInputOverflowed:
                logger.error(f"Error de IO leyendo audio: {e}")
        except Exception as e:
            logger.error(f"Error leyendo audio: {e}")
        return None

    def save_audio(self, filepath: str, audio_data: List[bytes]) -> bool:
        """
        Guarda audio a archivo WAV.
        
        Args:
            filepath: Ruta del archivo
            audio_data: Datos de audio
            
        Returns:
            True si se guarda exitosamente
        """
        try:
            if not audio_data:
                logger.warning(f"No hay datos de audio para guardar en {filepath}")
                return False
            
            # Calcular tamaño total
            total_bytes = sum(len(frame) for frame in audio_data)
            logger.info(f"Guardando audio: {len(audio_data)} frames, {total_bytes} bytes totales")
            
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(audio_data))
            
            # Verificar que el archivo se creó correctamente
            import os
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                logger.info(f"Audio guardado exitosamente: {filepath} ({file_size} bytes)")
                return True
            else:
                logger.error(f"El archivo de audio no se creó: {filepath}")
                return False
                
        except Exception as e:
            logger.error(f"Error guardando audio: {e}")
            return False

    def normalize_audio(self, audio_data: np.ndarray, threshold: float = 0.8) -> np.ndarray:
        """
        Normaliza audio para evitar distorsión.
        
        Args:
            audio_data: Datos de audio como array numpy
            threshold: Umbral de normalización (0-1)
            
        Returns:
            Audio normalizado
        """
        try:
            max_value = 32767  # Máximo para int16
            max_amplitude = np.max(np.abs(audio_data))
            
            if max_amplitude > threshold * max_value:
                normalization_factor = (threshold * max_value) / max_amplitude
                audio_data = audio_data * normalization_factor
                
            return np.clip(audio_data, -max_value, max_value).astype(np.int16)
        except Exception as e:
            logger.error(f"Error normalizando audio: {e}")
            return audio_data

    def apply_volume(self, audio_data: np.ndarray, volume: float) -> np.ndarray:
        """
        Aplica ganancia de volumen al audio.
        
        Args:
            audio_data: Datos de audio
            volume: Factor de volumen (0-3000 escalado a 0-1)
            
        Returns:
            Audio con volumen aplicado
        """
        try:
            max_value = 32767
            volume_factor = volume / 1000.0
            audio_data = np.clip(audio_data * volume_factor, -max_value, max_value)
            return audio_data.astype(np.int16)
        except Exception as e:
            logger.error(f"Error aplicando volumen: {e}")
            return audio_data

    def test_microphone(self, device_index: int, duration: float = 2.0) -> Optional[float]:
        """
        Prueba micrófono y retorna nivel promedio de volumen.
        
        Args:
            device_index: Índice del dispositivo
            duration: Duración de la prueba en segundos
            
        Returns:
            Nivel de volumen promedio (0-100)
        """
        try:
            logger.info(f"Iniciando prueba de micrófono en dispositivo {device_index} por {duration}s")
            
            recording = sd.rec(
                int(self.sample_rate * duration),
                samplerate=self.sample_rate,
                channels=1,
                device=device_index
            )
            sd.wait()
            
            # Calcular nivel RMS
            rms = np.sqrt(np.mean(recording**2))
            logger.info(f"RMS crudo: {rms}")
            
            # Escalar el nivel RMS a un rango de 0-100
            # Los valores típicos de RMS están entre 0.0 y 0.1 para audio normal
            # Multiplicamos por 1000 para obtener valores significativos
            level = min(100, float(rms * 1000))
            
            logger.info(f"Nivel de micrófono calculado: {level:.1f}")
            return level
        except Exception as e:
            logger.error(f"Error probando micrófono: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def get_audio_level(self, audio_data: np.ndarray) -> float:
        """
        Calcula el nivel de volumen de datos de audio.
        
        Args:
            audio_data: Datos de audio como array numpy
            
        Returns:
            Nivel (0-100)
        """
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            volume_norm = np.linalg.norm(audio_array) * 10
            return min(100, int(volume_norm))
        except Exception as e:
            logger.error(f"Error calculando nivel: {e}")
            return 0
