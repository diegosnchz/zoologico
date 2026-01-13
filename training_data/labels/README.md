# 🏷️ Archivos de Etiquetas YOLO

Este directorio contiene los archivos de etiquetas para las imágenes de entrenamiento.

## Formato de Etiquetas

Cada imagen debe tener un archivo `.txt` correspondiente con el mismo nombre.

**Ejemplo:**
- Imagen: `images/leon_001.jpg`
- Etiqueta: `labels/leon_001.txt`

## Formato del Archivo

Cada línea representa un objeto detectado:

```
<class_id> <x_center> <y_center> <width> <height>
```

Todos los valores de coordenadas están normalizados (0-1).

**Ejemplo de contenido:**

```
0 0.5 0.5 0.3 0.4
1 0.7 0.3 0.2 0.3
```

## Clases Disponibles

- `0`: animal_escape (🚨 FUGA - animal fuera de su recinto)
- `1`: elephant (elefante)
- `2`: giraffe (jirafa)
- `3`: lion (león)
- `4`: tiger (tigre)
- `5`: bear (oso)
- `6`: zebra (cebra)
- `7`: monkey (mono)

## Herramientas de Etiquetado

### LabelImg (Recomendado)

```bash
pip install labelImg
labelImg ../images ../labels
```

1. Abre LabelImg
2. Cambia a modo YOLO (View → YOLO)
3. Dibuja cajas alrededor de los animales
4. Selecciona la clase correcta
5. Guarda (Ctrl+S)

### Creación Manual

También puedes usar nuestro script:

```bash
cd ../..
python prepare_training_data.py
# Opción 3: Crear archivo de etiqueta
```

## Validación

Valida tus etiquetas antes de entrenar:

```bash
cd ../..
python prepare_training_data.py
# Opción 4: Validar etiquetas
```

## 📊 Estado Actual

```
Archivos de etiquetas: [ejecuta 'ls *.txt | wc -l' para contar]
```
