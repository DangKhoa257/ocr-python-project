import re


# ===========================
# Chuan hoa van ban
# ===========================

def normalize_text(text):
    """
    Lam sach van ban OCR.
    """
    if text is None:
        return ""

    text = str(text).replace("\r", "\n")
    lines = []

    for line in text.split("\n"):
        line = line.strip()
        if line:
            lines.append(line)

    return "\n".join(lines)


# ===========================
# Chuan hoa so tien
# ===========================

def normalize_amount(value):
    """
    Vi du:
    RM 9.00 -> 9.00
    9,00 -> 9.00
    1,299.50 -> 1299.50
    """
    if value is None:
        return ""

    value = str(value).upper()
    value = value.replace("RM", "")
    value = value.replace("MYR", "")
    value = value.replace("$", "")
    value = value.strip()

    match = re.search(r"\d[\d,\.\s]*", value)
    if not match:
        return ""

    value = re.sub(r"\s+", "", match.group(0))

    # 9,00 -> 9.00
    if re.fullmatch(r"\d+,\d{2}", value):
        value = value.replace(",", ".")

    # 1,299.50 -> 1299.50
    elif "," in value and "." in value:
        value = value.replace(",", "")

    # 1,299 -> 1299
    elif re.fullmatch(r"\d{1,3}(,\d{3})+", value):
        value = value.replace(",", "")

    try:
        return f"{float(value):.2f}"
    except ValueError:
        return ""


# ===========================
# Chuan hoa ngay
# ===========================

def normalize_date(date_text):
    """
    25-12-2018 -> 25/12/2018
    12-01-19 -> 12/01/2019
    """
    if date_text is None:
        return ""

    date_text = str(date_text).strip()
    match = re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", date_text)
    if match:
        date_text = match.group(0)

    date_text = date_text.replace("-", "/")
    date_text = date_text.replace(".", "/")
    parts = date_text.split("/")

    if len(parts) != 3:
        return date_text

    day, month, year = parts

    if len(year) == 2:
        year = "20" + year

    return f"{day.zfill(2)}/{month.zfill(2)}/{year}"


# ===========================
# Trich xuat ten cua hang
# ===========================

def extract_company(ocr_text):
    text = normalize_text(ocr_text)
    lines = text.split("\n")

    blacklist = [
        "receipt",
        "invoice",
        "tax invoice",
        "cash",
        "thank",
        "date",
        "time",
        "total",
    ]

    for line in lines[:5]:
        lower = line.lower()

        if any(word in lower for word in blacklist):
            continue

        if len(line) >= 3:
            return line

    return ""


# ===========================
# Trich xuat ngay
# ===========================

def extract_date(ocr_text):
    text = normalize_text(ocr_text)
    patterns = [
        r"\d{1,2}[/-]\d{1,2}[/-]\d{4}",
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group())

    return ""


# ===========================
# Trich xuat tong tien
# ===========================

def extract_total(ocr_text):
    text = normalize_text(ocr_text).upper()
    patterns = [
        r"GRAND TOTAL\s*:?\s*(RM\s*)?([\d,]+\.\d{2})",
        r"TOTAL\s*:?\s*(RM\s*)?([\d,]+\.\d{2})",
        r"AMOUNT\s*:?\s*(RM\s*)?([\d,]+\.\d{2})",
        r"NETT\s*:?\s*(RM\s*)?([\d,]+\.\d{2})",
        r"TOTAL\s*:?\s*(RM\s*)?([\d,]+,\d{2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return normalize_amount(match.group(2))

    # Neu khong tim thay TOTAL thi lay so tien cuoi cung
    amounts = re.findall(r"[\d,]+\.\d{2}|[\d,]+,\d{2}", text)
    if amounts:
        return normalize_amount(amounts[-1])

    return ""


# ===========================
# Trich xuat dia chi
# ===========================

def extract_address(ocr_text):
    text = normalize_text(ocr_text)
    lines = text.split("\n")

    if len(lines) <= 1:
        return ""

    address = []

    for line in lines[1:6]:
        lower = line.lower()

        if "tel" in lower or "phone" in lower:
            break

        if "date" in lower or "time" in lower or "total" in lower:
            break

        if re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", line):
            break

        address.append(line)

    return ", ".join(address)


# ===========================
# Test
# ===========================

if __name__ == "__main__":
    sample = """
    ABC MART SDN BHD
    123 Jalan Bukit
    Kuala Lumpur

    Date: 25-12-2018

    TOTAL RM 9,00
    """

    print("Company :", extract_company(sample))
    print("Address :", extract_address(sample))
    print("Date    :", extract_date(sample))
    print("Total   :", extract_total(sample))
