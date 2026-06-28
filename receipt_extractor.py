import re
from text_utils import normalize_text


def normalize_amount(value):
    """
    Chuẩn hóa tiền:
    9,00 -> 9.00
    RM 9.00 -> 9.00
    """

    if not value:
        return ""

    value = value.upper()

    value = value.replace("RM", "")
    value = value.replace("$", "")
    value = value.strip()

    # 9,00 -> 9.00
    if re.fullmatch(r"\d+,\d{2}", value):
        value = value.replace(",", ".")

    # 1,299.50 -> 1299.50
    elif "," in value and "." in value:
        value = value.replace(",", "")

    return value


def normalize_date(date_text):
    """
    25-12-2018 -> 25/12/2018
    12-01-19 -> 12/01/2019
    """

    if not date_text:
        return ""

    date_text = date_text.replace("-", "/")
    date_text = date_text.replace(".", "/")

    parts = date_text.split("/")

    if len(parts) != 3:
        return date_text

    day, month, year = parts

    if len(year) == 2:
        year = "20" + year

    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"


def extract_company(ocr_text):
    text = normalize_text(ocr_text)

    lines = text.split("\n")

    ignore = [
        "receipt",
        "invoice",
        "tax invoice",
        "total",
        "cash",
        "thank"
    ]

    for line in lines[:5]:

        low = line.lower()

        if any(word in low for word in ignore):
            continue

        if len(line) > 3:
            return line

    return ""


def extract_date(ocr_text):

    pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"

    match = re.search(pattern, ocr_text)

    if match:
        return normalize_date(match.group())

    return ""


def extract_total(ocr_text):

    text = ocr_text.upper()

    patterns = [
        r"TOTAL\s*:?\s*(RM\s*)?([\d,]+\.\d{2})",
        r"GRAND TOTAL\s*:?\s*(RM\s*)?([\d,]+\.\d{2})",
        r"AMOUNT\s*:?\s*(RM\s*)?([\d,]+\.\d{2})",
        r"TOTAL\s*:?\s*(RM\s*)?([\d,]+,\d{2})",
    ]

    for pattern in patterns:

        match = re.search(pattern, text)

        if match:
            return normalize_amount(match.group(2))

    numbers = re.findall(r"[\d,]+\.\d{2}|[\d,]+,\d{2}", text)

    if numbers:
        return normalize_amount(numbers[-1])

    return ""


def extract_address(ocr_text):

    text = normalize_text(ocr_text)

    lines = text.split("\n")

    address = []

    for line in lines[1:6]:

        low = line.lower()

        if "tel" in low:
            break

        if "total" in low:
            break

        if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", line):
            break

        address.append(line)

    return ", ".join(address)
