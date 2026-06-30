import easyocr
import numpy as np

_readers = {}


def get_reader(languages=None, gpu=False):
    """Tạo EasyOCR reader và dùng lại cho các lần OCR sau."""
    if languages is None:
        languages = ["vi", "en"]

    key = (tuple(languages), gpu)
    if key not in _readers:
        _readers[key] = easyocr.Reader(list(languages), gpu=gpu)

    return _readers[key]


def extract_text(
    image,
    languages=None,
    gpu=False,
    detail=1,
    paragraph=False,
    canvas_size=1600,
    mag_ratio=1.0,
):
    """Chạy OCR và trả về text theo từng dòng."""
    image_array = np.array(image)
    ocr_reader = get_reader(languages=languages, gpu=gpu)

    results = ocr_reader.readtext(
        image_array,
        detail=detail,
        paragraph=paragraph,
        contrast_ths=0.1,
        adjust_contrast=0.5,
        text_threshold=0.6,
        low_text=0.3,
        decoder="greedy",
        canvas_size=canvas_size,
        mag_ratio=mag_ratio,
    )

    text_list = []
    for result in results:
        if detail == 0:
            text_list.append(str(result))
        else:
            text_list.append(str(result[1]))

    return "\n".join(text_list)
