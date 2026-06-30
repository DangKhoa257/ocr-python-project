from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

from receipt_extractor import (
    extract_address,
    extract_company,
    extract_date,
    extract_total,
    normalize_amount,
    normalize_date,
)


RESULTS_DIR = Path("results")
INPUT_CSV = RESULTS_DIR / "ocr_results.csv"
OUTPUT_CSV = RESULTS_DIR / "evaluated_results.csv"


def similarity(text1, text2):
    """Tinh do giong nhau giua 2 chuoi."""
    text1 = "" if pd.isna(text1) else str(text1).lower().strip()
    text2 = "" if pd.isna(text2) else str(text2).lower().strip()

    if not text1 or not text2:
        return 0.0

    return SequenceMatcher(None, text1, text2).ratio()


def accuracy_percent(series):
    """Tinh phan tram dung."""
    if len(series) == 0:
        return 0.0

    return round(series.mean() * 100, 2)


def main():
    if not INPUT_CSV.exists():
        print("Chua co results/ocr_results.csv. Hay chay python batch_ocr.py truoc.")
        return

    RESULTS_DIR.mkdir(exist_ok=True)
    df = pd.read_csv(INPUT_CSV).fillna("")

    df["pred_company"] = df["ocr_text"].apply(extract_company)
    df["pred_date"] = df["ocr_text"].apply(extract_date)
    df["pred_address"] = df["ocr_text"].apply(extract_address)
    df["pred_total"] = df["ocr_text"].apply(extract_total)

    df["true_date_norm"] = df["true_date"].apply(normalize_date)
    df["true_total_norm"] = df["true_total"].apply(normalize_amount)

    df["date_correct"] = df["pred_date"] == df["true_date_norm"]
    df["total_correct"] = df["pred_total"] == df["true_total_norm"]

    df["company_similarity"] = df.apply(
        lambda row: similarity(row["pred_company"], row["true_company"]),
        axis=1,
    )
    df["company_correct"] = df["company_similarity"] >= 0.6

    df["address_similarity"] = df.apply(
        lambda row: similarity(row["pred_address"], row["true_address"]),
        axis=1,
    )
    df["address_correct"] = df["address_similarity"] >= 0.5

    output_columns = [
        "image_name",
        "ocr_text",
        "true_company",
        "true_date",
        "true_address",
        "true_total",
        "pred_company",
        "pred_date",
        "pred_address",
        "pred_total",
        "true_date_norm",
        "true_total_norm",
        "date_correct",
        "total_correct",
        "company_similarity",
        "company_correct",
        "address_similarity",
        "address_correct",
        "num_characters",
        "num_words",
        "num_lines",
    ]

    df[output_columns].to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    total_receipts = len(df)
    receipts_with_text = int((df["ocr_text"].astype(str).str.strip() != "").sum())

    print("Tong so hoa don:", total_receipts)
    print("So hoa don OCR co text:", receipts_with_text)
    print("Date accuracy:", f"{accuracy_percent(df['date_correct'])}%")
    print("Total accuracy:", f"{accuracy_percent(df['total_correct'])}%")
    print("Company accuracy:", f"{accuracy_percent(df['company_correct'])}%")
    print("Address accuracy:", f"{accuracy_percent(df['address_correct'])}%")
    print("Duong dan file output:", OUTPUT_CSV)


if __name__ == "__main__":
    main()
