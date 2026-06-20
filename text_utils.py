def clean_text(text):
    lines = text.split("\n")
    clean_lines = []

    for line in lines:
        line = line.strip()

        if line != "":
            clean_lines.append(line)

    return "\n".join(clean_lines)

def count_characters(text):
    return len(text)

def count_lines(text):
    if text.strip() == "":
        return 0

    return len(text.split("\n"))