import os
import torch
from ultralytics import YOLO

def train_weight_model(
    dataset_path='weights_yolo_dataset',
    pretrained_model='yolov8l.pt',
    epochs=75,
    img_size=640,
    batch_size=16,
    output_name='yolov8_weights_custom',
    fp16=True
):
    """
    Train a custom YOLOv8 object detection model for detecting multiple weights
    (dumbbells, barbells, kettlebells, plates, etc).

    Features:
        - Auto-selects GPU if available.
        - Uses mixed precision (FP16).
        - Strong augmentations (color jitter, blur, noise, cutout).
        - Multi-class training supported (ensure data.yaml has 4 classes).
    """
    print("\n--- YOLOv8 Custom Weight Detection Training ---\n")
    
    # --- Check dataset ---
    data_yaml = os.path.join(dataset_path, 'data.yaml')
    if not os.path.exists(data_yaml):
        print(f"❌ ERROR: Dataset file not found: {data_yaml}")
        return

    # --- Detect GPU ---
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    # --- Load pre-trained model ---
    try:
        model = YOLO(pretrained_model)
        print(f"✅ Loaded pre-trained model '{pretrained_model}'.")
    except Exception as e:
        print(f"❌ ERROR: Failed to load YOLOv8 model: {e}")
        return

    # --- Training ---
    print(f"\n🚀 Starting training on dataset: {dataset_path}")
    print(f"Epochs: {epochs}, Image Size: {img_size}, Batch Size: {batch_size}, FP16: {fp16}\n")
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True

    try:
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            name=output_name,
            device=device,
            exist_ok=True,
            workers = os.cpu_count() // 2,
            patience=15,
            lr0=0.01,
            optimizer='AdamW',
            amp=fp16,
            
            # Augmentation settings
            augment=True,
            hsv_h=0.5,       # Hue ±50°
            hsv_s=0.5,       # Saturation ±50%
            hsv_v=0.25,      # Brightness ±25%
            scale=0.5,       # Random zoom
            flipud=0.0,      # Disable vertical flip (not useful for weights)
            fliplr=0.5,      # Random left-right flip
            degrees=0.0,     # No rotation (keep orientation natural)
            shear=0.0,       # Disable shear
            perspective=0.0, # Disable perspective
            translate=0.1,   # Slight translation
            copy_paste=0.0,  # Disable copy-paste
            erasing=0.15,    # Cutout-style random erasing
            mosaic=1.0,      # Mosaic augmentation
            mixup=0.2        # Mixup augmentation
        )
    except Exception as e:
        print(f"❌ ERROR: Training failed: {e}")
        return

    # --- Training Complete ---
    best_model_path = os.path.join('runs', 'detect', output_name, 'weights', 'best.pt')
    print("\n✅ Training Complete!")
    print(f"Best model saved at: {best_model_path}")

    # --- Metrics summary ---
    if results:
        print("\n📊 Training Metrics Summary:")
        for k, v in results.metrics.items():
            print(f"  {k}: {v}")

if __name__ == '__main__':
    train_weight_model(
        dataset_path='weights_yolo_dataset',
        pretrained_model='yolov8n.pt',
        epochs=75,
        img_size=640,
        batch_size=16,
        output_name='yolov8_weights_custom',
        fp16=True
    )
