"""
Coordinador de computación distribuida para el sistema de vigilancia del zoológico.
Distribuye tareas entre el cluster local (urgencias) y la nube (análisis histórico).
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
from local_cluster import LocalCluster
from cloud_analyzer import CloudAnalyzer
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DistributedCoordinator:
    """
    Coordinador que distribuye tareas de computación entre recursos locales y en la nube.
    - Local: Procesamiento en tiempo real, detección urgente de escapes
    - Nube: Análisis histórico de terabytes, identificación de tendencias
    """
    
    def __init__(self, config: Config = None):
        """
        Inicializa el coordinador distribuido.
        
        Args:
            config: Configuración del sistema
        """
        self.config = config or Config()
        self.local_cluster = None
        self.cloud_analyzer = None
        self.task_stats = {
            'local_tasks': 0,
            'cloud_tasks': 0,
            'total_tasks': 0
        }
        
        logger.info("Inicializando coordinador de computación distribuida")
    
    def initialize_system(self):
        """Inicializa todos los componentes del sistema distribuido."""
        logger.info("=" * 60)
        logger.info("SISTEMA DE VIGILANCIA DISTRIBUIDA - ZOOLÓGICO")
        logger.info("=" * 60)
        
        # Inicializar cluster local
        if self.config.LOCAL_CLUSTER_ENABLED:
            logger.info("\n🖥️  Inicializando CLUSTER LOCAL para procesamiento en tiempo real...")
            self.local_cluster = LocalCluster(
                model_path=self.config.YOLO_MODEL_PATH,
                alert_threshold=self.config.ALERT_THRESHOLD
            )
            self.local_cluster.load_model()
            logger.info("✓ Cluster local listo para detección urgente de escapes")
        
        # Inicializar analizador en la nube
        if self.config.CLOUD_ENABLED:
            logger.info("\n☁️  Inicializando ANÁLISIS EN LA NUBE para datos históricos...")
            self.cloud_analyzer = CloudAnalyzer(
                bucket_name=self.config.CLOUD_STORAGE_BUCKET,
                region=self.config.CLOUD_REGION
            )
            self.cloud_analyzer.connect_to_cloud()
            logger.info("✓ Analizador en la nube listo para procesamiento masivo")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Sistema distribuido inicializado correctamente")
        logger.info("=" * 60 + "\n")
    
    def delegate_task(self, task_type: str, task_data: Dict) -> Dict:
        """
        Delega una tarea al recurso apropiado según su naturaleza.
        
        Args:
            task_type: Tipo de tarea (real-time, urgent, historical, etc.)
            task_data: Datos de la tarea
            
        Returns:
            Resultado de la tarea procesada
        """
        self.task_stats['total_tasks'] += 1
        
        # Decisión de delegación basada en prioridades
        if task_type in self.config.LOCAL_PROCESSING_PRIORITY:
            return self._delegate_to_local(task_type, task_data)
        elif task_type in self.config.CLOUD_PROCESSING_PRIORITY:
            return self._delegate_to_cloud(task_type, task_data)
        else:
            logger.warning(f"Tipo de tarea desconocido: {task_type}, delegando a local por defecto")
            return self._delegate_to_local(task_type, task_data)
    
    def _delegate_to_local(self, task_type: str, task_data: Dict) -> Dict:
        """
        Delega tarea urgente al cluster local.
        Optimizado para: Baja latencia, procesamiento en tiempo real
        """
        logger.info(f"⚡ Delegando tarea URGENTE a CLUSTER LOCAL: {task_type}")
        self.task_stats['local_tasks'] += 1
        
        if not self.local_cluster:
            return {'error': 'Cluster local no disponible', 'task_type': task_type}
        
        try:
            if task_type == 'real-time':
                # Procesar frame de video en tiempo real
                camera_id = task_data.get('camera_id', 'unknown')
                frame = task_data.get('frame')
                result = self.local_cluster.process_camera_feed(camera_id, frame)
                
                # Si hay detección, subir a la nube para análisis histórico
                if result.get('has_escape'):
                    self._sync_to_cloud(result)
                
                return result
            
            elif task_type == 'urgent' or task_type == 'escape-detection':
                # Procesar alerta urgente
                result = task_data
                result['processed_by'] = 'local_cluster'
                result['processed_at'] = datetime.now().isoformat()
                return result
            
            else:
                return task_data
                
        except Exception as e:
            logger.error(f"Error en procesamiento local: {e}")
            return {'error': str(e), 'task_type': task_type}
    
    def _delegate_to_cloud(self, task_type: str, task_data: Dict) -> Dict:
        """
        Delega tarea de análisis masivo a la nube.
        Optimizado para: Alto volumen, procesamiento de terabytes
        """
        logger.info(f"☁️  Delegando tarea de ANÁLISIS MASIVO a LA NUBE: {task_type}")
        self.task_stats['cloud_tasks'] += 1
        
        if not self.cloud_analyzer:
            return {'error': 'Analizador en la nube no disponible', 'task_type': task_type}
        
        try:
            if task_type == 'historical':
                # Análisis histórico de datos
                days = task_data.get('days', 30)
                result = self.cloud_analyzer.analyze_historical_trends(days)
                return result
            
            elif task_type == 'trends':
                # Análisis de tendencias
                days = task_data.get('days', 7)
                trends = self.cloud_analyzer.analyze_historical_trends(days)
                report = self.cloud_analyzer.generate_report(trends)
                return {'trends': trends, 'report': report}
            
            elif task_type == 'analytics':
                # Análisis avanzado
                result = task_data
                result['processed_by'] = 'cloud_analyzer'
                result['processed_at'] = datetime.now().isoformat()
                return result
            
            else:
                return task_data
                
        except Exception as e:
            logger.error(f"Error en procesamiento en la nube: {e}")
            return {'error': str(e), 'task_type': task_type}
    
    def _sync_to_cloud(self, data: Dict):
        """
        Sincroniza datos del cluster local a la nube para análisis posterior.
        
        Args:
            data: Datos a sincronizar
        """
        if self.cloud_analyzer:
            try:
                self.cloud_analyzer.upload_data(data, data_type='detection')
                logger.debug("Datos sincronizados a la nube para análisis histórico")
            except Exception as e:
                logger.error(f"Error al sincronizar datos a la nube: {e}")
    
    def process_realtime_feed(self, camera_id: str, frame):
        """
        Procesa un frame de video en tiempo real.
        Delegado al cluster local por su naturaleza urgente.
        
        Args:
            camera_id: ID de la cámara
            frame: Frame de video
            
        Returns:
            Resultado de detección
        """
        task_data = {
            'camera_id': camera_id,
            'frame': frame,
            'timestamp': datetime.now().isoformat()
        }
        
        return self.delegate_task('real-time', task_data)
    
    def analyze_historical_data(self, days: int = 30) -> Dict:
        """
        Analiza datos históricos.
        Delegado a la nube por el volumen masivo de datos.
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Análisis de tendencias
        """
        task_data = {'days': days}
        return self.delegate_task('historical', task_data)
    
    def get_system_status(self) -> Dict:
        """Obtiene el estado completo del sistema distribuido."""
        status = {
            'coordinator': {
                'tasks_delegated': self.task_stats,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        if self.local_cluster:
            status['local_cluster'] = self.local_cluster.get_stats()
        
        if self.cloud_analyzer:
            status['cloud_analyzer'] = self.cloud_analyzer.get_stats()
        
        return status
    
    def print_system_architecture(self):
        """Imprime la arquitectura del sistema distribuido."""
        print("\n" + "=" * 70)
        print("ARQUITECTURA DE COMPUTACIÓN DISTRIBUIDA - SISTEMA DE VIGILANCIA")
        print("=" * 70)
        print("""
┌─────────────────────────────────────────────────────────────────────┐
│                        CÁMARAS DE VIGILANCIA                        │
│                     (Feeds de video en tiempo real)                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  COORDINADOR    │
                    │   DISTRIBUIDO   │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐       ┌───────▼────────┐
        │ CLUSTER LOCAL  │       │  NUBE (CLOUD)  │
        │                │       │                │
        │ • YOLO Model   │       │ • Terabytes de │
        │ • Tiempo Real  │       │   datos        │
        │ • Detección    │       │ • Análisis     │
        │   Urgente      │◄──────┤   Histórico    │
        │ • Alertas      │ sync  │ • Tendencias   │
        └────────────────┘       └────────────────┘
             Latencia              Escalabilidad
             Mínima                Masiva
        
DISTRIBUCIÓN DE TAREAS:
• Local:  Procesamiento en tiempo real, detección urgente de escapes
• Nube:   Análisis histórico, identificación de tendencias, big data

VENTAJAS:
✓ Aprovecha fortalezas de cada recurso
✓ Poder local para urgencias (baja latencia)
✓ Nube para volumen masivo de datos
✓ Optimización de recursos distribuidos globalmente vía Internet
        """)
        print("=" * 70 + "\n")
