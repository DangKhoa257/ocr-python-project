from pathlib import Path
import json
import time
import pandas as pd
from PIL import Image

from ocr_engine import extract_text
from text_utils import text_statistics


base_path = Path(r"D:\archive\SROIE2019\train")
img_dir = base_path / "img"
entities_dir = base_path / "entities"

results_dir = Path("results")
results_dir.mkdir(exist_ok=True)

images = sorted(img_dir.glob("*.jpg"))

LIMIT = 20  # chạy thử 20 ảnh trước

rows = []

start_time = time.time()

for index, image_path in enumerate(images[:LIMIT], start=1):
    file_id = image_path.stem
    entity_path = entities_dir / f"{file_id}.txt"

    print(f"\n[{index}/{LIMIT}] Đang OCR: {image_path.name}")

    try:
        image = Image.open(image_path).convert("RGB")
        ocr_text = extract_text(image)

        with open(entity_path, "r", encoding="utf-8") as f:
            true_data = json.load(f)

        stats = text_statistics(ocr_text)

        rows.append({
            "image_name": image_path.name,
            "ocr_text": ocr_text,
            "num_characters": stats["characters"],
            "num_words": stats["words"],
            "num_lines": stats["lines"],
            "true_company": true_data.get("company", ""),
            "true_date": true_data.get("date", ""),
            "true_address": true_data.get("address", ""),
            "true_total": true_data.get("total", "")
        })

    except Exception as e:
        print("Lỗi:", e)
        rows.append({
            "image_name": image_path.name,
            "ocr_text": "",
            "num_characters": 0,
            "num_words": 0,
            "num_lines": 0,
            "true_company": "",
            "true_date": "",
            "true_address": "",
            "true_total": "",
            "error": str(e)
        })

df = pd.DataFrame(rows)

output_path = results_dir / "ocr_results_sample.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")

end_time = time.time()

print("\n===== HOÀN THÀNH =====")
print("Số ảnh đã OCR:", len(df))
print("File kết quả:", output_path)
print("Thời gian chạy:", round(end_time - start_time, 2), "giây")