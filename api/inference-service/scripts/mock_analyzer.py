import sys
import json
import time
import random

# Имитация долгой работы
time.sleep(2)

text_path = sys.argv[1]
audio_path = sys.argv[2]

# Простая заглушка: генерируем тройки
triples = []
with open(text_path, 'r', encoding='utf-8') as f:
    text = f.read().strip()
    for char in text[:20]:  # только первые 20 символов
        expected = char if char.isalpha() else "|"
        recognized = expected if random.random() > 0.2 else ("|" if expected != "|" else "a")
        marker = "0" if expected == recognized else random.choice("123456789abcdef"[:10])
        triples.append([expected, recognized, marker])

result = {
    "triples": triples
}
print(json.dumps(result, ensure_ascii=False))
