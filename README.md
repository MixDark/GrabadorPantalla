# Grabador de pantalla

## Descripción
Una aplicación creada con PyQt6 para grabar la pantalla del computador, tambien captura audio del sistema y del microfono.

## Capturas de pantalla
![1](https://github.com/user-attachments/assets/986ff664-156c-4af8-a8f2-26b2af397db6)

![2](https://github.com/user-attachments/assets/ed3f34d1-a42e-427d-bcbd-dd5e1076bdc2)

![3](https://github.com/user-attachments/assets/4ed1d90f-312f-4b76-a086-1d706fa0bc76)


## Características
- Es compatible con Windows
- Reconoce varias pantallas y permite elegir la que se quiera grabar
- Soporte para formatos de video como mp4, avi, mov
- Cursor en cruz, preterminado o en circulo de diferentes colores
- Opciones para grabar audio del sistema y el microfono
- Opción para probar el microfono
- Opción para establecer un atajo de teclado
- Opción para minimizar la aplicación mientas se esta grabando
- Opciones para cambiar el nombre del archivo, elegir la ubicación de almacenamiento y abrir la carpeta 
- Interfaz simple e intuitiva
- Pestaña donde se muestra el registro de eventos

## Tecnologías utilizadas
- Python 3.x
- pyqt6
- opencv-python
- sounddevice
- pyaudio

## Requerimientos
- Python 3.x 
- numpy
- sounddevice
- pyaudio
- mss
- opencv-python
- moviepy
- pyqt6
- PyQtWebEngine
- pypiwin32
- screeninfo
- qtawesome
- pywin32

## Instalación desde CLI
1. Clona el repositorio: 
git clone https://github.com/MixDark/GrabadorPantalla.git
2. Instala las dependencias:
pip install -r requirements.txt
3. Ejecuta la aplicación:
python main.py

## Uso
1. Abre la aplicación y elige una pantalla
2. Haz clic en el boton "Iniciar" para que empiece a grabar
3. Haz clic en el boton "Detener" y esperar a que la grabación se guarde.
4. Si deseas personalización lo puedes hacer en la pestaña "Configuraciones"

## Estructura del proyecto

![image](https://github.com/user-attachments/assets/3a3c7eee-d9d0-403b-91da-fc03c3b73088)
