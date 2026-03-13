"""
Ремаппинг временных позиций t1 на совпадающие слова в f2.
Сохраняет порядок слов эталона (t1).
"""
import w2vtransf as w2vtr


def remap_t1_to_rightmost(segmentst1, segmentsf2):
    """
    Переставляет временные позиции segmentst1 на совпадающее слово в segmentsf2.
    Выбирает самое правое совпадение, но НЕ нарушает порядок слов t1.
    Также ремаппирует разделители '|' на ближайший '|' в f2 после совпавшего слова.
    """
    t1_labels = [s.label for s in segmentst1]
    f2_labels = [s.label for s in segmentsf2]

    def get_words(labels):
        words = []
        i = 0
        while i < len(labels):
            if labels[i] == '|':
                i += 1
            else:
                j = i
                while j < len(labels) and labels[j] != '|':
                    j += 1
                words.append((i, j))
                i = j
        return words

    t1_words = get_words(t1_labels)
    f2_words = get_words(f2_labels)
    f2_bars = [i for i, l in enumerate(f2_labels) if l == '|']

    new_segs = list(segmentst1)
    word_to_f2_end = {}
    extra_segs = []

    # 1) Собираем все совпадения для каждого слова t1
    all_matches = []
    for t1_s, t1_e in t1_words:
        t1_word = t1_labels[t1_s:t1_e]
        n = t1_e - t1_s
        matches = []
        for f2_s, f2_e in f2_words:
            f2_word = f2_labels[f2_s:f2_e]
            if f2_word == t1_word:
                matches.append((f2_s, f2_e, 'exact'))
            elif len(f2_word) > n and f2_word[:n] == t1_word:
                matches.append((f2_s, f2_e, 'prefix'))
        all_matches.append(matches)

    # 2) Назначаем совпадения справа налево, сохраняя порядок по времени
    #    upper_bound_time — верхняя граница: новое совпадение должно быть раньше
    assigned = [None] * len(t1_words)
    upper_bound_time = float('inf')

    for wi in range(len(t1_words) - 1, -1, -1):
        t1_s, t1_e = t1_words[wi]
        best = None
        for f2_s, f2_e, match_type in all_matches[wi]:
            f2_start_time = segmentsf2[f2_s].start
            if f2_start_time < upper_bound_time:
                if best is None or f2_start_time > best[3]:
                    best = (f2_s, f2_e, match_type, f2_start_time)
        if best is not None:
            assigned[wi] = (best[0], best[1], best[2])
            upper_bound_time = best[3]
        else:
            # Нет подходящего совпадения — используем оригинальное время t1
            upper_bound_time = min(upper_bound_time, segmentst1[t1_s].start)

    # 3) Применяем назначения
    for wi, (t1_s, t1_e) in enumerate(t1_words):
        if assigned[wi] is None:
            continue
        f2_s, f2_e, match_type = assigned[wi]
        n = t1_e - t1_s
        for k in range(n):
            new_segs[t1_s + k] = w2vtr.Segment(
                segmentst1[t1_s + k].label,
                segmentsf2[f2_s + k].start,
                segmentsf2[f2_s + k].end,
                segmentst1[t1_s + k].score
            )
        word_to_f2_end[wi] = f2_s + n
        if match_type == 'prefix':
            for k in range(n, f2_e - f2_s):
                extra_segs.append(w2vtr.Segment(
                    '|',
                    segmentsf2[f2_s + k].start,
                    segmentsf2[f2_s + k].end,
                    0.0
                ))

    # 4) Ремаппинг '|' в t1: на первый '|' в f2 после совпавшего слова
    for i, label in enumerate(t1_labels):
        if label != '|':
            continue
        prev_word_idx = None
        for word_idx, (t1_s, t1_e) in enumerate(t1_words):
            if t1_e <= i:
                prev_word_idx = word_idx
        if prev_word_idx is not None and prev_word_idx in word_to_f2_end:
            f2_after = word_to_f2_end[prev_word_idx]
            for f2_bar_idx in f2_bars:
                if f2_bar_idx >= f2_after:
                    new_segs[i] = w2vtr.Segment(
                        '|',
                        segmentsf2[f2_bar_idx].start,
                        segmentsf2[f2_bar_idx].end,
                        segmentst1[i].score
                    )
                    break

    return new_segs + extra_segs
