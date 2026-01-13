# 🦁 Sistema de Vigilancia Distribuida para Zoológico

Sistema de computación distribuida para detección de escapes de animales en tiempo real y análisis histórico de patrones.

## 🌐 Interfaz Web

El sistema incluye una **aplicación web completa** para monitorear y gestionar el sistema de vigilancia:

![Sistema de Vigilancia Web](https://github.com/user-attachments/assets/8581b7b8-950a-4331-8d08-a186794cd8c0)

### Características de la Interfaz Web:
- 📊 **Dashboard en tiempo real** con estadísticas del sistema
- 📹 **Monitoreo de cámaras** con estado en vivo
- ⚠️ **Panel de alertas** para escapes detectados
- ☁️ **Análisis histórico** con reportes visuales
- 🏗️ **Vista de arquitectura** del sistema distribuido
- 🎮 **Controles interactivos** para iniciar/detener monitoreo

## 🎓 Entrenamiento del Modelo YOLO

El sistema incluye herramientas completas para entrenar tu propio modelo YOLO personalizado:

### Proceso de Entrenamiento

1. **Preparar imágenes:**
   ```bash
   # Coloca tus imágenes en training_data/images/
   python prepare_training_data.py
   ```

2. **Etiquetar imágenes:**
   - Usa LabelImg, Roboflow o herramientas similares
   - Formato YOLO: `<class_id> <x_center> <y_center> <width> <height>`
   - Clases: 0=escape, 1=elephant, 2=giraffe, 3=lion, etc.

3. **Entrenar modelo:**
   ```bash
   python train_model.py
   # Selecciona: Entrenamiento completo (50 épocas)
   ```

4. **Integrar modelo entrenado:**
   ```bash
   export YOLO_MODEL_PATH=training_data/models/animal_escape_detector.pt
   python web_app.py
   ```

📖 **[Guía Completa de Entrenamiento](training_data/TRAINING_GUIDE.md)**

## 📋 Descripción

Este sistema implementa una arquitectura de computación distribuida que combina:

- **Cluster Local**: Procesamiento en tiempo real usando YOLO para detectar escapes de animales desde feeds de cámaras
- **Análisis en la Nube**: Procesamiento de terabytes de datos históricos para identificar tendencias y patrones

Similar a sistemas web o asistentes de IA, el sistema distribuye tareas globalmente vía Internet, optimizando recursos según las fortalezas de cada componente:
- **Local**: Poder de cómputo para urgencias (baja latencia)
- **Nube**: Escalabilidad para grandes volúmenes de datos

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│        CÁMARAS DE VIGILANCIA               │
│     (Feeds de video en tiempo real)         │
└────────────────┬────────────────────────────┘
                 │
        ┌────────▼────────┐
        │  COORDINADOR    │
        │   DISTRIBUIDO   │
        └────────┬────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼────────┐       ┌────────▼───┐
│  CLUSTER   │       │    NUBE    │
│   LOCAL    │◄──────┤   (CLOUD)  │
│            │ sync  │            │
│ • YOLO     │       │ • Terabytes│
│ • Tiempo   │       │ • Análisis │
│   Real     │       │   Histórico│
│ • Alertas  │       │ • Tendencias│
└────────────┘       └────────────┘
```

## 🚀 Características

### Cluster Local
- ✅ Detección en tiempo real con YOLO (You Only Look Once)
- ✅ Procesamiento de múltiples feeds de cámaras simultáneamente
- ✅ Generación de alertas urgentes ante escapes
- ✅ Baja latencia para respuesta inmediata
- ✅ Sincronización automática de datos a la nube

### Análisis en la Nube
- ✅ Procesamiento de grandes volúmenes de datos históricos
- ✅ Análisis de tendencias y patrones
- ✅ Identificación de zonas de alto riesgo
- ✅ Análisis de patrones temporales (horarios, días)
- ✅ Generación de reportes detallados
- ✅ Escalabilidad para terabytes de datos

### Coordinador Distribuido
- ✅ Delegación inteligente de tareas
- ✅ Tareas urgentes → Cluster local
- ✅ Análisis masivo → Nube
- ✅ Optimización automática de recursos
- ✅ Monitoreo del estado del sistema

## 📦 Instalación

### Requisitos
- Python 3.8+
- OpenCV
- NumPy
- Ultralytics (YOLO)
- Boto3 (para integración con AWS S3)

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

## 🔧 Configuración

Cree un archivo `.env` con las siguientes variables (opcional):

```env
# Configuración del cluster local
YOLO_MODEL_PATH=yolov8n.pt
CAMERA_FEED_URLS=rtsp://camera1,rtsp://camera2
ALERT_THRESHOLD=0.7

# Configuración de la nube
CLOUD_STORAGE_BUCKET=zoo-historical-data
CLOUD_REGION=us-east-1
DATA_SYNC_INTERVAL=3600
```

## 💻 Uso

### Opción 1: Interfaz Web (Recomendado)

La forma más fácil de usar el sistema es a través de la interfaz web:

```bash
# Desplegar e iniciar la aplicación web
./start_web.sh

# O directamente con Python
python web_app.py
```

Luego abre tu navegador en: **http://localhost:5000**

La interfaz web proporciona:
- Control completo del sistema (inicializar, monitorear, detener)
- Visualización de estadísticas en tiempo real
- Monitoreo de 4 cámaras simultáneamente
- Panel de alertas de escapes
- Análisis histórico con reportes visuales

### Opción 2: Ejecución del sistema completo (CLI)

```bash
python main.py
```

### Opción 3: Uso programático

```python
from distributed_coordinator import DistributedCoordinator
from config import Config
import numpy as np

# Inicializar coordinador
config = Config()
coordinator = DistributedCoordinator(config)
coordinator.initialize_system()

# Procesar frame en tiempo real (delegado a cluster local)
frame = np.zeros((480, 640, 3), dtype=np.uint8)
result = coordinator.process_realtime_feed('camera_1', frame)

# Analizar datos históricos (delegado a la nube)
trends = coordinator.analyze_historical_data(days=30)

# Obtener estado del sistema
status = coordinator.get_system_status()
```

## 📊 Componentes del Sistema

### 1. LocalCluster (`local_cluster.py`)
Gestiona el procesamiento en tiempo real:
- Carga y ejecuta modelo YOLO
- Procesa frames de video
- Detecta animales con alto nivel de confianza
- Genera alertas de escape
- Mantiene estadísticas de detecciones

### 2. CloudAnalyzer (`cloud_analyzer.py`)
Gestiona el análisis en la nube:
- Almacena datos históricos
- Analiza tendencias temporales
- Identifica zonas de riesgo
- Genera reportes detallados
- Procesa grandes volúmenes de datos

### 3. DistributedCoordinator (`distributed_coordinator.py`)
Coordina la distribución de tareas:
- Inicializa componentes del sistema
- Delega tareas según prioridad
- Sincroniza datos entre local y nube
- Monitorea estado del sistema
- Optimiza uso de recursos

### 4. Config (`config.py`)
Gestiona la configuración del sistema:
- Parámetros del cluster local
- Configuración de la nube
- Prioridades de procesamiento
- Umbrales de detección

## 🎯 Ejemplos de Uso

### Detección en Tiempo Real

```python
from local_cluster import LocalCluster
import cv2

# Inicializar cluster local
cluster = LocalCluster(model_path='yolov8n.pt', alert_threshold=0.7)
cluster.load_model()

# Procesar video de cámara
video_source = 'rtsp://192.168.1.100/stream'
cluster.process_video_stream(video_source, camera_id='camera_entrance')

# Obtener alertas
alerts = cluster.get_recent_alerts(limit=10)
```

### Análisis Histórico

```python
from cloud_analyzer import CloudAnalyzer

# Inicializar analizador
analyzer = CloudAnalyzer(bucket_name='zoo-data', region='us-east-1')
analyzer.connect_to_cloud()

# Analizar tendencias
trends = analyzer.analyze_historical_trends(days=30)
report = analyzer.generate_report(trends)
print(report)
```

## 🔍 Tipos de Tareas

El sistema categoriza y delega tareas automáticamente:

**Tareas Locales (Urgentes):**
- `real-time`: Procesamiento de video en tiempo real
- `urgent`: Alertas que requieren atención inmediata
- `escape-detection`: Detección de escapes de animales

**Tareas en la Nube (Masivas):**
- `historical`: Análisis de datos históricos
- `trends`: Identificación de tendencias
- `analytics`: Análisis avanzados de patrones

## 📈 Ventajas de la Computación Distribuida

1. **Optimización de Recursos**: Cada componente trabaja en lo que hace mejor
2. **Escalabilidad**: La nube maneja grandes volúmenes sin afectar procesamiento local
3. **Baja Latencia**: Procesamiento local para decisiones urgentes
4. **Redundancia**: Datos sincronizados entre local y nube
5. **Costo-Efectivo**: Usa recursos locales para tareas frecuentes, nube para análisis pesados

## 🛠️ Desarrollo

### Estructura del Proyecto

```
zoologico/
├── README.md
├── requirements.txt
├── config.py                    # Configuración del sistema
├── local_cluster.py            # Cluster local (YOLO + tiempo real)
├── cloud_analyzer.py           # Analizador en la nube
├── distributed_coordinator.py  # Coordinador distribuido
└── main.py                     # Aplicación principal
```

## 🔒 Seguridad

- Las credenciales de la nube deben configurarse mediante variables de entorno
- No incluir credenciales en el código fuente
- Usar IAM roles apropiados para acceso a servicios de nube
- Implementar autenticación para acceso a feeds de cámaras

## 📝 Licencia

Este proyecto es código abierto y está disponible bajo licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork del repositorio
2. Crear una rama para tu feature
3. Commit de tus cambios
4. Push a la rama
5. Abrir un Pull Request

## 📧 Contacto

Para preguntas o sugerencias, por favor abrir un issue en GitHub.

---

**Nota**: Este es un sistema de demostración que ilustra principios de computación distribuida. Para uso en producción, se requiere:
- Configuración completa de servicios de nube (AWS, Azure, GCP)
- Implementación de seguridad robusta
- Monitoreo y logging avanzado
- Manejo de errores y recuperación
- Testing exhaustivo