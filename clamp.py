import os
import cv2

def fix_labels(img_dir, label_dir, out_label_dir, target_size=640):
    os.makedirs(out_label_dir, exist_ok=True)

    for label_file in os.listdir(label_dir):
        if not label_file.endswith(".txt"):
            continue

        img_file = os.path.join(img_dir, label_file.replace(".txt", ".jpg"))
        if not os.path.exists(img_file):
            print(f"⚠️ Missing image for {label_file}")
            continue

        # Load image to get original size
        img = cv2.imread(img_file)
        h, w = img.shape[:2]

        # Compute scale and padding
        scale = min(target_size / w, target_size / h)
        new_w, new_h = int(w * scale), int(h * scale)
        pad_x = (target_size - new_w) // 2
        pad_y = (target_size - new_h) // 2

        fixed_lines = []
        with open(os.path.join(label_dir, label_file), "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                cls, x, y, bw, bh = map(float, parts)

                # Convert normalized → pixel
                x *= w
                y *= h
                bw *= w
                bh *= h

                # Scale
                x = x * scale + pad_x
                y = y * scale + pad_y
                bw *= scale
                bh *= scale

                # Normalize to new size
                x /= target_size
                y /= target_size
                bw /= target_size
                bh /= target_size

                fixed_lines.append(f"{int(cls)} {x:.6f} {y:.6f} {bw:.6f} {bh:.6f}")

        out_path = os.path.join(out_label_dir, label_file)
        with open(out_path, "w") as f:
            f.write("\n".join(fixed_lines))

    print("✅ Labels fixed and saved to:", out_label_dir)


# Example usage:
# fix_labels("weights_yolo_dataset/train/images", "weights_yolo_dataset/train/labels",
#            "weights_yolo_dataset/train/labels_fixed", target_size=640)
