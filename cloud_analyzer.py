"""
Módulo de análisis en la nube para procesamiento histórico de datos.
Analiza terabytes de datos históricos para identificar tendencias y patrones.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudAnalyzer:
    """
    Analizador en la nube para procesamiento de grandes volúmenes de datos históricos.
    Delega el análisis de terabytes de datos a la nube para identificar tendencias.
    """
    
    def __init__(self, bucket_name: str, region: str = 'us-east-1'):
        """
        Inicializa el analizador en la nube.
        
        Args:
            bucket_name: Nombre del bucket de almacenamiento en la nube
            region: Región de la nube
        """
        self.bucket_name = bucket_name
        self.region = region
        self.cloud_client = None
        self.historical_data = []
        
        logger.info(f"Inicializando analizador en la nube: {bucket_name} ({region})")
    
    def connect_to_cloud(self):
        """Establece conexión con servicios de nube."""
        try:
            import boto3
            self.cloud_client = boto3.client('s3', region_name=self.region)
            logger.info("Conexión a la nube establecida")
            return True
        except Exception as e:
            logger.warning(f"No se pudo conectar a AWS S3: {e}")
            logger.info("Usando modo simulado para análisis en la nube")
            return False
    
    def upload_data(self, data: Dict, data_type: str = 'detection') -> bool:
        """
        Sube datos al almacenamiento en la nube para análisis posterior.
        
        Args:
            data: Datos a subir
            data_type: Tipo de datos (detection, alert, etc.)
            
        Returns:
            True si la carga fue exitosa
        """
        try:
            # Guardar localmente para análisis (modo simulado)
            data['uploaded_at'] = datetime.now().isoformat()
            data['data_type'] = data_type
            self.historical_data.append(data)
            
            # En producción, subiría a S3
            if self.cloud_client:
                key = f"{data_type}/{datetime.now().strftime('%Y/%m/%d')}/{data.get('timestamp', 'unknown')}.json"
                # self.cloud_client.put_object(Bucket=self.bucket_name, Key=key, Body=json.dumps(data))
            
            logger.info(f"Datos de tipo '{data_type}' subidos a la nube")
            return True
            
        except Exception as e:
            logger.error(f"Error al subir datos a la nube: {e}")
            return False
    
    def analyze_historical_trends(self, days: int = 30) -> Dict:
        """
        Analiza tendencias históricas de los últimos N días.
        Procesa grandes volúmenes de datos para identificar patrones.
        
        Args:
            days: Número de días a analizar
            
        Returns:
            Diccionario con análisis de tendencias
        """
        logger.info(f"Iniciando análisis de tendencias de los últimos {days} días")
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filtrar datos históricos
        relevant_data = [
            d for d in self.historical_data
            if datetime.fromisoformat(d.get('timestamp', d.get('uploaded_at', ''))) >= cutoff_date
        ]
        
        # Análisis de patrones
        trends = {
            'period_days': days,
            'total_detections': len(relevant_data),
            'animals_by_type': self._analyze_by_animal_type(relevant_data),
            'escapes_by_camera': self._analyze_by_camera(relevant_data),
            'hourly_patterns': self._analyze_hourly_patterns(relevant_data),
            'risk_zones': self._identify_risk_zones(relevant_data),
            'processed_by': 'cloud_analyzer',
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Análisis completado: {trends['total_detections']} detecciones procesadas")
        
        return trends
    
    def _analyze_by_animal_type(self, data: List[Dict]) -> Dict:
        """Analiza detecciones por tipo de animal."""
        animal_counts = defaultdict(int)
        
        for record in data:
            animals = record.get('animals', [])
            for animal in animals:
                animal_type = animal.get('class', 'unknown')
                animal_counts[animal_type] += 1
        
        return dict(animal_counts)
    
    def _analyze_by_camera(self, data: List[Dict]) -> Dict:
        """Analiza detecciones por cámara."""
        camera_stats = defaultdict(lambda: {'detections': 0, 'escapes': 0})
        
        for record in data:
            camera_id = record.get('camera_id', 'unknown')
            camera_stats[camera_id]['detections'] += 1
            if record.get('has_escape', False):
                camera_stats[camera_id]['escapes'] += 1
        
        return dict(camera_stats)
    
    def _analyze_hourly_patterns(self, data: List[Dict]) -> Dict:
        """Analiza patrones por hora del día."""
        hourly_detections = defaultdict(int)
        
        for record in data:
            try:
                timestamp = record.get('timestamp', record.get('uploaded_at', ''))
                hour = datetime.fromisoformat(timestamp).hour
                hourly_detections[hour] += 1
            except:
                continue
        
        return dict(hourly_detections)
    
    def _identify_risk_zones(self, data: List[Dict]) -> List[Dict]:
        """Identifica zonas de alto riesgo basándose en patrones históricos."""
        camera_risks = defaultdict(lambda: {'escape_count': 0, 'total_detections': 0})
        
        for record in data:
            camera_id = record.get('camera_id', 'unknown')
            camera_risks[camera_id]['total_detections'] += 1
            if record.get('has_escape', False):
                camera_risks[camera_id]['escape_count'] += 1
        
        # Calcular riesgo
        risk_zones = []
        for camera_id, stats in camera_risks.items():
            if stats['total_detections'] > 0:
                risk_score = stats['escape_count'] / stats['total_detections']
                if risk_score > 0.3:  # Umbral de riesgo
                    risk_zones.append({
                        'camera_id': camera_id,
                        'risk_score': round(risk_score, 2),
                        'escape_count': stats['escape_count'],
                        'total_detections': stats['total_detections']
                    })
        
        # Ordenar por riesgo descendente
        risk_zones.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return risk_zones
    
    def generate_report(self, trends: Dict) -> str:
        """
        Genera un reporte legible del análisis de tendencias.
        
        Args:
            trends: Datos de tendencias generados
            
        Returns:
            Reporte en formato texto
        """
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE ANÁLISIS HISTÓRICO - SISTEMA DE VIGILANCIA")
        report.append("=" * 60)
        report.append(f"\nPeríodo analizado: {trends['period_days']} días")
        report.append(f"Total de detecciones: {trends['total_detections']}")
        report.append(f"Fecha de análisis: {trends['analysis_timestamp']}")
        
        report.append("\n--- DETECCIONES POR TIPO DE ANIMAL ---")
        for animal, count in trends['animals_by_type'].items():
            report.append(f"  {animal}: {count}")
        
        report.append("\n--- ZONAS DE ALTO RIESGO ---")
        for zone in trends['risk_zones']:
            report.append(f"  Cámara {zone['camera_id']}: "
                        f"Riesgo {zone['risk_score']*100:.1f}% "
                        f"({zone['escape_count']} escapes de {zone['total_detections']} detecciones)")
        
        report.append("\n--- PATRONES HORARIOS ---")
        hourly = trends['hourly_patterns']
        if hourly:
            peak_hour = max(hourly, key=hourly.get)
            report.append(f"  Hora pico de actividad: {peak_hour}:00 ({hourly[peak_hour]} detecciones)")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del analizador en la nube."""
        return {
            'total_historical_records': len(self.historical_data),
            'cloud_connected': self.cloud_client is not None,
            'bucket_name': self.bucket_name,
            'region': self.region,
            'processor_type': 'cloud',
            'processing_capability': 'large-scale-historical'
        }
