import os

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def load_font(font_path):
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Файл шрифта {font_path} не найден! Укажи правильный путь.")
    pdfmetrics.registerFont(TTFont("JapaneseFont", font_path))