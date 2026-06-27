from pathlib import Path
import json

base_path = Path(r"D:\archive\SROIE2019\train")

img_dir = base_path / "img"
entities_dir = base_path / "entities"
box_dir = base_path / "box"

images = sorted(img_dir.glob("*.jpg"))
entities = sorted(entities_dir.glob("*.txt"))
boxes = sorted(box_dir.glob("*.txt"))

print("Số ảnh:", len(images))
print("Số file entities:", len(entities))
print("Số file box:", len(boxes))

# Kiểm tra 5 ảnh đầu tiên có đủ file entities và box không
for img_path in images[:5]:
    file_id = img_path.stem

    entity_path = entities_dir / f"{file_id}.txt"
    box_path = box_dir / f"{file_id}.txt"

    print("\nẢnh:", img_path.name)
    print("Có entities:", entity_path.exists())
    print("Có box:", box_path.exists())

    if entity_path.exists():
        with open(entity_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Thông tin đúng:", data)