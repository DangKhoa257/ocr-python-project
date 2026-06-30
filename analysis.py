from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


RESULTS_DIR = Path("results")
INPUT_CSV = RESULTS_DIR / "evaluated_results.csv"
SUMMARY_CSV = RESULTS_DIR / "analysis_summary.csv"
CHARTS_DIR = RESULTS_DIR / "charts"


def accuracy_percent(series):
    """Tinh phan tram dung."""
    if len(series) == 0:
        return 0.0

    return round(series.mean() * 100, 2)


def save_field_accuracy_chart(accuracies):
    """Ve bieu do accuracy theo truong."""
    labels = ["company", "date", "address", "total"]
    values = [accuracies[label] for label in labels]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b", "#e45756"])
    plt.title("Field accuracy")
    plt.ylabel("Accuracy (%)")
    plt.ylim(0, 100)

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value + 1, f"{value}%", ha="center")

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "field_accuracy.png", dpi=150)
    plt.close()


def save_ocr_statistics_chart(avg_characters, avg_words, avg_lines):
    """Ve bieu do thong ke text OCR."""
    labels = ["num_characters", "num_words", "num_lines"]
    values = [avg_characters, avg_words, avg_lines]

    plt.figure(figsize=(8, 5))
    bars = plt.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b"])
    plt.title("OCR text statistics")
    plt.ylabel("Average value")

    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width() / 2, value, str(value), ha="center", va="bottom")

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "ocr_text_statistics.png", dpi=150)
    plt.close()


def save_correct_vs_wrong_chart(df):
    """Ve bieu do so sanh dung va sai."""
    labels = ["company", "date", "address", "total"]
    correct_values = [int(df[f"{label}_correct"].sum()) for label in labels]
    wrong_values = [len(df) - value for value in correct_values]
    positions = range(len(labels))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar([pos - width / 2 for pos in positions], correct_values, width, label="Dung")
    plt.bar([pos + width / 2 for pos in positions], wrong_values, width, label="Sai")
    plt.xticks(list(positions), labels)
    plt.title("Correct vs wrong")
    plt.ylabel("Number of receipts")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "correct_vs_wrong.png", dpi=150)
    plt.close()


def main():
    if not INPUT_CSV.exists():
        print("Chua co results/evaluated_results.csv. Hay chay python evaluate_results.py truoc.")
        return

    RESULTS_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_CSV).fillna("")
    total_receipts = len(df)

    avg_num_characters = round(df["num_characters"].mean(), 2) if total_receipts else 0.0
    avg_num_words = round(df["num_words"].mean(), 2) if total_receipts else 0.0
    avg_num_lines = round(df["num_lines"].mean(), 2) if total_receipts else 0.0

    accuracies = {
        "company": accuracy_percent(df["company_correct"]),
        "date": accuracy_percent(df["date_correct"]),
        "address": accuracy_percent(df["address_correct"]),
        "total": accuracy_percent(df["total_correct"]),
    }

    summary = pd.DataFrame([
        {"metric": "total_receipts", "value": total_receipts},
        {"metric": "avg_num_characters", "value": avg_num_characters},
        {"metric": "avg_num_words", "value": avg_num_words},
        {"metric": "avg_num_lines", "value": avg_num_lines},
        {"metric": "date_accuracy", "value": accuracies["date"]},
        {"metric": "total_accuracy", "value": accuracies["total"]},
        {"metric": "company_accuracy", "value": accuracies["company"]},
        {"metric": "address_accuracy", "value": accuracies["address"]},
    ])

    summary.to_csv(SUMMARY_CSV, index=False, encoding="utf-8-sig")

    save_field_accuracy_chart(accuracies)
    save_ocr_statistics_chart(avg_num_characters, avg_num_words, avg_num_lines)
    save_correct_vs_wrong_chart(df)

    print("Tong so hoa don da xu ly:", total_receipts)
    print("Trung binh so ky tu OCR moi hoa don:", avg_num_characters)
    print("Trung binh so tu OCR moi hoa don:", avg_num_words)
    print("Trung binh so dong OCR moi hoa don:", avg_num_lines)
    print("Ty le dung date:", f"{accuracies['date']}%")
    print("Ty le dung total:", f"{accuracies['total']}%")
    print("Ty le dung company:", f"{accuracies['company']}%")
    print("Ty le dung address:", f"{accuracies['address']}%")
    print("File tong hop:", SUMMARY_CSV)
    print("Thu muc bieu do:", CHARTS_DIR)


if __name__ == "__main__":
    main()
