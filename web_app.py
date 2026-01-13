"""
Aplicación web para el sistema de vigilancia distribuida del zoológico.
Interfaz web para monitorear cámaras, alertas y análisis histórico.
"""
from flask import Flask, render_template, jsonify, request
from distributed_coordinator import DistributedCoordinator
from config import Config
import numpy as np
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Inicializar coordinador distribuido
config = Config()
coordinator = DistributedCoordinator(config)

# Variable global para controlar el estado
system_initialized = False
monitoring_active = False


def initialize_system():
    """Inicializa el sistema de vigilancia."""
    global system_initialized
    if not system_initialized:
        coordinator.initialize_system()
        system_initialized = True
        print("✓ Sistema de vigilancia inicializado")


@app.route('/')
def index():
    """Página principal del sistema de vigilancia."""
    return render_template('index.html')


@app.route('/api/system/status')
def get_system_status():
    """Obtiene el estado actual del sistema."""
    if not system_initialized:
        return jsonify({
            'initialized': False,
            'message': 'Sistema no inicializado'
        })
    
    status = coordinator.get_system_status()
    status['initialized'] = True
    status['monitoring_active'] = monitoring_active
    return jsonify(status)


@app.route('/api/system/initialize', methods=['POST'])
def initialize():
    """Inicializa el sistema de vigilancia."""
    try:
        initialize_system()
        return jsonify({
            'success': True,
            'message': 'Sistema inicializado correctamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/cameras/list')
def list_cameras():
    """Lista las cámaras disponibles."""
    cameras = [
        {'id': 'camera_1', 'name': 'Cámara Zona Cocodrilos', 'status': 'active'},
        {'id': 'camera_2', 'name': 'Cámara Área Primates', 'status': 'active'},
        {'id': 'camera_3', 'name': 'Cámara Zona Tigres', 'status': 'active'},
        {'id': 'camera_4', 'name': 'Cámara Área Osos', 'status': 'active'}
    ]
    return jsonify(cameras)


@app.route('/api/cameras/<camera_id>/process', methods=['POST'])
def process_camera_feed(camera_id):
    """Procesa un frame de una cámara específica."""
    if not system_initialized:
        return jsonify({
            'success': False,
            'error': 'Sistema no inicializado'
        }), 400
    
    try:
        # Simular frame de cámara
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = coordinator.process_realtime_feed(camera_id, frame)
        
        return jsonify({
            'success': True,
            'camera_id': camera_id,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/alerts/recent')
def get_recent_alerts():
    """Obtiene las alertas más recientes."""
    if not system_initialized or not coordinator.local_cluster:
        return jsonify([])
    
    alerts = coordinator.local_cluster.get_recent_alerts(limit=20)
    return jsonify(alerts)


@app.route('/api/analysis/historical', methods=['POST'])
def analyze_historical():
    """Ejecuta análisis histórico de datos."""
    if not system_initialized:
        return jsonify({
            'success': False,
            'error': 'Sistema no inicializado'
        }), 400
    
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        
        # Agregar algunos datos de muestra si no hay datos
        if coordinator.cloud_analyzer and len(coordinator.cloud_analyzer.historical_data) < 10:
            for i in range(50):
                sample_data = {
                    'camera_id': f'camera_{(i % 4) + 1}',
                    'timestamp': datetime.now().isoformat(),
                    'animals': [{'class': 'elephant', 'confidence': 0.85}] if i % 5 == 0 else [],
                    'has_escape': i % 5 == 0
                }
                coordinator.cloud_analyzer.upload_data(sample_data, 'detection')
        
        result = coordinator.analyze_historical_data(days=days)
        
        # Generar reporte
        if coordinator.cloud_analyzer and 'report' not in result:
            report = coordinator.cloud_analyzer.generate_report(result)
            result['report'] = report
        
        return jsonify({
            'success': True,
            'analysis': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Inicia el monitoreo continuo de cámaras."""
    global monitoring_active
    
    if not system_initialized:
        return jsonify({
            'success': False,
            'error': 'Sistema no inicializado'
        }), 400
    
    monitoring_active = True
    
    # Iniciar thread de monitoreo
    def monitor():
        cameras = ['camera_1', 'camera_2', 'camera_3', 'camera_4']
        while monitoring_active:
            for camera_id in cameras:
                if not monitoring_active:
                    break
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                coordinator.process_realtime_feed(camera_id, frame)
            time.sleep(5)  # Procesar cada 5 segundos
    
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Monitoreo iniciado'
    })


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Detiene el monitoreo continuo."""
    global monitoring_active
    monitoring_active = False
    
    return jsonify({
        'success': True,
        'message': 'Monitoreo detenido'
    })


@app.route('/api/stats/summary')
def get_stats_summary():
    """Obtiene resumen de estadísticas del sistema."""
    if not system_initialized:
        return jsonify({})
    
    status = coordinator.get_system_status()
    
    summary = {
        'total_tasks': status['coordinator']['tasks_delegated']['total_tasks'],
        'local_tasks': status['coordinator']['tasks_delegated']['local_tasks'],
        'cloud_tasks': status['coordinator']['tasks_delegated']['cloud_tasks'],
        'total_alerts': status.get('local_cluster', {}).get('total_alerts', 0),
        'active_cameras': status.get('local_cluster', {}).get('active_cameras', 0),
        'historical_records': status.get('cloud_analyzer', {}).get('total_historical_records', 0)
    }
    
    return jsonify(summary)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🦁 SISTEMA DE VIGILANCIA DISTRIBUIDA - INTERFAZ WEB")
    print("="*70)
    print("\n🌐 Iniciando servidor web...")
    print("📍 URL: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    # Inicializar sistema al arrancar
    initialize_system()
    
    # Iniciar servidor Flask (sin debug mode en producción)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
