import os
import json
import csv
from pathlib import Path
from PIL import Image
from ocr_engine import extract_text
from preprocess import ImagePreprocessor

# ===== CẤU HÌNH ĐƯỜNG DẪN =====
# Cập nhật BASE_PATH cho phù hợp 
BASE_PATH = Path(r"C:\Users\Admin\Downloads\archive\SROIE2019\train")

IMG_DIR = BASE_PATH / "img"
ENTITIES_DIR = BASE_PATH / "entities"
OUTPUT_DIR = Path("results")
OUTPUT_CSV = OUTPUT_DIR / "ocr_results.csv"
# ================================

def read_entities(entities_path):
    try:
        with open(entities_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return (
            data.get("company", ""),
            data.get("date", ""),
            data.get("address", ""),
            data.get("total", "")
        )
    except:
        return "", "", "", ""

def run_batch_ocr():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    preprocessor = ImagePreprocessor()

    image_files = sorted([
        f for f in os.listdir(IMG_DIR) if f.lower().endswith(".jpg")
    ])

    print(f"Tìm thấy {len(image_files)} ảnh. Bắt đầu OCR...")

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "image_name", "ocr_text",
            "num_characters", "num_words", "num_lines",
            "true_company", "true_date", "true_address", "true_total"
        ])

        for i, filename in enumerate(image_files):
            img_path = os.path.join(IMG_DIR, filename)
            name_without_ext = os.path.splitext(filename)[0]
            entities_path = os.path.join(ENTITIES_DIR, name_without_ext + ".txt")

            print(f"[{i+1}/{len(image_files)}] Đang xử lý: {filename}")

            try:
                img = Image.open(img_path).convert("RGB")
                cleaned_img = preprocessor.process_invoice_image(img)
                ocr_text = extract_text(cleaned_img)

                num_characters = len(ocr_text)
                num_words = len(ocr_text.split())
                num_lines = len(ocr_text.splitlines())

                true_company, true_date, true_address, true_total = read_entities(entities_path)

                writer.writerow([
                    filename, ocr_text,
                    num_characters, num_words, num_lines,
                    true_company, true_date, true_address, true_total
                ])

            except Exception as e:
                print(f"  Lỗi với {filename}: {e}")
                writer.writerow([filename, "", 0, 0, 0, "", "", "", ""])

    print(f"\nHoàn thành! Kết quả lưu tại: {OUTPUT_CSV}")

if __name__ == "__main__":
    run_batch_ocr()