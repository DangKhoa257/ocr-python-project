import easyocr
import numpy as np

reader = None

def get_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['vi', 'en'])
    return reader

def extract_text(image):
    image_array = np.array(image)
    ocr_reader = get_reader()
    
    results = ocr_reader.readtext(
        image_array,
        contrast_ths=0.1,
        adjust_contrast=0.5,
        text_threshold=0.6,
        low_text=0.3
    )
    
    text_list = []
    for result in results:
        text = result[1]
        text_list.append(text)
    
    return "\n".join(text_list)