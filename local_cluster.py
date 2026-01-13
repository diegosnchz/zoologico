"""
Módulo del cluster local para detección en tiempo real de escapes de animales.
Utiliza YOLO para procesar feeds de cámaras y detectar animales fuera de sus recintos.
"""
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LocalCluster:
    """
    Cluster local que procesa video en tiempo real para detectar escapes de animales.
    Utiliza YOLO para detección de objetos y prioriza alertas urgentes.
    """
    
    def __init__(self, model_path: str, alert_threshold: float = 0.7):
        """
        Inicializa el cluster local con el modelo YOLO.
        
        Args:
            model_path: Ruta al modelo YOLO
            alert_threshold: Umbral de confianza para generar alertas
        """
        self.model_path = model_path
        self.alert_threshold = alert_threshold
        self.model = None
        self.active_cameras = {}
        self.alerts = []
        
        logger.info(f"Inicializando cluster local con modelo: {model_path}")
    
    def load_model(self):
        """Carga el modelo YOLO para detección de animales."""
        try:
            from ultralytics import YOLO
            self.model = YOLO(self.model_path)
            logger.info("Modelo YOLO cargado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error al cargar modelo YOLO: {e}")
            return False
    
    def process_camera_feed(self, camera_id: str, frame: np.ndarray) -> Dict:
        """
        Procesa un frame de video para detectar animales.
        
        Args:
            camera_id: Identificador único de la cámara
            frame: Frame de video (imagen numpy array)
            
        Returns:
            Diccionario con resultados de detección
        """
        if self.model is None:
            logger.warning("Modelo no cargado, usando modo simulado")
            return self._simulate_detection(camera_id, frame)
        
        try:
            results = self.model(frame, verbose=False)
            detections = self._parse_results(results, camera_id)
            
            # Verificar si hay escapes (animales detectados con alta confianza)
            if detections['has_escape']:
                self._trigger_alert(camera_id, detections)
            
            return detections
            
        except Exception as e:
            logger.error(f"Error procesando frame de cámara {camera_id}: {e}")
            return {'error': str(e), 'camera_id': camera_id}
    
    def _parse_results(self, results, camera_id: str) -> Dict:
        """Parsea resultados de YOLO y genera estructura de datos."""
        detections = {
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat(),
            'animals': [],
            'has_escape': False,
            'confidence_scores': []
        }
        
        for result in results:
            for box in result.boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                detections['confidence_scores'].append(confidence)
                
                if confidence >= self.alert_threshold:
                    detections['animals'].append({
                        'class': class_name,
                        'confidence': confidence,
                        'bbox': box.xyxy[0].tolist()
                    })
                    detections['has_escape'] = True
        
        return detections
    
    def _simulate_detection(self, camera_id: str, frame: np.ndarray) -> Dict:
        """Simula detección cuando el modelo no está disponible (para testing)."""
        return {
            'camera_id': camera_id,
            'timestamp': datetime.now().isoformat(),
            'animals': [],
            'has_escape': False,
            'confidence_scores': [],
            'simulated': True
        }
    
    def _trigger_alert(self, camera_id: str, detections: Dict):
        """
        Genera una alerta de escape de animal.
        
        Args:
            camera_id: ID de la cámara que detectó el escape
            detections: Datos de detección
        """
        alert = {
            'type': 'ANIMAL_ESCAPE',
            'priority': 'URGENT',
            'camera_id': camera_id,
            'timestamp': detections['timestamp'],
            'animals': detections['animals'],
            'processed_by': 'local_cluster'
        }
        
        self.alerts.append(alert)
        logger.warning(f"⚠️  ALERTA DE ESCAPE - Cámara {camera_id}: "
                      f"{len(detections['animals'])} animal(es) detectado(s)")
        
        return alert
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Obtiene las alertas más recientes."""
        return self.alerts[-limit:]
    
    def process_video_stream(self, video_source: str, camera_id: str):
        """
        Procesa un stream de video en tiempo real.
        
        Args:
            video_source: URL o ruta del video
            camera_id: Identificador de la cámara
        """
        cap = cv2.VideoCapture(video_source)
        
        if not cap.isOpened():
            logger.error(f"No se pudo abrir la fuente de video: {video_source}")
            return
        
        logger.info(f"Procesando stream de cámara {camera_id}")
        self.active_cameras[camera_id] = True
        
        frame_count = 0
        try:
            while self.active_cameras.get(camera_id, False):
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Procesar cada N frames para optimizar rendimiento
                if frame_count % 5 == 0:
                    self.process_camera_feed(camera_id, frame)
                
                frame_count += 1
                
        finally:
            cap.release()
            logger.info(f"Stream de cámara {camera_id} finalizado")
    
    def stop_camera(self, camera_id: str):
        """Detiene el procesamiento de una cámara específica."""
        self.active_cameras[camera_id] = False
        logger.info(f"Cámara {camera_id} detenida")
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del cluster local."""
        return {
            'active_cameras': sum(1 for v in self.active_cameras.values() if v),
            'total_alerts': len(self.alerts),
            'model_loaded': self.model is not None,
            'cluster_type': 'local',
            'processing_capability': 'real-time'
        }
