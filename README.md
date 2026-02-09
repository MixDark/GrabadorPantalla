# 🎬 Grabador de Pantalla

Una aplicación profesional de grabación de pantalla desarrollada en Python con interfaz gráfica PyQt6, diseñada para capturar, procesar y guardar videos de alta calidad.

## 📋 Características

### 🎥 Grabación de video
- ✅ Soporte para múltiples pantallas/monitores
- ✅ Grabación en tiempo real con FPS ajustable (actualmente 15 FPS)
- ✅ Múltiples formatos de salida: MP4, AVI, MOV
- ✅ Captura de región completa de la pantalla

### 🎙️ Audio
- ✅ Grabación de audio del micrófono
- ✅ Soporte para micrófono de múltiples canales
- ✅ Control de volumen del micrófono
- ✅ Prueba de micrófono integrada
- ✅ Grabación de audio del sistema (cuando está disponible)
- ✅ Normalización y compresión de audio

### 🖱️ Personalización del cursor
- ✅ Mostrar/ocultar cursor durante grabación
- ✅ Múltiples estilos: Predeterminado, círculos (blanco, rojo, verde, azul), cruz

### ⌨️ Atajos de teclado
- ✅ Atajos de teclado personalizables para iniciar/detener grabación
- ✅ Configuración global del atajo
- ✅ Minimizar ventana automáticamente al iniciar

### 📊 Interfaz de usuario
- ✅ Interfaz con 3 pestañas (Grabación, Configuraciones, Registro)
- ✅ Previsualizaciones de pantallas disponibles
- ✅ Contador de tiempo en vivo
- ✅ Barra de progreso
- ✅ Registro de eventos detallado

### 📁 Gestión de archivos
- ✅ Seleccionar ubicación personalizada para grabaciones
- ✅ Acceso rápido a la carpeta de grabaciones
- ✅ Verificación de archivos existentes antes de sobrescribir

## 🚀 Requisitos previos

### Sistema operativo
- Windows 10/11 (actualmente optimizado para Windows con APIs específicas)

### Python
- Python 3.10 o superior

### Dependencias del sistema
- FFmpeg (recomendado para mejor compatibilidad de video)

## 📦 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/grabador-pantalla.git
cd grabador-pantalla
```

### 2. Crear entorno virtual (opcional pero recomendado)
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Instalar dependencias del sistema (Windows)
```bash
pip install pypiwin32
python Scripts/pywin32_postinstall.py -install
```

## 🎯 Uso

### Ejecutar la aplicación
```bash
python main.py
```

### Flujo básico:
1. **Seleccionar pantalla**: Elige la pantalla/monitor a grabar
2. **Configurar opciones**: Ajusta nombre, formato, audio y cursor
3. **Iniciar grabación**: Presiona "Iniciar" o usa el atajo de teclado
4. **Detener grabación**: Presiona "Detener" o usa el atajo
5. **Esperar procesamiento**: El video se procesa y guarda automáticamente

## ⚙️ Configuración

La aplicación permite personalizar:

- **Nombre de archivo**: Nombre personalizado para la grabación
- **Formato**: .mp4, .avi, .mov
- **Ubicación**: Dónde guardar las grabaciones
- **Audio del micrófono**: Activar/desactivar y ajustar volumen
- **Audio del sistema**: Activar/desactivar y ajustar volumen
- **Estilo del cursor**: Diferentes opciones de visualización
- **Atajo de teclado**: Configurar combinación para iniciar/detener
- **Minimizar al iniciar**: Ocultar ventana automáticamente

## 📝 Registro de eventos

Todos los eventos de la aplicación se registran en:
- **Pantalla**: En la pestaña "Registro de eventos"
- **Archivo**: En `app.log` en el directorio raíz

## 🛠️ Estructura del proyecto

```
grabador-pantalla/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias Python
├── README.md              # Este archivo
├── CHANGELOG.md           # Historial de cambios
├── .gitignore             # Archivos a ignorar en git
├── app.log                # Registro de eventos
└── grabaciones/           # Carpeta de grabaciones
    └── tmp/               # Archivos temporales durante grabación
```

## 🐛 Solución de problemas

### Problema: "El micrófono no se detecta"
**Solución**: Recargue la lista de dispositivos o reinicie la aplicación

### Problema: "Error al procesar video"
**Solución**: Asegúrese de tener FFmpeg instalado y en el PATH

### Problema: "No se puede escribir archivo temporal"
**Solución**: Verifique permisos de escritura en la carpeta de grabaciones

### Problema: "AudioFileClip error"
**Solución**: Instale FFmpeg: `pip install imageio-ffmpeg`

## 🔮 Mejoras futuras planeadas

- [ ] Grabación de región personalizada (captura de área)
- [ ] Pausa/Reanuda de grabación sin detener
- [ ] Historial de grabaciones con miniaturas
- [ ] Editor de video integrado (corte, recorte, watermark)
- [ ] Soporte para grabación en Linux y macOS
- [ ] Panel de estadísticas de grabación
- [ ] Configuración oscura personalizable
- [ ] Grabación con codificadores de hardware (NVIDIA NVENC, Intel Quick Sync)
- [ ] API REST para grabación remota
- [ ] Validación automática de dependencias

## 💻 Requisitos técnicos

| Componente | Versión |
|-----------|---------|
| Python | 3.10+ |
| PyQt6 | 6.0+ |
| OpenCV | 4.5+ |
| MoviePy | 1.0+ |
| NumPy | 1.20+ |
| SoundDevice | 0.4+ |
| PyAudio | 0.2+ |

## 📄 Licencia

Este proyecto está bajo licencia MIT. Consulte el archivo LICENSE para más detalles.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ❓ FAQ

**P: ¿Funciona en Linux o macOS?**
R: Actualmente está optimizado para Windows. Se requieren ajustes para otros SO.

**P: ¿Cuál es el tamaño de archivo típico?**
R: Depende de la resolución y duración. ~100-200 MB por minuto de grabación en MP4 HD.

**P: ¿Puedo editar los videos después de grabar?**
R: Actualmente no, pero es una característica planeada.

**P: ¿Es posible grabar solo una región?**
R: No en esta versión, es una mejora futura.

## 📧 Contacto

Para reportes de bugs o sugerencias: [tu-email@ejemplo.com]

## 👏 Agradecimientos

- PyQt6 por la interfaz gráfica
- OpenCV por el procesamiento de video
- FFmpeg por la codificación de video
- La comunidad de Python por las herramientas utilizadas

---

**Última actualización**: 7 febrero 2026  
**Versión**: 1.0.0
