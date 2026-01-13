"""
Configuración del sistema de vigilancia distribuida del zoológico.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración general del sistema"""
    
    # Configuración del cluster local
    LOCAL_CLUSTER_ENABLED = True
    YOLO_MODEL_PATH = os.getenv('YOLO_MODEL_PATH', 'yolov8n.pt')
    CAMERA_FEED_URLS = os.getenv('CAMERA_FEED_URLS', '').split(',')
    ALERT_THRESHOLD = float(os.getenv('ALERT_THRESHOLD', '0.7'))
    
    # Configuración de la nube
    CLOUD_ENABLED = True
    CLOUD_STORAGE_BUCKET = os.getenv('CLOUD_STORAGE_BUCKET', 'zoo-historical-data')
    CLOUD_REGION = os.getenv('CLOUD_REGION', 'us-east-1')
    
    # Configuración de procesamiento distribuido
    LOCAL_PROCESSING_PRIORITY = ['real-time', 'urgent', 'escape-detection']
    CLOUD_PROCESSING_PRIORITY = ['historical', 'trends', 'analytics']
    DATA_SYNC_INTERVAL = int(os.getenv('DATA_SYNC_INTERVAL', '3600'))  # segundos
    
    # Animales a detectar
    ANIMAL_CLASSES = [
        'bear', 'elephant', 'giraffe', 'horse', 'zebra',
        'cat', 'dog', 'bird', 'cow', 'sheep'
    ]
