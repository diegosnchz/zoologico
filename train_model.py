"""
Script de entrenamiento para el modelo YOLO de detección de fugas de animales.
Pre-entrena o afina (fine-tune) el modelo YOLOv8 con imágenes personalizadas.
"""
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YOLOTrainer:
    """Clase para entrenar modelos YOLO para detección de fugas."""
    
    def __init__(self, dataset_config='training_data/dataset.yaml'):
        self.dataset_config = dataset_config
        self.models_dir = Path('training_data/models')
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
    def train_model(self, 
                    base_model='yolov8n.pt',
                    epochs=50,
                    image_size=640,
                    batch_size=16,
                    name='animal_escape_detector'):
        """
        Entrena un modelo YOLO con las imágenes preparadas.
        
        Args:
            base_model: Modelo base de YOLO (yolov8n.pt, yolov8s.pt, yolov8m.pt, etc.)
            epochs: Número de épocas de entrenamiento
            image_size: Tamaño de las imágenes de entrada
            batch_size: Tamaño del batch
            name: Nombre del experimento de entrenamiento
        """
        try:
            from ultralytics import YOLO
            
            logger.info("="*70)
            logger.info("🚀 INICIANDO ENTRENAMIENTO DE YOLO")
            logger.info("="*70)
            
            # Validar que existan imágenes y etiquetas
            images_dir = Path('training_data/images')
            labels_dir = Path('training_data/labels')
            
            images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
            labels = list(labels_dir.glob('*.txt'))
            
            if len(images) == 0:
                logger.error("❌ No se encontraron imágenes en training_data/images/")
                logger.error("   Por favor, coloca las imágenes en ese directorio")
                return None
            
            if len(labels) == 0:
                logger.error("❌ No se encontraron etiquetas en training_data/labels/")
                logger.error("   Por favor, crea archivos de etiquetas usando prepare_training_data.py")
                return None
            
            logger.info(f"📸 Imágenes encontradas: {len(images)}")
            logger.info(f"🏷️  Etiquetas encontradas: {len(labels)}")
            
            # Cargar modelo base
            logger.info(f"\n📦 Cargando modelo base: {base_model}")
            model = YOLO(base_model)
            
            # Configurar parámetros de entrenamiento
            logger.info(f"\n⚙️  Configuración de entrenamiento:")
            logger.info(f"   • Épocas: {epochs}")
            logger.info(f"   • Tamaño de imagen: {image_size}")
            logger.info(f"   • Batch size: {batch_size}")
            logger.info(f"   • Dataset config: {self.dataset_config}")
            
            # Entrenar modelo
            logger.info(f"\n🏋️  Iniciando entrenamiento...")
            results = model.train(
                data=self.dataset_config,
                epochs=epochs,
                imgsz=image_size,
                batch=batch_size,
                name=name,
                project='training_data/models',
                patience=10,  # Early stopping
                save=True,
                plots=True
            )
            
            logger.info("\n✅ Entrenamiento completado exitosamente!")
            
            # Guardar modelo final
            best_model_path = Path(f'training_data/models/{name}/weights/best.pt')
            if best_model_path.exists():
                logger.info(f"\n🎯 Mejor modelo guardado en: {best_model_path}")
                
                # Copiar a ubicación estándar
                final_model_path = self.models_dir / 'animal_escape_detector.pt'
                import shutil
                shutil.copy2(best_model_path, final_model_path)
                logger.info(f"📋 Modelo copiado a: {final_model_path}")
            
            return results
            
        except ImportError:
            logger.error("❌ Error: La librería 'ultralytics' no está instalada")
            logger.error("   Instala con: pip install ultralytics")
            return None
        except Exception as e:
            logger.error(f"❌ Error durante el entrenamiento: {e}")
            return None
    
    def evaluate_model(self, model_path='training_data/models/animal_escape_detector.pt'):
        """
        Evalúa un modelo entrenado con el dataset de validación.
        
        Args:
            model_path: Ruta al modelo entrenado
        """
        try:
            from ultralytics import YOLO
            
            logger.info("="*70)
            logger.info("📊 EVALUANDO MODELO")
            logger.info("="*70)
            
            model = YOLO(model_path)
            
            # Validar modelo
            results = model.val(data=self.dataset_config)
            
            logger.info("\n✅ Evaluación completada")
            logger.info(f"📈 Métricas:")
            logger.info(f"   • mAP50: {results.box.map50:.4f}")
            logger.info(f"   • mAP50-95: {results.box.map:.4f}")
            
            return results
            
        except ImportError:
            logger.error("❌ Error: La librería 'ultralytics' no está instalada")
            return None
        except Exception as e:
            logger.error(f"❌ Error durante la evaluación: {e}")
            return None
    
    def test_model(self, 
                   model_path='training_data/models/animal_escape_detector.pt',
                   image_path=None):
        """
        Prueba el modelo con una imagen.
        
        Args:
            model_path: Ruta al modelo entrenado
            image_path: Ruta a la imagen de prueba
        """
        try:
            from ultralytics import YOLO
            
            if not image_path:
                # Usar primera imagen del dataset
                images_dir = Path('training_data/images')
                images = list(images_dir.glob('*.jpg')) + list(images_dir.glob('*.png'))
                if images:
                    image_path = str(images[0])
                else:
                    logger.error("❌ No hay imágenes para probar")
                    return None
            
            logger.info("="*70)
            logger.info("🧪 PROBANDO MODELO")
            logger.info("="*70)
            logger.info(f"📸 Imagen: {image_path}")
            
            model = YOLO(model_path)
            results = model(image_path)
            
            # Mostrar resultados
            for result in results:
                boxes = result.boxes
                logger.info(f"\n✅ Detecciones: {len(boxes)}")
                
                for i, box in enumerate(boxes):
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    class_names = ['escape', 'elephant', 'giraffe', 'lion', 
                                  'tiger', 'bear', 'zebra', 'monkey']
                    class_name = class_names[class_id] if class_id < len(class_names) else 'unknown'
                    
                    logger.info(f"  {i+1}. {class_name} - Confianza: {confidence:.2f}")
            
            return results
            
        except ImportError:
            logger.error("❌ Error: La librería 'ultralytics' no está instalada")
            return None
        except Exception as e:
            logger.error(f"❌ Error durante la prueba: {e}")
            return None


