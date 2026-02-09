import mss
import cv2
import os
import time
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Tuple
from threading import Thread, Lock
import logging
import subprocess

logger = logging.getLogger(__name__)


class RecorderState:
    """Estados posibles de la grabación."""
    IDLE = "idle"
    RECORDING = "recording"
    PAUSED = "paused"
    PROCESSING = "processing"


class ScreenRecorder:
    """Gestor centralizado de grabación de pantalla."""

    def __init__(self, screen_handler, audio_handler, config_manager):
        """
        Inicializa el recorder.
        
        Args:
            screen_handler: Instancia de ScreenHandler
            audio_handler: Instancia de AudioHandler
            config_manager: Instancia de ConfigManager
        """
        self.screen_handler = screen_handler
        self.audio_handler = audio_handler
        self.config_manager = config_manager
        
        # Lock para sincronizar acceso al estado
        self.state_lock = Lock()
        
        self.state = RecorderState.IDLE
        self.video_writer = None
        self.audio_stream = None
        self.audio_frames = []
        self.start_time = None
        self.pause_time = None
        self.total_paused_time = 0
        self.current_fps = config_manager.get("recording.fps", 15)
        self.bbox = None
        self.quality = 85
        self.output_video_path = None
        self.output_audio_path = None
        self.webcam = None
        self.capture_camera = False

    def set_state(self, new_state: str) -> None:
        """Cambia el estado de grabación de forma thread-safe."""
        with self.state_lock:
            logger.info(f"Estado de grabación: {self.state} -> {new_state}")
            self.state = new_state

    def is_recording(self) -> bool:
        """Retorna True si está grabando (no pausado)."""
        with self.state_lock:
            return self.state == RecorderState.RECORDING

    def is_paused(self) -> bool:
        """Retorna True si está pausado."""
        with self.state_lock:
            return self.state == RecorderState.PAUSED

    def get_elapsed_time(self) -> float:
        """Retorna tiempo transcurrido en segundos (sin incluir pausa)."""
        if self.state == RecorderState.IDLE:
            return 0
        
        current_time = time.time()
        total_time = current_time - self.start_time - self.total_paused_time
        return max(0, total_time)

    def format_time(self, seconds: float) -> str:
        """Formatea tiempo en HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def start_recording(
        self,
        output_video_path: str,
        output_audio_path: str,
        bbox: Dict[str, int],
        mic_device_index: int,
        fps: Optional[int] = None,
        quality: int = 85,
        capture_camera: bool = False,
        webcam_object: Optional[cv2.VideoCapture] = None,
        webcam_callback: Optional[Callable] = None
    ) -> bool:
        """
        Inicia grabación.
        
        Args:
            output_video_path: Ruta del archivo de video temporal
            output_audio_path: Ruta del archivo de audio temporal
            bbox: Bounding box de región {'left', 'top', 'width', 'height'}
            mic_device_index: Índice del dispositivo de micrófono
            fps: FPS (usa config si None)
            quality: Calidad de video (1-100)
            capture_camera: Si True, superpone la cámara web en el video
            webcam_object: Objeto VideoCapture ya abierto para reutilizar
            webcam_callback: Función para enviar frames de cámara a la UI
            
        Returns:
            True si se inicia exitosamente
        """
        try:
            if self.state != RecorderState.IDLE:
                logger.warning(f"No se puede grabar en estado: {self.state}")
                return False

            self.current_fps = fps or self.config_manager.get("recording.fps", 15)
            self.bbox = bbox
            self.quality = quality
            self.output_video_path = output_video_path
            self.output_audio_path = output_audio_path
            self.capture_camera = capture_camera
            self.webcam_callback = webcam_callback
            
            # Preparar video con codec XVID
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.video_writer = cv2.VideoWriter(
                output_video_path,
                fourcc,
                self.current_fps,
                (bbox['width'], bbox['height'])
            )

            # Preparar captura de cámara
            if self.capture_camera:
                if webcam_object and webcam_object.isOpened():
                    self.webcam = webcam_object
                    logger.info("Reutilizando cámara web de la UI")
                else:
                    self.webcam = cv2.VideoCapture(0)
                
                if not self.webcam.isOpened():
                    logger.warning("No se pudo abrir la cámara web. Continuando sin superposición.")
                    self.capture_camera = False

            # Preparar audio
            if not self.audio_handler.start_recording(mic_device_index):
                logger.error("Falló inicio de grabación de audio")
                return False

            # Inicializar tiempos
            self.start_time = time.time()
            self.pause_time = None
            self.total_paused_time = 0
            self.audio_frames = []
            
            self.set_state(RecorderState.RECORDING)
            logger.info(f"Grabación iniciada. FPS: {self.current_fps}, Calidad: {quality}%")
            
            # Loop de captura de frames
            frame_delay = 1.0 / self.current_fps
            last_frame_time = time.time()
            
            # Mantener una instancia de mss
            with mss.mss() as sct:
                while self.state != RecorderState.IDLE:
                    # Capturar audio constantemente para evitar overflow del buffer
                    self.audio_handler.read_audio_frame()
                    
                    # Gestionar cámara web (lectura y callback para UI)
                    webcam_frame_to_overlay = None
                    if self.capture_camera and hasattr(self, 'webcam') and self.webcam:
                        try:
                            ret, w_frame = self.webcam.read()
                            if ret:
                                webcam_frame_to_overlay = w_frame
                                # Enviar a la UI para mantener el preview vivo
                                if hasattr(self, 'webcam_callback') and self.webcam_callback:
                                    self.webcam_callback(w_frame)
                        except Exception as e:
                            logger.error(f"Error leyendo webcam: {e}")
                    
                    if self.state == RecorderState.PAUSED:
                        time.sleep(0.01)
                        continue

                    current_time = time.time()
                    elapsed = current_time - last_frame_time
                    
                    # Capturar frame si ha pasado el tiempo necesario
                    if elapsed >= frame_delay:
                        try:
                            # Captura ultra-rápida con mss
                            img = sct.grab(bbox)
                            frame = np.array(img)
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                            
                            # Superponer cámara web si hay frame disponible
                            if webcam_frame_to_overlay is not None:
                                cam_w = bbox['width'] // 6
                                cam_h = bbox['height'] // 6
                                resized_cam = cv2.resize(webcam_frame_to_overlay, (cam_w, cam_h))
                                
                                x_offset = bbox['width'] - cam_w - 10
                                y_offset = 10
                                frame[y_offset:y_offset+cam_h, x_offset:x_offset+cam_w] = resized_cam
                            
                            if self.video_writer:
                                self.video_writer.write(frame)
                            last_frame_time = current_time
                        except Exception as e:
                            logger.error(f"Error capturando frame: {e}")
                    
                    time.sleep(0.001)
            
            # No liberar la cámara aquí si es propiedad de la UI
            # self.webcam.release() se manejará en stop_recording o en la UI
            return True

        except Exception as e:
            logger.error(f"Error iniciando grabación: {e}")
            return False

    def write_frame(self, frame: np.ndarray) -> bool:
        """
        Escribe un frame de video.
        
        Args:
            frame: Frame a escribir
            
        Returns:
            True si se escribió exitosamente
        """
        try:
            if self.video_writer and self.is_recording():
                self.video_writer.write(frame)
                return True
        except Exception as e:
            logger.error(f"Error escribiendo frame: {e}")
        return False

    def pause_recording(self) -> bool:
        """Pausa la grabación."""
        try:
            if self.state == RecorderState.RECORDING:
                self.pause_time = time.time()
                self.set_state(RecorderState.PAUSED)
                logger.info("Grabación pausada")
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausando grabación: {e}")
            return False

    def resume_recording(self) -> bool:
        """Reanuda la grabación pausada."""
        try:
            if self.state == RecorderState.PAUSED and self.pause_time:
                paused_duration = time.time() - self.pause_time
                self.total_paused_time += paused_duration
                self.set_state(RecorderState.RECORDING)
                logger.info(f"Grabación reanudada (pausa: {paused_duration:.1f}s)")
                return True
            return False
        except Exception as e:
            logger.error(f"Error reanudando grabación: {e}")
            return False

    def stop_recording(self) -> Tuple[str, str]:
        """
        Detiene la grabación y libera recursos.
        
        Returns:
            Tupla (video_path, audio_path)
        """
        try:
            # 1. Cambiar estado a IDLE primero para detener el bucle de captura en el otro hilo
            self.set_state(RecorderState.IDLE)
            
            # Dar un breve momento para que el bucle de captura termine su iteración actual
            time.sleep(0.1)

            # 2. Liberar video writer
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

            # 3. Guardar audio
            audio_path = self.output_audio_path or ""
            if audio_path and self.audio_handler.audio_frames:
                logger.info(f"Guardando {len(self.audio_handler.audio_frames)} frames de audio...")
                self.audio_handler.save_audio(audio_path, self.audio_handler.audio_frames)
            else:
                logger.warning("No hay frames de audio para guardar")
            
            # 4. Detener grabación de audio
            self.audio_handler.stop_recording()
            
            elapsed = self.get_elapsed_time()
            logger.info(f"Grabación detenida. Tiempo total: {self.format_time(elapsed)}")
            
            # 5. Liberar cámara si la abrimos nosotros
            if hasattr(self, 'webcam') and self.webcam is not None:
                if not getattr(self, 'webcam_callback', None):
                    self.webcam.release()
                self.webcam = None

            # 6. Retornar las rutas guardadas (usando self para evitar NameError)
            video_path = self.output_video_path or ""
            return video_path, audio_path
        except Exception as e:
            logger.error(f"Error deteniendo grabación: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return "", ""

    def combine_audio_video(
        self,
        video_file: str,
        audio_file: str,
        output_file: str,
        video_format: str = ".mp4"
    ) -> bool:
        """
        Combina video y audio usando PyAV, FFmpeg o imageio.
        
        Args:
            video_file: Ruta del archivo de video
            audio_file: Ruta del archivo de audio
            output_file: Ruta del archivo de salida
            video_format: Formato de video (.mp4, .avi, etc)
            
        Returns:
            True si se combina exitosamente
        """
        try:
            self.set_state(RecorderState.PROCESSING)
            
            # Verificar que existen los archivos
            if not os.path.exists(video_file):
                logger.error(f"Archivo de video no encontrado: {video_file}")
                return False
            
            if not os.path.exists(audio_file):
                logger.warning(f"Archivo de audio no encontrado: {audio_file}, guardando solo video")
                # Si no hay audio, simplemente copiar el video
                import shutil
                shutil.copy(video_file, output_file)
                logger.info(f"Video copiado sin audio: {output_file}")
                return True
            
            # Intento 1: Usar PyAV (Nativo, no requiere FFmpeg externo)
            if self._combine_with_pyav(video_file, audio_file, output_file):
                return True
                
            # Intento 2: Usar subprocess con FFmpeg como fallback
            try:
                if self._combine_with_ffmpeg(video_file, audio_file, output_file):
                    return True
            except (FileNotFoundError, Exception) as e:
                logger.warning(f"FFmpeg no disponible o falló: {e}")
            
            # Intento 3: Usar imageio como último recurso
            try:
                return self._combine_with_imageio(video_file, audio_file, output_file)
            except Exception as e:
                logger.warning(f"imageio no disponible: {e}, guardando solo video")
            
            # Fallback final: Solo guardar video original
            import shutil
            shutil.copy(video_file, output_file)
            logger.info(f"Video guardado sin audio (sin librerías de combinación funcionando): {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error crítico combinando audio y video: {e}")
            return False
        finally:
            self.set_state(RecorderState.IDLE)
    
    def _combine_with_pyav(self, video_file: str, audio_file: str, output_file: str) -> bool:
        """Combina video y audio usando PyAV (no requiere FFmpeg externo)."""
        try:
            import av
            logger.info(f"Combinando con PyAV: '{video_file}' + '{audio_file}'")
            
            # Abrir archivos de entrada
            input_video = av.open(video_file)
            input_audio = av.open(audio_file)
            
            # Crear archivo de salida
            output = av.open(output_file, 'w')
            
            # Configurar stream de video
            try:
                video_stream = input_video.streams.video[0]
                out_video_stream = output.add_stream('h264', rate=video_stream.base_rate or video_stream.average_rate)
                out_video_stream.width = video_stream.width
                out_video_stream.height = video_stream.height
                out_video_stream.pix_fmt = 'yuv420p'
                out_video_stream.options = {'preset': 'fast', 'crf': '23'}
                logger.info("Stream de video configurado en PyAV")
            except Exception as ev:
                logger.error(f"Error configurando video en PyAV: {ev}")
                return False
                
            # Configurar stream de audio
            try:
                audio_stream = input_audio.streams.audio[0]
                out_audio_stream = output.add_stream('aac', rate=audio_stream.rate)
                out_audio_stream.channels = audio_stream.channels
                # layout puede ser un objeto o string, nos aseguramos de que sea compatible
                out_audio_stream.layout = audio_stream.layout
                logger.info(f"Stream de audio configurado en PyAV (Rate: {audio_stream.rate}, Channels: {audio_stream.channels})")
            except Exception as ea:
                logger.error(f"Error configurando audio en PyAV: {ea}")
                return False
            
            # Procesar video
            v_frames = 0
            for packet in input_video.demux(video_stream):
                for frame in packet.decode():
                    # Es vital resetear timestamps para que empiecen desde 0
                    frame.pts = None 
                    for out_packet in out_video_stream.encode(frame):
                        output.mux(out_packet)
                        v_frames += 1
            
            # Procesar audio
            a_frames = 0
            # AAC suele requerir fltp, creamos un resampler si es necesario
            resampler = av.AudioResampler(
                format='fltp',
                layout=audio_stream.layout,
                rate=audio_stream.rate,
            )
            
            for packet in input_audio.demux(audio_stream):
                for frame in packet.decode():
                    # Resamplear frame
                    resampled_frames = resampler.resample(frame)
                    for r_frame in resampled_frames:
                        r_frame.pts = None
                        for out_packet in out_audio_stream.encode(r_frame):
                            output.mux(out_packet)
                            a_frames += 1
            
            # Flush encoders
            for out_packet in out_video_stream.encode():
                output.mux(out_packet)
            for out_packet in out_audio_stream.encode():
                output.mux(out_packet)
            
            # Cerrar archivos
            input_video.close()
            input_audio.close()
            output.close()
            
            logger.info(f"PyAV completado. Frames procesados - Video: {v_frames}, Audio: {a_frames}")
            return True
            
        except ImportError:
            logger.warning("PyAV (av) no está instalado. Ejecute 'pip install av'")
            return False
        except Exception as e:
            logger.error(f"Error crítico en PyAV: {e}", exc_info=True)
            return False
    
    def _combine_with_ffmpeg(self, video_file: str, audio_file: str, output_file: str) -> bool:
        """Combina video y audio usando FFmpeg via subprocess (usa ffmpeg.exe local si existe)."""
        logger.info(f"Combinando con FFmpeg: '{video_file}' + '{audio_file}'")
        import os
        ffmpeg_path = 'ffmpeg.exe' if os.name == 'nt' else './ffmpeg'
        if not os.path.exists(ffmpeg_path):
            ffmpeg_path = 'ffmpeg'  # fallback al sistema
        cmd = [
            ffmpeg_path,
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'libx264',      # Re-encodear con H.264 en lugar de copiar
            '-preset', 'fast',       # Preset rápido para no tardar mucho
            '-crf', '23',            # Calidad constante (18-28, menor = mejor calidad)
            '-c:a', 'aac',
            '-b:a', '192k',          # Bitrate de audio
            '-shortest',             # Terminar cuando el stream más corto termine
            '-y',                    # Sobrescribir archivo de salida
            output_file
        ]
        logger.info(f"Comando FFmpeg: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode != 0:
            logger.error(f"Error en FFmpeg (código {result.returncode})")
            logger.error(f"STDERR: {result.stderr}")
            return False
        # Mostrar salida de FFmpeg para diagnóstico
        if result.stderr:
            logger.info(f"FFmpeg output: {result.stderr[-500:]}")  # Últimos 500 caracteres
        logger.info(f"Video final guardado con FFmpeg: {output_file}")
        return True
    
    def _combine_with_imageio(self, video_file: str, audio_file: str, output_file: str) -> bool:
        """Combina video y audio usando imageio."""
        import imageio
        import soundfile as sf
        import numpy as np
        
        logger.info(f"Combinando con imageio: '{video_file}' + '{audio_file}'")
        
        # Leer video
        reader = imageio.get_reader(video_file)
        fps = reader.get_meta_data().get('fps', 30)
        
        # Leer audio
        audio_data, sr = sf.read(audio_file)
        
        # Crear writer con audio
        writer = imageio.get_writer(output_file, fps=fps, codec='libx264', pixelformat='yuv420p')
        
        try:
            # Escribir frames
            for i, frame in enumerate(reader):
                writer.append_data(frame)
        finally:
            writer.close()
        
        logger.info(f"Video final guardado con imageio: {output_file}")
        return True

    def cleanup_temp_files(self, video_file: str, audio_file: str, max_retries: int = 5) -> None:
        """
        Limpia archivos temporales.
        
        Args:
            video_file: Ruta del archivo de video temporal
            audio_file: Ruta del archivo de audio temporal
            max_retries: Número máximo de reintentos
        """
        for attempts, filepath in enumerate([(video_file, "video"), (audio_file, "audio")]):
            file_path, file_type = filepath
            
            for attempt in range(max_retries):
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logger.info(f"Archivo temporal ({file_type}) eliminado: {file_path}")
                    break
                except PermissionError:
                    if attempt < max_retries - 1:
                        time.sleep(1)
                        logger.info(f"Reintentando eliminación de {file_type}... ({attempt + 1}/{max_retries})")
                    else:
                        logger.error(f"No se pudo eliminar {file_path} después de {max_retries} intentos")
