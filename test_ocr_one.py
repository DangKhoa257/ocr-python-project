from pathlib import Path
import json
from PIL import Image

from ocr_engine import extract_text

base_path = Path(r"D:\archive\SROIE2019\train")

img_dir = base_path / "img"
entities_dir = base_path / "entities"

# Lấy ảnh đầu tiên trong thư mục img
image_path = sorted(img_dir.glob("*.jpg"))[0]
file_id = image_path.stem
entity_path = entities_dir / f"{file_id}.txt"

print("Đang OCR ảnh:", image_path.name)

# Mở ảnh
image = Image.open(image_path).convert("RGB")

# Chạy OCR bằng hàm extract_text trong ocr_engine.py
ocr_text = extract_text(image)

print("\n===== KẾT QUẢ OCR =====")
print(ocr_text)

# Đọc đáp án đúng từ entities
with open(entity_path, "r", encoding="utf-8") as f:
    true_data = json.load(f)

print("\n===== THÔNG TIN ĐÚNG TRONG DATASET =====")
print("Company:", true_data.get("company"))
print("Date:", true_data.get("date"))
print("Address:", true_data.get("address"))
print("Total:", true_data.get("total"))