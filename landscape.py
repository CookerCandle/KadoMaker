from sources.fonts import load_font
from sources.wrap import wrap_text
from sources.words import load_words

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import red, black, lime


def create_flashcards_pdf(words, name, pdf_filename, font_path):
    """
    Создает PDF-файл с карточками слов (кандзи, чтение, перевод).
    Первый лист: Кандзи по центру карточек.
    Второй лист: Чтение и перевод, расположенные зеркально по X-оси.
    """
    c = canvas.Canvas(pdf_filename, pagesize=landscape(A4))
    load_font(font_path)  # Загружаем шрифт
    
    width, height = landscape(A4)  # Получаем размеры альбомного A4
    margin = 40  # Отступы от краев страницы
    cards_per_row, cards_per_col = 4, 4  # Количество карточек в строке и колонке
    card_width = (width - 2 * margin) / cards_per_row  # Вычисляем ширину карточки
    card_height = (height - 2 * margin) / cards_per_col  # Вычисляем высоту карточки
    x_start, y_start = margin, height - margin  # Начальная позиция первой карточки
    
    kanji_positions_per_page = []  # Список для хранения позиций кандзи на страницах
    current_page_positions = []  # Временный список для текущей страницы
    row, col = 0, 0  # Счетчики строк и колонок
    
    # --- Первый лист: Кандзи ---
    for i, word in enumerate(words):
        x_pos = x_start + col * card_width  # Координата X текущей карточки
        y_pos = y_start - (row + 1) * card_height  # Координата Y текущей карточки
        current_page_positions.append((x_pos, y_pos, word))
        
        c.rect(x_pos, y_pos, card_width, card_height)  # Рисуем границы карточки

        c.setFillColor(lime)  # Цвет текста (сверху карточки)    
        c.setFont("JapaneseFont", 8)  # Мелкий текст сверху карточки
        c.drawCentredString(x_pos + card_width / 1.3, y_pos + card_height / 1.2, f"{name}-unit")
        
        c.setFillColor(red)  # Цвет текста (кандзи)
        if len(word['word']) >= 5:
            c.setFont("JapaneseFont", 25)
        else:
            c.setFont("JapaneseFont", 35)
        c.drawCentredString(x_pos + card_width / 2, y_pos + card_height / 2.5, word["word"])  # Рисуем кандзи
        
        # Перемещаемся к следующей карточке
        col += 1
        if col >= cards_per_row:
            col = 0
            row += 1
        if row >= cards_per_col:
            kanji_positions_per_page.append(current_page_positions)
            current_page_positions = []
            c.showPage()  # Создаем новую страницу
            row, col = 0, 0
    
    if current_page_positions:
        kanji_positions_per_page.append(current_page_positions)  # Сохраняем последнюю страницу
    c.showPage()
    
    # --- Второй лист: Чтение и перевод (зеркально по X) ---
    for page_positions in kanji_positions_per_page:
        for (x_pos, y_pos, word) in page_positions:
            mirrored_x_pos = width - x_pos - card_width  # Отражаем координату X
            
            # TODO: Нарисовать границы карточки, если нужно
            # c.rect(mirrored_x_pos, y_pos, card_width, card_height)
            
            c.setFillColor(red)  # Цвет текста
            c.setFont("JapaneseFont", 20)  # Устанавливаем шрифт для чтения
            c.drawCentredString(mirrored_x_pos + card_width / 2, y_pos + card_height / 1.8, word["reading"])
            
            c.setFillColor(black)
            c.setFont("JapaneseFont", 12)
            translation_lines = wrap_text(word["translation"], card_width - 10, "JapaneseFont", 12, c)
            
            line_y = y_pos + card_height - 85  # Начальная позиция перевода
            for line in translation_lines:
                c.drawCentredString(mirrored_x_pos + card_width / 2, line_y, line)
                line_y -= 15  # Смещаемся вниз для следующей строки
        c.showPage()
    
    c.save()  # Сохраняем PDF
    print(f"Файл {name}-dars создан!")


if __name__ == "__main__":
    font_path = "files/yumin.ttf"  # TODO: Убедиться, что шрифт доступен
    json_path = "files/words.json"  # Путь к JSON-файлу со словами
    
    words, name = load_words(json_path)  # Загружаем слова и название урока
    pdf_filename = f"output/{name}-dars.pdf"  # Формируем имя выходного файла
    
    create_flashcards_pdf(words, name, pdf_filename, font_path)  # Генерируем PDF
