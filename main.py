import os
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.lib.colors import black
from reportlab.pdfgen import canvas

from typing import Literal, Iterable

from sources.fonts import load_font
from sources.json_reader import load_words


def _draw_kanji_side(c, page_positions, lesson, card_width, card_height):
    """Рисует лицевую сторону (кандзи) для одной страницы."""
    for x_pos, y_pos, word in page_positions:
        c.rect(x_pos, y_pos, card_width, card_height)

        c.setFillColor(black)
        c.setFont("JapaneseFont", 8)
        c.drawRightString(
            x_pos + card_width * 0.9,
            y_pos + card_height * 0.83,
            f"第{lesson}課"
        )

        word_len = len(word["word"])
        if word_len <= 4:
            font_size = 40
        elif word_len <= 5:
            font_size = 35
        else:
            font_size = max(20, int(150 / word_len))
        c.setFont("JapaneseFont", font_size)
        c.drawCentredString(
            x_pos + card_width / 2,
            y_pos + card_height / 2 - font_size / 4,
            word["word"]
        )


def _draw_translation_side(c, page_positions, width, card_width, card_height):
    """Рисует обратную сторону (чтение + перевод) для одной страницы."""
    for x_pos, y_pos, word in page_positions:
        mirrored_x_pos = width - x_pos - card_width

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

        translations = list(word["translation"].values())
        if translations:
            font_size = 14
            max_text_width = max(
                c.stringWidth(t, "TranslateFont", font_size) for t in translations
            )
            while max_text_width > card_width - 10 and font_size > 8:
                font_size -= 1
                max_text_width = max(
                    c.stringWidth(t, "TranslateFont", font_size) for t in translations
                )

            c.setFont("TranslateFont", font_size)

            total_height = len(translations) * (font_size + 2)
            start_y = y_pos + card_height * 0.35 + total_height / 2

            for i, line in enumerate(translations):
                c.drawCentredString(
                    mirrored_x_pos + card_width / 2,
                    start_y - i * (font_size + 2),
                    line
                )


def create_flashcards_pdf(
    json_path: str,
    lessons: list,
    font_path_jp: str = "files/yumin.ttf",
    font_path_tr: str = "files/NotoSans.ttf",
    langs: Iterable[str] = ("uz", "en", "ru"),
    orientation: Literal["portrait", "landscape"] = "landscape",
) -> None:
    """
    Создает PDF-файл с карточками для изучения японских слов.
    Страницы идут парами: нечетная — лицо (кандзи), четная — оборот
    (чтение + перевод), для удобной дуплексной печати без сортировки листов.
    """
    if orientation == "portrait":
        width, height = portrait(A4)
        cards_per_row, cards_per_col = 3, 6
    elif orientation == "landscape":
        width, height = landscape(A4)
        cards_per_row, cards_per_col = 4, 4
    else:
        raise ValueError("Orientation must be 'portrait' or 'landscape'")

    os.makedirs("output", exist_ok=True)

    words = load_words(json_path, lessons, langs)
    if not words:
        raise ValueError("No words found for the specified lessons.")

    load_font("JapaneseFont", font_path_jp)
    load_font("TranslateFont", font_path_tr)

    for lesson in lessons:
        pdf_filename = f"output/{lesson}-dars_{orientation}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=(width, height))
        margin = 40

        card_width = (width - 2 * margin) / cards_per_row
        card_height = (height - 2 * margin) / cards_per_col
        x_start, y_start = margin, height - margin

        lesson_words = [w for w in words if w.get("lesson") == lesson]

        current_page_positions = []
        row, col = 0, 0

        def flush_page():
            """Рисует лицо + оборот текущей страницы и переходит к следующей."""
            if not current_page_positions:
                return
            _draw_kanji_side(c, current_page_positions, lesson, card_width, card_height)
            c.showPage()  # конец нечетной (лицевой) страницы
            _draw_translation_side(c, current_page_positions, width, card_width, card_height)
            c.showPage()  # конец четной (обратной) страницы

        for word in lesson_words:
            x_pos = x_start + col * card_width
            y_pos = y_start - (row + 1) * card_height
            current_page_positions.append((x_pos, y_pos, word))

            col += 1
            if col >= cards_per_row:
                col = 0
                row += 1
            if row >= cards_per_col:
                flush_page()
                current_page_positions = []
                row, col = 0, 0

        # последняя, возможно неполная страница
        flush_page()

        c.save()
        print(f"Файл {pdf_filename} создан!")


if __name__ == "__main__":
    create_flashcards_pdf(
        json_path="files/kanjiN2.json",
        lessons=list(range(1, 16)),
        langs=["uz", "ru"],
    )