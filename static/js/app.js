// API endpoints
const API_BASE = '';

// Estado global
let isInitialized = false;
let isMonitoring = false;

// Inicializar página
document.addEventListener('DOMContentLoaded', function() {
    console.log('🦁 Sistema de Vigilancia Distribuida - Interfaz Web Cargada');
    loadCameras();
    refreshStatus();
    
    // Actualizar estado cada 5 segundos
    setInterval(refreshStatus, 5000);
    setInterval(loadAlerts, 10000);
});

// Inicializar sistema
async function initializeSystem() {
    try {
        showLoading('Inicializando sistema...');
        const response = await fetch(`${API_BASE}/api/system/initialize`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            isInitialized = true;
            showSuccess('✓ ' + data.message);
            refreshStatus();
        } else {
            showError('Error: ' + data.error);
        }
    } catch (error) {
        showError('Error al inicializar: ' + error.message);
    }
}

// Iniciar monitoreo
async function startMonitoring() {
    try {
        showLoading('Iniciando monitoreo...');
        const response = await fetch(`${API_BASE}/api/monitoring/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            isMonitoring = true;
            document.getElementById('monitoringStatus').textContent = '▶️ Activo';
            document.getElementById('monitoringStatus').style.color = '#28a745';
            showSuccess('✓ ' + data.message);
            
            // Actualizar alertas más frecuentemente cuando está monitoreando
            setInterval(loadAlerts, 3000);
        } else {
            showError('Error: ' + data.error);
        }
    } catch (error) {
        showError('Error al iniciar monitoreo: ' + error.message);
    }
}

// Detener monitoreo
async function stopMonitoring() {
    try {
        const response = await fetch(`${API_BASE}/api/monitoring/stop`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            isMonitoring = false;
            document.getElementById('monitoringStatus').textContent = '⏸️ Detenido';
            document.getElementById('monitoringStatus').style.color = '#666';
            showSuccess('✓ ' + data.message);
        }
    } catch (error) {
        showError('Error al detener monitoreo: ' + error.message);
    }
}

// Actualizar estado del sistema
async function refreshStatus() {
    try {
        // Obtener estado del sistema
        const statusResponse = await fetch(`${API_BASE}/api/system/status`);
        const status = await statusResponse.json();
        
        if (status.initialized) {
            isInitialized = true;
            document.getElementById('systemStatus').textContent = '✓ Operativo';
            document.getElementById('systemStatus').style.color = '#28a745';
            
            // Actualizar componentes
            if (status.local_cluster) {
                document.getElementById('localStatus').textContent = 
                    status.local_cluster.model_loaded ? '✓ YOLO Cargado' : '⚠️ Modo Simulado';
            }
            
            if (status.cloud_analyzer) {
                document.getElementById('cloudStatusText').textContent = 
                    status.cloud_analyzer.cloud_connected ? '✓ Conectado' : '⚠️ Modo Local';
            }
        } else {
            document.getElementById('systemStatus').textContent = '⚠️ No Inicializado';
            document.getElementById('systemStatus').style.color = '#ffc107';
        }
        
        // Obtener estadísticas
        const statsResponse = await fetch(`${API_BASE}/api/stats/summary`);
        const stats = await statsResponse.json();
        
        document.getElementById('totalTasks').textContent = stats.total_tasks || 0;
        document.getElementById('localTasks').textContent = stats.local_tasks || 0;
        document.getElementById('cloudTasks').textContent = stats.cloud_tasks || 0;
        document.getElementById('totalAlerts').textContent = stats.total_alerts || 0;
        
    } catch (error) {
        console.error('Error al actualizar estado:', error);
    }
}

// Cargar lista de cámaras
async function loadCameras() {
    try {
        const response = await fetch(`${API_BASE}/api/cameras/list`);
        const cameras = await response.json();
        
        const cameraList = document.getElementById('cameraList');
        cameraList.innerHTML = '';
        
        cameras.forEach(camera => {
            const cameraItem = document.createElement('div');
            cameraItem.className = 'camera-item';
            cameraItem.innerHTML = `
                <div>
                    <div class="camera-name">📹 ${camera.name}</div>
                    <small style="color: #666;">${camera.id}</small>
                </div>
                <div class="camera-status">${camera.status === 'active' ? 'Activa' : 'Inactiva'}</div>
            `;
            cameraList.appendChild(cameraItem);
        });
    } catch (error) {
        console.error('Error al cargar cámaras:', error);
    }
}

// Cargar alertas recientes
async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/api/alerts/recent`);
        const alerts = await response.json();
        
        const alertsList = document.getElementById('alertsList');
        
        if (alerts.length === 0) {
            alertsList.innerHTML = '<p class="no-data">No hay alertas</p>';
            return;
        }
        
        alertsList.innerHTML = '';
        
        alerts.slice(0, 10).forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = alert.priority === 'URGENT' ? 'alert-item urgent' : 'alert-item';
            
            const timestamp = new Date(alert.timestamp).toLocaleString('es-ES');
            const animals = alert.animals.map(a => a.class).join(', ');
            
            alertItem.innerHTML = `
                <div class="alert-time">⏰ ${timestamp}</div>
                <div class="alert-message">
                    ⚠️ ${alert.type}: ${alert.animals.length} animal(es) detectado(s)
                    <br><small>Cámara: ${alert.camera_id} | Animales: ${animals}</small>
                </div>
            `;
            alertsList.appendChild(alertItem);
        });
    } catch (error) {
        console.error('Error al cargar alertas:', error);
    }
}

// Ejecutar análisis histórico
async function runHistoricalAnalysis() {
    try {
        showLoading('Ejecutando análisis histórico...');
        
        const days = document.getElementById('analysisDays').value;
        
        const response = await fetch(`${API_BASE}/api/analysis/historical`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ days: parseInt(days) })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultsDiv = document.getElementById('analysisResults');
            
            if (data.analysis.report) {
                resultsDiv.innerHTML = `<pre>${data.analysis.report}</pre>`;
            } else {
                const analysis = data.analysis;
                resultsDiv.innerHTML = `
                    <pre>
ANÁLISIS HISTÓRICO (${analysis.period_days} días)
═══════════════════════════════════════════════

Total de detecciones: ${analysis.total_detections}
Fecha de análisis: ${new Date(analysis.analysis_timestamp).toLocaleString('es-ES')}

Animales detectados:
${Object.entries(analysis.animals_by_type || {}).map(([animal, count]) => 
    `  • ${animal}: ${count}`).join('\n') || '  (No hay datos)'}

Zonas de alto riesgo:
${(analysis.risk_zones || []).map(zone => 
    `  • ${zone.camera_id}: Riesgo ${(zone.risk_score * 100).toFixed(1)}%`).join('\n') || '  (No se identificaron zonas de riesgo)'}

Procesado por: ${analysis.processed_by}
                    </pre>
                `;
            }
            
            showSuccess('✓ Análisis completado');
        } else {
            showError('Error: ' + data.error);
        }
    } catch (error) {
        showError('Error al ejecutar análisis: ' + error.message);
    }
}

// Funciones de notificación
function showLoading(message) {
    // Implementación simple - podrías usar una librería de notificaciones
    console.log('⏳', message);
}

function showSuccess(message) {
    console.log('✓', message);
    alert(message);
}

function showError(message) {
    console.error('✗', message);
    alert(message);
}
