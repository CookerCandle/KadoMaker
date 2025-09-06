import json

def load_words(json_path: str, lessons: list, langs: list) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    words = []
    for lesson in data:
        if lesson['lesson'] in lessons:
            for word in lesson["data"]:
                words.append({
                    "lesson": lesson['lesson'],
                    "word": word["kanji"],
                    "reading": word["jp"],
                    "translation": {lang: word[lang] for lang in langs if lang in word}
                })
    return words

# print(load_words("files/kanjiN3.json", [1, 2], ["uz", "en", "ru"]))