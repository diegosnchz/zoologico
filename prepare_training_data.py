"""
Script para preparar imágenes para entrenamiento de YOLO.
Ayuda a organizar imágenes y crear archivos de etiquetas.
"""
import os
import shutil
from pathlib import Path


class ImagePreparationTool:
    """Herramienta para preparar imágenes para entrenamiento YOLO."""
    
    def __init__(self, base_dir='training_data'):
        self.base_dir = Path(base_dir)
        self.images_dir = self.base_dir / 'images'
        self.labels_dir = self.base_dir / 'labels'
        self.models_dir = self.base_dir / 'models'
        
        # Crear directorios si no existen
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.labels_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def import_images(self, source_dir):
        """
        Importa imágenes desde un directorio fuente.
        
        Args:
            source_dir: Directorio con las imágenes a importar
        """
        source_path = Path(source_dir)
        
        if not source_path.exists():
            print(f"❌ Error: El directorio {source_dir} no existe")
            return
        
        # Extensiones de imagen soportadas
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        imported_count = 0
        
        for img_file in source_path.iterdir():
            if img_file.suffix.lower() in image_extensions:
                dest = self.images_dir / img_file.name
                shutil.copy2(img_file, dest)
                print(f"✓ Importada: {img_file.name}")
                imported_count += 1
        
        print(f"\n📊 Total de imágenes importadas: {imported_count}")
        return imported_count
    
    def list_images(self):
        """Lista todas las imágenes disponibles para etiquetar."""
        images = list(self.images_dir.glob('*.[jp][pn][g]')) + \
                 list(self.images_dir.glob('*.jpeg')) + \
                 list(self.images_dir.glob('*.bmp'))
        
        if not images:
            print("⚠️  No hay imágenes para etiquetar")
            return []
        
        print(f"\n📸 Imágenes disponibles ({len(images)}):")
        for i, img in enumerate(images, 1):
            label_file = self.labels_dir / f"{img.stem}.txt"
            status = "✓ Etiquetada" if label_file.exists() else "⚠️  Sin etiquetar"
            print(f"  {i}. {img.name} - {status}")
        
        return images
    
    def create_label_template(self, image_name):
        """
        Crea un archivo de etiqueta de plantilla para una imagen.
        
        Args:
            image_name: Nombre del archivo de imagen
        """
        img_path = self.images_dir / image_name
        if not img_path.exists():
            print(f"❌ Error: La imagen {image_name} no existe")
            return
        
        label_path = self.labels_dir / f"{img_path.stem}.txt"
        
        # Crear archivo de etiqueta vacío si no existe
        if not label_path.exists():
            with open(label_path, 'w') as f:
                f.write("# Formato YOLO: <class_id> <x_center> <y_center> <width> <height>\n")
                f.write("# Coordenadas normalizadas (0-1)\n")
                f.write("# Clases: 0=escape, 1=elephant, 2=giraffe, 3=lion, 4=tiger, 5=bear, 6=zebra, 7=monkey\n")
                f.write("# Ejemplo: 0 0.5 0.5 0.3 0.4\n")
            print(f"✓ Archivo de etiqueta creado: {label_path.name}")
        else:
            print(f"⚠️  El archivo de etiqueta ya existe: {label_path.name}")
    
    def validate_labels(self):
        """Valida que los archivos de etiquetas estén correctos."""
        images = self.list_images()
        valid_count = 0
        invalid_count = 0
        
        print("\n🔍 Validando etiquetas...")
        
        for img in images:
            label_file = self.labels_dir / f"{img.stem}.txt"
            
            if not label_file.exists():
                print(f"⚠️  {img.name}: Sin archivo de etiqueta")
                invalid_count += 1
                continue
            
            # Leer y validar etiquetas
            try:
                with open(label_file, 'r') as f:
                    lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
                
                if not lines:
                    print(f"⚠️  {img.name}: Archivo de etiqueta vacío")
                    invalid_count += 1
                    continue
                
                # Validar formato de cada línea
                valid = True
                for line in lines:
                    parts = line.split()
                    if len(parts) != 5:
                        print(f"❌ {img.name}: Formato incorrecto en línea: {line}")
                        valid = False
                        break
                    
                    try:
                        class_id = int(parts[0])
                        coords = [float(p) for p in parts[1:5]]
                        
                        # Validar rangos
                        if class_id < 0 or class_id > 7:
                            print(f"❌ {img.name}: class_id fuera de rango: {class_id}")
                            valid = False
                            break
                        
                        if not all(0 <= c <= 1 for c in coords):
                            print(f"❌ {img.name}: Coordenadas fuera de rango (0-1)")
                            valid = False
                            break
                    
                    except ValueError:
                        print(f"❌ {img.name}: Valores no numéricos en: {line}")
                        valid = False
                        break
                
                if valid:
                    print(f"✓ {img.name}: Etiquetas válidas ({len(lines)} objetos)")
                    valid_count += 1
                else:
                    invalid_count += 1
            
            except Exception as e:
                print(f"❌ {img.name}: Error al leer etiqueta: {e}")
                invalid_count += 1
        
        print(f"\n📊 Resumen de validación:")
        print(f"  ✓ Válidas: {valid_count}")
        print(f"  ❌ Inválidas: {invalid_count}")
        print(f"  📸 Total: {len(images)}")
        
        return valid_count, invalid_count
    
    def get_statistics(self):
        """Obtiene estadísticas del dataset."""
        images = list(self.images_dir.glob('*.[jp][pn][g]')) + \
                 list(self.images_dir.glob('*.jpeg'))
        labels = list(self.labels_dir.glob('*.txt'))
        
        print("\n📊 Estadísticas del Dataset:")
        print(f"  📸 Imágenes totales: {len(images)}")
        print(f"  🏷️  Archivos de etiquetas: {len(labels)}")
        print(f"  📁 Ubicación: {self.base_dir.absolute()}")
        
        # Contar objetos por clase
        class_counts = {i: 0 for i in range(8)}
        total_objects = 0
        
        for label_file in labels:
            try:
                with open(label_file, 'r') as f:
                    lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith('#')]
                    for line in lines:
                        parts = line.split()
                        if len(parts) == 5:
                            class_id = int(parts[0])
                            if 0 <= class_id <= 7:
                                class_counts[class_id] += 1
                                total_objects += 1
            except:
                continue
        
        if total_objects > 0:
            print(f"\n  🎯 Objetos etiquetados por clase:")
            class_names = ['escape', 'elephant', 'giraffe', 'lion', 'tiger', 'bear', 'zebra', 'monkey']
            for class_id, count in class_counts.items():
                if count > 0:
                    print(f"    {class_names[class_id]}: {count}")
            print(f"  📦 Total de objetos: {total_objects}")


def main():
    """Función principal."""
    print("="*70)
    print("🦁 HERRAMIENTA DE PREPARACIÓN DE IMÁGENES - YOLO")
    print("="*70)
    
    tool = ImagePreparationTool()
    
    while True:
        print("\n" + "="*70)
        print("MENÚ:")
        print("  1. Importar imágenes desde directorio")
        print("  2. Listar imágenes disponibles")
        print("  3. Crear archivo de etiqueta para imagen")
        print("  4. Validar etiquetas")
        print("  5. Ver estadísticas del dataset")
        print("  6. Salir")
        print("="*70)
        
        choice = input("\nSelecciona una opción (1-6): ").strip()
        
        if choice == '1':
            source = input("Ruta del directorio con imágenes: ").strip()
            tool.import_images(source)
        
        elif choice == '2':
            tool.list_images()
        
        elif choice == '3':
            image_name = input("Nombre del archivo de imagen: ").strip()
            tool.create_label_template(image_name)
        
        elif choice == '4':
            tool.validate_labels()
        
        elif choice == '5':
            tool.get_statistics()
        
        elif choice == '6':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == '__main__':
    main()
