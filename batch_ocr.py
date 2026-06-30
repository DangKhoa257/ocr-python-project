import csv
import json
import os
import time
from pathlib import Path

from PIL import Image

from ocr_engine import extract_text
from preprocess import ImagePreprocessor

# ===== CẤU HÌNH ĐƯỜNG DẪN =====
# Người chạy cần sửa BASE_PATH theo vị trí dataset SROIE2019 trên máy mình.
BASE_PATH = Path(r"D:\archive\SROIE2019\train")

IMG_DIR = BASE_PATH / "img"
ENTITIES_DIR = BASE_PATH / "entities"
OUTPUT_DIR = Path("results")
OUTPUT_CSV = OUTPUT_DIR / "ocr_results.csv"

# Đặt số nhỏ như 20 để test nhanh; đặt None để chạy toàn bộ dataset.
LIMIT = None
MAX_IMAGE_SIZE = 960
# ================================


def read_entities(entities_path):
    try:
        with open(entities_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return (
            data.get("company", ""),
            data.get("date", ""),
            data.get("address", ""),
            data.get("total", ""),
        )
    except Exception:
        return "", "", "", ""


def get_image_files():
    if not IMG_DIR.exists():
        raise FileNotFoundError(
            f"Không tìm thấy thư mục ảnh: {IMG_DIR}. Hãy sửa BASE_PATH trong batch_ocr.py."
        )

    image_files = sorted(
        file_name for file_name in os.listdir(IMG_DIR)
        if file_name.lower().endswith((".jpg", ".jpeg", ".png"))
    )

    if LIMIT is not None:
        image_files = image_files[:LIMIT]

    return image_files


def run_batch_ocr():
    OUTPUT_DIR.mkdir(exist_ok=True)
    preprocessor = ImagePreprocessor()
    image_files = get_image_files()

    print(f"Tìm thấy {len(image_files)} ảnh. Bắt đầu OCR...")
    print("Batch dùng EasyOCR tiếng Anh để chạy nhanh hơn với dataset SROIE.")

    start_time = time.time()

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "image_name", "ocr_text",
            "num_characters", "num_words", "num_lines",
            "true_company", "true_date", "true_address", "true_total",
        ])

        for index, filename in enumerate(image_files, start=1):
            img_path = IMG_DIR / filename
            entities_path = ENTITIES_DIR / f"{Path(filename).stem}.txt"

            print(f"[{index}/{len(image_files)}] Đang xử lý: {filename}", flush=True)

            try:
                image = Image.open(img_path).convert("RGB")
                cleaned_img = preprocessor.process_invoice_image(image, target_size=MAX_IMAGE_SIZE)
                ocr_text = extract_text(
                    cleaned_img,
                    languages=["en"],
                    detail=0,
                    paragraph=True,
                    canvas_size=1280,
                )

                num_characters = len(ocr_text)
                num_words = len(ocr_text.split())
                num_lines = len(ocr_text.splitlines())
                true_company, true_date, true_address, true_total = read_entities(entities_path)

                writer.writerow([
                    filename, ocr_text,
                    num_characters, num_words, num_lines,
                    true_company, true_date, true_address, true_total,
                ])
                csvfile.flush()

            except Exception as error:
                print(f"  Lỗi với {filename}: {error}", flush=True)
                writer.writerow([filename, "", 0, 0, 0, "", "", "", ""])
                csvfile.flush()

    elapsed = round(time.time() - start_time, 2)
    print(f"\nHoàn thành! Kết quả lưu tại: {OUTPUT_CSV}")
    print(f"Thời gian chạy: {elapsed} giây")


if __name__ == "__main__":
    run_batch_ocr()
