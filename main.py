from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas

from typing import Literal

from sources.fonts import load_font
from sources.json_reader import load_words


def create_flashcards_pdf(
    json_path: str,
    lessons: list,
    font_path_jp: str = "files/yumin.ttf",
    font_path_tr: str = "files/NotoSans.ttf",
    langs: list = ("uz", "en", "ru"),
    color: str = "black",
    orientation: Literal["portrait", "landscape"] = "landscape",
) -> None:
    """
    Создает PDF-файл с карточками для изучения японских слов.
    params: json_path — путь к JSON-файлу с данными,
    params: lessons — список номеров уроков для включения,
    params: font_path_jp — путь к TTF-файлу с японским шрифтом,
    params: font_path_tr — путь к TTF-файлу с шрифтом для перевода,
    params: langs — список языков для перевода (ключи из JSON),
    params: color — цвет текста (по умолчанию черный), 
    params: orientation — ориентация страниц (портрет или ландшафт).
    """
    if orientation == "portrait":
        width, height = portrait(A4)
    elif orientation == "landscape":
        width, height = landscape(A4)
    else:
        raise ValueError("Orientation must be 'portrait' or 'landscape'")

    words = load_words(json_path, lessons, langs)
    if not words:
        raise ValueError("No words found for the specified lessons.")

    for lesson in lessons:
        pdf_filename = f"output/{lesson}-dars_{orientation}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=(width, height))
        load_font("JapaneseFont", font_path_jp)
        load_font("TranslateFont", font_path_tr)
        margin = 40

        match orientation:
            case "portrait":
                cards_per_row, cards_per_col = 3, 6
            case "landscape":
                cards_per_row, cards_per_col = 4, 4

        card_width = (width - 2 * margin) / cards_per_row
        card_height = (height - 2 * margin) / cards_per_col
        x_start, y_start = margin, height - margin

        kanji_positions_per_page = []
        current_page_positions = []
        row, col = 0, 0

        # --- Первый лист: Кандзи ---
        for word in [w for w in words if w.get("lesson") == lesson]:
            x_pos = x_start + col * card_width
            y_pos = y_start - (row + 1) * card_height
            current_page_positions.append((x_pos, y_pos, word))

            # рамка
            c.rect(x_pos, y_pos, card_width, card_height)

            # подпись урока (в правом верхнем углу карточки)
            c.setFillColor(black)
            c.setFont("JapaneseFont", 8)  # используем мелкий шрифт
            c.drawRightString(
                x_pos + card_width / 1.1,  # чуть влево от правого края
                y_pos + card_height / 1.2,  # чуть ниже верхней границы
            f"第{lesson}課" 
            )

            # кандзи
            word_len = len(word["word"])
            if word_len <= 4:
                font_size = 40
            elif word_len <= 5:
                font_size = 35
            else:
                font_size = max(20, int(150 / word_len))  # плавное уменьшение
            c.setFont("JapaneseFont", font_size)
            c.drawCentredString(
                x_pos + card_width / 2,
                y_pos + card_height / 2,
                word["word"]
            )

            col += 1
            if col >= cards_per_row:
                col = 0
                row += 1
            if row >= cards_per_col:
                mirrored_page = []
                for j in range(0, len(current_page_positions), cards_per_row):
                    row_slice = current_page_positions[j:j+cards_per_row]
                    mirrored_page.extend(row_slice[::-1])
                kanji_positions_per_page.append(mirrored_page)

                current_page_positions = []
                c.showPage()
                row, col = 0, 0

        if current_page_positions:
            mirrored_page = []
            for j in range(0, len(current_page_positions), cards_per_row):
                row_slice = current_page_positions[j:j+cards_per_row]
                mirrored_page.extend(row_slice[::-1])
            kanji_positions_per_page.append(mirrored_page)

        c.showPage()

        # --- Второй лист: чтение + перевод ---
        for page_positions in kanji_positions_per_page:
            for (x_pos, y_pos, word) in page_positions:
                mirrored_x_pos = width - x_pos - card_width

                # чтение
                reading_len = len(word["reading"])
                if reading_len <= 8:
                    font_size = 23
                else:
                    font_size = max(12, int(160 / reading_len))
                c.setFont("JapaneseFont", font_size)
                c.drawCentredString(
                    mirrored_x_pos + card_width / 2,
                    y_pos + card_height * 0.65,
                    word["reading"]
                )

                # перевод (каждый язык с новой строки)
                translations = list(word["translation"].values())

                # подбираем шрифт так, чтобы влезло
                font_size = 14
                max_text_width = max(c.stringWidth(t, "TranslateFont", font_size) for t in translations)
                while max_text_width > card_width - 10 and font_size > 8:
                    font_size -= 1
                    max_text_width = max(c.stringWidth(t, "TranslateFont", font_size) for t in translations)

                c.setFont("TranslateFont", font_size)

                # рассчитываем вертикальное выравнивание
                total_height = len(translations) * (font_size + 2)
                start_y = y_pos + card_height * 0.35 + total_height / 2

                for i, line in enumerate(translations):
                    c.drawCentredString(
                        mirrored_x_pos + card_width / 2,
                        start_y - i * (font_size + 2),
                        line
                    )

            c.showPage()

        c.save()
        print(f"Файл {pdf_filename} создан!")

# create_flashcards_pdf(
#     json_path="files/kanjiN3.json",
#     lessons=[1, 2],
#     langs=["uz", "en", "ru"],
# )