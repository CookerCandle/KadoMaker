import os

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def load_font(name: str, font_path: str):
    """
    Регистрирует шрифт в ReportLab под указанным именем.
    """
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Файл шрифта {font_path} не найден! Укажи правильный путь.")
    pdfmetrics.registerFont(TTFont(name, font_path))
