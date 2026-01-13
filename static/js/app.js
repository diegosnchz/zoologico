// API endpoints
const API_BASE = '';

// Estado global
let isInitialized = false;
let isMonitoring = false;

// Inicializar página
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema de Vigilancia Distribuida - Interfaz Web Cargada');
    loadCameras();
    refreshStatus();
    
    // Actualizar estado cada 5 segundos
    setInterval(refreshStatus, 5000);
    setInterval(loadAlerts, 10000);
    setInterval(loadCameras, 3000); // Refrescar cámaras cada 3 segundos
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
            showSuccess('Monitoreo iniciado: ' + data.message);
            loadCameras(); // Refrescar vista de cámaras
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
            showSuccess('Monitoreo detenido: ' + data.message);
            loadCameras(); // Refrescar vista de cámaras
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
        
        const camerasGrid = document.getElementById('camerasGrid');
        camerasGrid.innerHTML = '';
        
        // Mapeo de imágenes para las 4 cámaras
        const cameraImages = {
            'camera_1': 'camera1.png',
            'camera_2': 'camera2.png',
            'camera_3': 'camera3.png',
            'camera_4': 'camera4.png'
        };
        
        // Configuración realista de detecciones por cámara
        const cameraDetections = {
            'camera_1': { animal: 'COCODRILO', minConf: 84, maxConf: 95, probability: 0.68 },
            'camera_2': { animal: 'MONO', minConf: 79, maxConf: 92, probability: 0.72 },
            'camera_3': { animal: 'TIGRE', minConf: 86, maxConf: 97, probability: 0.70 },
            'camera_4': { animal: 'OSO', minConf: 81, maxConf: 94, probability: 0.65 }
        };
        
        cameras.forEach((camera, index) => {
            const detection = cameraDetections[camera.id];
            const hasDetection = isMonitoring && detection && Math.random() < detection.probability;
            
            // Generar confianza realista dentro del rango
            let confidence = 0;
            if (hasDetection) {
                confidence = Math.floor(Math.random() * (detection.maxConf - detection.minConf + 1)) + detection.minConf;
            }
            
            const cardClass = hasDetection ? 'camera-card alert' : 'camera-card';
            const statusClass = isMonitoring ? 'recording' : '';
            const statusText = isMonitoring ? 'REC' : 'ACTIVA';
            const imageFile = cameraImages[camera.id] || 'camera1.png';
            
            const cameraCard = document.createElement('div');
            cameraCard.className = cardClass;
            cameraCard.innerHTML = `
                <div class="camera-image-container">
                    <img src="/static/${imageFile}" alt="${camera.name}" class="camera-image">
                    <div class="camera-overlay"></div>
                    <div class="camera-status-badge ${statusClass}">${statusText}</div>
                    ${hasDetection ? `
                        <div class="camera-detection-badge">
                            ${detection.animal} ${confidence}%
                        </div>
                    ` : ''}
                </div>
                <div class="camera-info">
                    <div class="camera-name">${camera.name}</div>
                    <div class="camera-details">
                        <div class="camera-meta">
                            <span>CAM ${camera.id}</span>
                            <span>${new Date().toLocaleTimeString('es-ES')}</span>
                        </div>
                    </div>
                </div>
            `;
            camerasGrid.appendChild(cameraCard);
        });
        
        if (cameras.length === 0) {
            camerasGrid.innerHTML = '<p class="no-data">No hay cámaras disponibles</p>';
        }
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
                <div class="alert-time">${timestamp}</div>
                <div class="alert-message">
                    ALERTA: ${alert.type}: ${alert.animals.length} animal(es) detectado(s)
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
    console.log('Loading:', message);
}

function showSuccess(message) {
    console.log('Success:', message);
    alert(message);
}

function showError(message) {
    console.error('Error:', message);
    alert(message);
}
