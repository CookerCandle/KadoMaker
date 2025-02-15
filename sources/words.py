import json

def load_words(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    name = str(data[0]['dars'])
    words = []
    for lesson in data:
        for word in lesson["so'zlar"]:
            words.append({
                "word": word["kana"],
                "reading": word["jp"],
                "translation": word["uzb"]
            })
    return words, name