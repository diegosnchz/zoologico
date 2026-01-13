"""
Sistema principal de vigilancia distribuida para zoológico.
Coordina el procesamiento distribuido entre cluster local y nube.
"""
import numpy as np
from distributed_coordinator import DistributedCoordinator
from config import Config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Función principal del sistema de vigilancia."""
    
    # Inicializar configuración
    config = Config()
    
    # Crear coordinador distribuido
    coordinator = DistributedCoordinator(config)
    
    # Mostrar arquitectura del sistema
    coordinator.print_system_architecture()
    
    # Inicializar sistema
    coordinator.initialize_system()
    
    # Simular procesamiento en tiempo real (cluster local)
    print("\n" + "=" * 60)
    print("DEMO: Procesamiento en Tiempo Real (Cluster Local)")
    print("=" * 60)
    
    # Simular frame de cámara
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    for i in range(3):
        result = coordinator.process_realtime_feed(f'camera_{i+1}', dummy_frame)
        print(f"\nCámara {i+1} - Resultado: {result}")
    
    # Obtener alertas recientes
    if coordinator.local_cluster:
        alerts = coordinator.local_cluster.get_recent_alerts()
        print(f"\n📢 Alertas recientes: {len(alerts)}")
    
    # Simular análisis histórico (nube)
    print("\n" + "=" * 60)
    print("DEMO: Análisis Histórico Masivo (Nube)")
    print("=" * 60)
    
    # Simular carga de datos históricos
    if coordinator.cloud_analyzer:
        # Agregar datos de ejemplo
        for i in range(50):
            sample_data = {
                'camera_id': f'camera_{(i % 3) + 1}',
                'timestamp': '2024-01-01T12:00:00',
                'animals': [{'class': 'elephant', 'confidence': 0.85}] if i % 5 == 0 else [],
                'has_escape': i % 5 == 0
            }
            coordinator.cloud_analyzer.upload_data(sample_data, 'detection')
    
    # Ejecutar análisis de tendencias
    trends_result = coordinator.analyze_historical_data(days=30)
    
    if coordinator.cloud_analyzer and 'trends' not in trends_result:
        report = coordinator.cloud_analyzer.generate_report(trends_result)
        print(f"\n{report}")
    
    # Mostrar estado del sistema
    print("\n" + "=" * 60)
    print("ESTADO DEL SISTEMA DISTRIBUIDO")
    print("=" * 60)
    
    status = coordinator.get_system_status()
    
    print(f"\n📊 Estadísticas del Coordinador:")
    print(f"  • Total de tareas procesadas: {status['coordinator']['tasks_delegated']['total_tasks']}")
    print(f"  • Tareas locales (urgentes): {status['coordinator']['tasks_delegated']['local_tasks']}")
    print(f"  • Tareas en la nube (históricas): {status['coordinator']['tasks_delegated']['cloud_tasks']}")
    
    if 'local_cluster' in status:
        print(f"\n🖥️  Cluster Local:")
        local_stats = status['local_cluster']
        print(f"  • Cámaras activas: {local_stats['active_cameras']}")
        print(f"  • Total de alertas: {local_stats['total_alerts']}")
        print(f"  • Modelo cargado: {'Sí' if local_stats['model_loaded'] else 'No (modo simulado)'}")
        print(f"  • Capacidad: {local_stats['processing_capability']}")
    
    if 'cloud_analyzer' in status:
        print(f"\n☁️  Analizador en la Nube:")
        cloud_stats = status['cloud_analyzer']
        print(f"  • Registros históricos: {cloud_stats['total_historical_records']}")
        print(f"  • Bucket: {cloud_stats['bucket_name']}")
        print(f"  • Región: {cloud_stats['region']}")
        print(f"  • Capacidad: {cloud_stats['processing_capability']}")
    
    print("\n" + "=" * 60)
    print("✓ Demo completada exitosamente")
    print("=" * 60 + "\n")
    
    print("""
RESUMEN DE COMPUTACIÓN DISTRIBUIDA:
────────────────────────────────────────────────────────────
Este sistema demuestra cómo la computación distribuida optimiza
recursos aprovechando las fortalezas de cada componente:

• CLUSTER LOCAL: Procesa video en tiempo real con YOLO para
  detectar escapes de animales inmediatamente. Optimizado para
  baja latencia y respuesta urgente.

• NUBE: Analiza terabytes de datos históricos para identificar
  tendencias y patrones a largo plazo. Optimizado para
  escalabilidad masiva.

Similar a la web o asistentes de IA, este sistema distribuye
tareas globalmente vía Internet, optimizando recursos según
la naturaleza de cada tarea.
────────────────────────────────────────────────────────────
    """)


if __name__ == '__main__':
    main()
