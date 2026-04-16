import easyocr
import os

# Инициализируем читатель только для упрощённого китайского и английского
reader = None

def get_reader():
    global reader
    if reader is None:
        # Только упрощённый китайский и английский
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    return reader

def extract_text_from_image(image_path):
    """
    Извлекает текст с изображения с помощью OCR
    Возвращает строку с распознанным текстом
    """
    if not os.path.exists(image_path):
        return f"Файл не найден: {image_path}"
    
    try:
        rdr = get_reader()
        result = rdr.readtext(image_path, detail=0, paragraph=True)
        text = ' '.join(result)
        print(f"OCR распознал: {text[:200] if text else 'пусто'}")
        return text
    except Exception as e:
        print(f"Ошибка OCR: {e}")
        return ""