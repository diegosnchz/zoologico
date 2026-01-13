# 🎯 Guía de Entrenamiento del Modelo YOLO

Esta guía explica cómo preparar y entrenar el modelo YOLO para detectar fugas de animales en el zoológico.

## 📋 Requisitos Previos

```bash
pip install ultralytics opencv-python
```

## 📁 Estructura de Directorios

```
training_data/
├── images/          # Colocar aquí las imágenes para entrenamiento
├── labels/          # Archivos de etiquetas YOLO (.txt)
├── models/          # Modelos entrenados
└── dataset.yaml     # Configuración del dataset
```

## 🚀 Proceso de Entrenamiento

### Paso 1: Preparar las Imágenes

1. **Colocar imágenes en el directorio:**
   ```bash
   # Copiar tus 6 imágenes al directorio de entrenamiento
   cp /ruta/a/tus/imagenes/*.jpg training_data/images/
   ```

2. **Ejecutar la herramienta de preparación:**
   ```bash
   python prepare_training_data.py
   ```

   Opciones disponibles:
   - **Importar imágenes**: Copia imágenes desde cualquier directorio
   - **Listar imágenes**: Ve qué imágenes están disponibles
   - **Crear archivos de etiqueta**: Genera plantillas para etiquetar
   - **Validar etiquetas**: Verifica que las etiquetas sean correctas
   - **Ver estadísticas**: Muestra resumen del dataset

### Paso 2: Etiquetar las Imágenes

Las etiquetas siguen el formato YOLO:

```
<class_id> <x_center> <y_center> <width> <height>
```

Donde:
- `class_id`: ID de la clase (0-7)
- `x_center, y_center`: Centro del objeto (normalizado 0-1)
- `width, height`: Ancho y alto del objeto (normalizado 0-1)

**Clases disponibles:**
- `0`: animal_escape (animal fuera de su recinto - FUGA)
- `1`: elephant
- `2`: giraffe
- `3`: lion
- `4`: tiger
- `5`: bear
- `6`: zebra
- `7`: monkey

**Ejemplo de archivo de etiqueta** (`training_data/labels/imagen1.txt`):
```
0 0.5 0.5 0.3 0.4
1 0.7 0.3 0.2 0.3
```

### Herramientas Recomendadas para Etiquetar

1. **LabelImg** (Recomendado)
   ```bash
   pip install labelImg
   labelImg training_data/images training_data/labels
   ```
   - Interfaz gráfica fácil de usar
   - Genera archivos YOLO automáticamente

2. **Roboflow** (Online)
   - https://roboflow.com
   - Interfaz web profesional
   - Exporta en formato YOLO

3. **CVAT** (Online/Local)
   - https://cvat.org
   - Herramienta avanzada de anotación

### Paso 3: Entrenar el Modelo

```bash
python train_model.py
```

Opciones de entrenamiento:

1. **Entrenamiento Rápido (10 épocas)** - Para pruebas
   - Tiempo: ~5-10 minutos
   - Ideal para: Validar que todo funciona

2. **Entrenamiento Completo (50 épocas)** - Recomendado
   - Tiempo: ~30-60 minutos
   - Ideal para: Modelo final de producción

3. **Entrenamiento Personalizado**
   - Configura épocas, batch size, etc.

**Parámetros recomendados para 6 imágenes:**
```
Épocas: 30-50
Batch size: 4-8 (menor batch por pocas imágenes)
Image size: 640
```

### Paso 4: Evaluar el Modelo

Después del entrenamiento, evalúa el modelo:

```bash
python train_model.py
# Seleccionar opción 4: Evaluar modelo
```

Métricas importantes:
- **mAP50**: Precisión media con IoU >= 0.5
- **mAP50-95**: Precisión media con IoU de 0.5 a 0.95

### Paso 5: Probar el Modelo

Prueba el modelo con una imagen:

```bash
python train_model.py
# Seleccionar opción 5: Probar modelo
```

## 🎓 Mejores Prácticas

### Para 6 Imágenes

Con solo 6 imágenes, considera:

1. **Data Augmentation**: YOLO automáticamente aplica:
   - Rotaciones
   - Cambios de escala
   - Ajustes de brillo/contraste
   - Recortes aleatorios

2. **Transfer Learning**: Usa un modelo pre-entrenado:
   - `yolov8n.pt` (nano) - Rápido, menos preciso
   - `yolov8s.pt` (small) - Balance ideal
   - `yolov8m.pt` (medium) - Más preciso, más lento

3. **Más datos**: Idealmente necesitas:
   - **Mínimo**: 10-20 imágenes por clase
   - **Recomendado**: 50-100 imágenes por clase
   - **Óptimo**: 500+ imágenes por clase

4. **Estrategias para pocas imágenes**:
   - Tomar más fotos desde diferentes ángulos
   - Usar diferentes condiciones de iluminación
   - Capturar animales en diferentes posiciones
   - Aumentar artificialmente con herramientas

## 📊 Monitoreo del Entrenamiento

Durante el entrenamiento, YOLO genera:

```
training_data/models/animal_escape_detector/
├── weights/
│   ├── best.pt      # Mejor modelo (úsalo en producción)
│   └── last.pt      # Último checkpoint
├── results.png      # Gráficas de métricas
├── confusion_matrix.png
├── F1_curve.png
└── PR_curve.png
```

## 🔧 Integración con el Sistema

Una vez entrenado, actualiza la configuración:

```python
# En config.py
YOLO_MODEL_PATH = 'training_data/models/animal_escape_detector.pt'
```

O mediante variable de entorno:

```bash
export YOLO_MODEL_PATH=training_data/models/animal_escape_detector.pt
python web_app.py
```

## 🐛 Troubleshooting

### Error: "No images found"
```bash
# Verifica que las imágenes estén en el directorio correcto
ls training_data/images/
```

### Error: "No labels found"
```bash
# Crea archivos de etiquetas para cada imagen
python prepare_training_data.py
# Opción 3: Crear archivo de etiqueta
```

### Error: "CUDA out of memory"
```bash
# Reduce el batch size
# En train_model.py, usa batch_size=4 o batch_size=2
```

### Modelo no detecta bien
- **Más datos**: Necesitas más imágenes etiquetadas
- **Más épocas**: Incrementa el número de épocas
- **Mejor modelo base**: Usa yolov8m.pt en lugar de yolov8n.pt
- **Revisa etiquetas**: Verifica que las etiquetas sean correctas

## 📚 Recursos Adicionales

- [Documentación YOLO](https://docs.ultralytics.com/)
- [Tutorial de Etiquetado](https://github.com/tzutalin/labelImg)
- [Data Augmentation](https://roboflow.com/augment)
- [Mejores Prácticas YOLO](https://docs.ultralytics.com/guides/)

## 💡 Consejos Finales

1. **Empieza simple**: Prueba con pocas épocas primero
2. **Valida etiquetas**: Usa `prepare_training_data.py` opción 4
3. **Monitorea métricas**: Revisa las gráficas generadas
4. **Itera**: Mejora el dataset basándote en los errores
5. **Documenta**: Anota qué configuración funciona mejor

¡Buena suerte con el entrenamiento! 🚀
