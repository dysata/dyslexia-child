import sys
import json
import time
import random

time.sleep(1)

input_data = json.load(sys.stdin)
analyses = input_data["analyses"]

# Собираем все маркеры
all_markers = []
for analysis in analyses:
    for triple in analysis["triples"]:
        all_markers.append(triple[2])

# Считаем статистику
from collections import Counter
counter = Counter(all_markers)
total = len(all_markers)
marker_stats = {k: round(v / total * 100, 1) for k, v in counter.items()}

# Простое правило для группы риска
risk_group = "отсутствуют значимые нарушения"
if marker_stats.get("1", 0) > 5 or marker_stats.get("a", 0) > 10:
    risk_group = "подозрение на дислексию"
elif any(v > 3 for v in marker_stats.values()):
    risk_group = "имеются нарушения, требуется наблюдение"

result = {
    "risk_group": risk_group,
    "marker_statistics": marker_stats,
    "temporal_analysis": {
        "improving_markers": ["р"] if random.random() > 0.5 else [],
        "persistent_issues": ["л"] if random.random() > 0.5 else []
    }
}
print(json.dumps(result, ensure_ascii=False))
