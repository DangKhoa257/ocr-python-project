import re


def clean_text(text):
    """
    Xóa khoảng trắng dư thừa và dòng trống.
    """
    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()

        if line:
            clean_lines.append(line)

    return "\n".join(clean_lines)


def normalize_text(text):
    """
    Chuẩn hóa văn bản OCR.
    """
    if text is None:
        return ""

    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return clean_text(text)


def count_characters(text):
    return len(text)


def count_words(text):
    words = text.split()
    return len(words)


def count_lines(text):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return len(lines)


def text_statistics(text):
    return {
        "characters": count_characters(text),
        "words": count_words(text),
        "lines": count_lines(text)
    }


# Chạy thử
if __name__ == "__main__":
    sample_text = """
        Hello World

        OCR Project
        Python Programming

    """

    cleaned = normalize_text(sample_text)

    print("=== Clean Text ===")
    print(cleaned)

    print("\n=== Statistics ===")
    stats = text_statistics(cleaned)

    print("Characters:", stats["characters"])
    print("Words:", stats["words"])
    print("Lines:", stats["lines"])
