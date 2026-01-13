# 📸 Coloca tus imágenes aquí

Para entrenar el modelo YOLO, coloca tus imágenes en este directorio.

## Instrucciones Rápidas

1. **Copia tus 6 imágenes aquí:**
   ```bash
   cp /ruta/a/tus/imagenes/*.jpg .
   ```

2. **Formatos soportados:**
   - JPG/JPEG
   - PNG
   - BMP

3. **Nombrado de archivos:**
   - Usa nombres descriptivos
   - Ejemplo: `leon_escape_001.jpg`, `elefante_zona_002.png`

4. **Siguiente paso:**
   - Ve al directorio raíz
   - Ejecuta: `python prepare_training_data.py`
   - Sigue las instrucciones para etiquetar

## 📊 Estado Actual

```
Imágenes en este directorio: [ejecuta 'ls' para ver]
```

## 🔗 Enlaces Útiles

- [Guía Completa de Entrenamiento](./TRAINING_GUIDE.md)
- [Herramienta de Preparación](../prepare_training_data.py)
- [Script de Entrenamiento](../train_model.py)