def main():
    """Función principal para entrenamiento."""
    print("="*70)
    print("🦁 ENTRENAMIENTO DE MODELO YOLO - DETECCIÓN DE FUGAS")
    print("="*70)
    
    trainer = YOLOTrainer()
    
    while True:
        print("\n" + "="*70)
        print("MENÚ:")
        print("  1. Entrenar modelo nuevo (pre-entrenamiento)")
        print("  2. Entrenar con configuración rápida (10 épocas)")
        print("  3. Entrenar con configuración completa (50 épocas)")
        print("  4. Evaluar modelo entrenado")
        print("  5. Probar modelo con imagen")
        print("  6. Salir")
        print("="*70)
        
        choice = input("\nSelecciona una opción (1-6): ").strip()
        
        if choice == '1':
            epochs = int(input("Número de épocas (recomendado: 50): ") or "50")
            batch_size = int(input("Batch size (recomendado: 16): ") or "16")
            trainer.train_model(epochs=epochs, batch_size=batch_size)
        
        elif choice == '2':
            print("\n🚀 Entrenamiento rápido (10 épocas)...")
            trainer.train_model(epochs=10, batch_size=8)
        
        elif choice == '3':
            print("\n🚀 Entrenamiento completo (50 épocas)...")
            trainer.train_model(epochs=50, batch_size=16)
        
        elif choice == '4':
            trainer.evaluate_model()
        
        elif choice == '5':
            img_path = input("Ruta de la imagen (Enter para usar primera del dataset): ").strip()
            trainer.test_model(image_path=img_path if img_path else None)
        
        elif choice == '6':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == '__main__':
    main()
