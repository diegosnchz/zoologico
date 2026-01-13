"""
Tests unitarios para el sistema de vigilancia distribuida.
"""
import unittest
import numpy as np
from local_cluster import LocalCluster
from cloud_analyzer import CloudAnalyzer
from distributed_coordinator import DistributedCoordinator
from config import Config


class TestLocalCluster(unittest.TestCase):
    """Tests para el cluster local."""
    
    def setUp(self):
        self.cluster = LocalCluster(model_path='yolov8n.pt', alert_threshold=0.7)
    
    def test_initialization(self):
        """Test que el cluster se inicializa correctamente."""
        self.assertIsNotNone(self.cluster)
        self.assertEqual(self.cluster.alert_threshold, 0.7)
        self.assertEqual(self.cluster.model_path, 'yolov8n.pt')
    
    def test_process_camera_feed_simulation(self):
        """Test procesamiento de feed de cámara en modo simulado."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.cluster.process_camera_feed('camera_test', frame)
        
        self.assertIn('camera_id', result)
        self.assertIn('timestamp', result)
        self.assertIn('animals', result)
        self.assertEqual(result['camera_id'], 'camera_test')
    
    def test_get_stats(self):
        """Test obtención de estadísticas."""
        stats = self.cluster.get_stats()
        
        self.assertIn('active_cameras', stats)
        self.assertIn('total_alerts', stats)
        self.assertIn('cluster_type', stats)
        self.assertEqual(stats['cluster_type'], 'local')


class TestCloudAnalyzer(unittest.TestCase):
    """Tests para el analizador en la nube."""
    
    def setUp(self):
        self.analyzer = CloudAnalyzer(bucket_name='test-bucket', region='us-east-1')
    
    def test_initialization(self):
        """Test que el analizador se inicializa correctamente."""
        self.assertIsNotNone(self.analyzer)
        self.assertEqual(self.analyzer.bucket_name, 'test-bucket')
        self.assertEqual(self.analyzer.region, 'us-east-1')
    
    def test_upload_data(self):
        """Test subida de datos."""
        test_data = {
            'camera_id': 'camera_1',
            'timestamp': '2024-01-01T12:00:00',
            'animals': [],
            'has_escape': False
        }
        
        result = self.analyzer.upload_data(test_data, 'detection')
        self.assertTrue(result)
        self.assertEqual(len(self.analyzer.historical_data), 1)
    
    def test_analyze_historical_trends(self):
        """Test análisis de tendencias históricas."""
        # Agregar datos de prueba
        for i in range(10):
            data = {
                'camera_id': f'camera_{i % 3}',
                'timestamp': '2024-01-01T12:00:00',
                'animals': [{'class': 'elephant', 'confidence': 0.9}] if i % 2 == 0 else [],
                'has_escape': i % 2 == 0
            }
            self.analyzer.upload_data(data, 'detection')
        
        trends = self.analyzer.analyze_historical_trends(days=30)
        
        self.assertIn('total_detections', trends)
        self.assertIn('animals_by_type', trends)
        self.assertIn('processed_by', trends)
        self.assertEqual(trends['processed_by'], 'cloud_analyzer')
    
    def test_get_stats(self):
        """Test obtención de estadísticas."""
        stats = self.analyzer.get_stats()
        
        self.assertIn('total_historical_records', stats)
        self.assertIn('bucket_name', stats)
        self.assertIn('processor_type', stats)
        self.assertEqual(stats['processor_type'], 'cloud')


class TestDistributedCoordinator(unittest.TestCase):
    """Tests para el coordinador distribuido."""
    
    def setUp(self):
        self.config = Config()
        self.coordinator = DistributedCoordinator(self.config)
        self.coordinator.initialize_system()
    
    def test_initialization(self):
        """Test que el coordinador se inicializa correctamente."""
        self.assertIsNotNone(self.coordinator)
        self.assertIsNotNone(self.coordinator.local_cluster)
        self.assertIsNotNone(self.coordinator.cloud_analyzer)
    
    def test_delegate_to_local(self):
        """Test delegación de tarea urgente al cluster local."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        task_data = {'camera_id': 'camera_1', 'frame': frame}
        
        result = self.coordinator.delegate_task('real-time', task_data)
        
        self.assertIn('camera_id', result)
        self.assertEqual(self.coordinator.task_stats['local_tasks'], 1)
    
    def test_delegate_to_cloud(self):
        """Test delegación de tarea de análisis a la nube."""
        task_data = {'days': 7}
        
        result = self.coordinator.delegate_task('historical', task_data)
        
        self.assertIn('total_detections', result)
        self.assertEqual(self.coordinator.task_stats['cloud_tasks'], 1)
    
    def test_process_realtime_feed(self):
        """Test procesamiento de feed en tiempo real."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.coordinator.process_realtime_feed('camera_test', frame)
        
        self.assertIn('camera_id', result)
        self.assertEqual(result['camera_id'], 'camera_test')
    
    def test_analyze_historical_data(self):
        """Test análisis de datos históricos."""
        result = self.coordinator.analyze_historical_data(days=30)
        
        self.assertIn('total_detections', result)
        self.assertIn('period_days', result)
    
    def test_get_system_status(self):
        """Test obtención de estado del sistema."""
        status = self.coordinator.get_system_status()
        
        self.assertIn('coordinator', status)
        self.assertIn('local_cluster', status)
        self.assertIn('cloud_analyzer', status)
        
        self.assertIn('tasks_delegated', status['coordinator'])


class TestTaskDelegation(unittest.TestCase):
    """Tests para verificar la delegación correcta de tareas."""
    
    def setUp(self):
        self.coordinator = DistributedCoordinator()
        self.coordinator.initialize_system()
    
    def test_urgent_tasks_to_local(self):
        """Test que tareas urgentes se delegan al cluster local."""
        urgent_tasks = ['real-time', 'urgent', 'escape-detection']
        
        for task_type in urgent_tasks:
            initial_local = self.coordinator.task_stats['local_tasks']
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            self.coordinator.delegate_task(task_type, {'frame': frame})
            
            self.assertEqual(
                self.coordinator.task_stats['local_tasks'], 
                initial_local + 1,
                f"Tarea {task_type} no fue delegada al cluster local"
            )
    
    def test_historical_tasks_to_cloud(self):
        """Test que tareas de análisis masivo se delegan a la nube."""
        cloud_tasks = ['historical', 'trends', 'analytics']
        
        for task_type in cloud_tasks:
            initial_cloud = self.coordinator.task_stats['cloud_tasks']
            self.coordinator.delegate_task(task_type, {'days': 7})
            
            self.assertEqual(
                self.coordinator.task_stats['cloud_tasks'],
                initial_cloud + 1,
                f"Tarea {task_type} no fue delegada a la nube"
            )


if __name__ == '__main__':
    unittest.main()
