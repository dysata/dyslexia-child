#!/usr/bin/env python3
import os
"""
Модуль маркировки ошибок распознавания речи
=============================================

Сравнивает эталонный текст (labelt1) с транскрипцией модели (labelf2)
и расставляет маркеры ошибок.

Коды маркеров:
  0 — Нет ошибки
  1 — Парная замена ж/х
  2 — Парная замена н/п, и/н
  3 — Парная замена в/з
  4 — Парная замена т/г
  5 — Парная замена р/ь/б
  6 — Парная замена о/ю
  7 — Замена по звонкости/глухости (с проверкой оглушения)
  8 — Парная замена х/к
  9 — Пропуск согласной на стечении
  A — Удлинение гласной с пропуском согласной
  B — Пропуск гласной между согласными
  C — Произвольная замена (остаточная)
  D — Перестановка гласных
  E — Перестановка согласных
  F — Лишний звук в конце слова
  G — Смягчение окончания (а→я, о→ё, у→ю)
  H — Пропуск с удвоением
  J — Повтор через паузу / лишний префикс
  K — Заикание (серия одинаковых фонем)
  L — Удлинение согласной с пропуском гласной
  R — Некорректное произношение 'р' (классификация CatBoost)

Порядок вызова: K → 7 → 1-6,8 → 9 → J → A → B → L → D → G → F → C → E → R → 0
Маркеры не перезаписываются: если сегмент уже помечен, следующие функции его пропускают.
"""

# Consonant classifications
soglzv = ['б', 'в', 'г', 'д', 'ж', 'з', 'л', 'м', 'н', 'р']  # Voiced consonants
soglgl = ['к', 'п', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш', 'щ']  # Voiceless consonants
sogl = ['б', 'в', 'г', 'д', 'ж', 'з', 'к', 'л', 'м', 'н', 'п', 'р', 'с', 'т', 'ф', 'х', 'ц', 'ч', 'ш', 'щ']  # All consonants
vogel = ['а', 'е', 'и', 'о', 'у', 'э', 'ю', 'я', 'ы']  # Vowels


def mark7(segments2):
    """
    Mark voicing pair substitutions (voiced/voiceless consonant confusion).
    
    Excludes devoicing contexts (voiced→voiceless after vowel, before voiceless)
    as those are normal phonetic variations, not errors.
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated for matching segments
    """
    pairs = [ 'т', 'б', 'п', 'з', 'с', 'г', 'к', 'в', 'ф']
    pairs2 = [ 'д', 'п', 'б', 'с', 'з', 'к', 'г', 'ф', 'в']

    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    # Check for normal devoicing context (not an error)
                    # 1) между гласной и глухой согласной
                    oglushenie = (
                        segments2[i].labelt1 in soglzv and
                        segments2[i].labelf2 in soglgl and
                        i > 0 and i < len(segments2) - 1 and
                        segments2[i - 1].labelt1 in vogel and
                        segments2[i + 1].labelt1 in soglgl
                    )
                    # 2) оглушение в конце слова (перед границей | или концом)
                    if not oglushenie:
                        oglushenie = (
                            segments2[i].labelt1 in soglzv and
                            segments2[i].labelf2 in soglgl and
                            (i == len(segments2) - 1 or segments2[i + 1].labelt1 == '|')
                        )
                    # Only mark if NOT a normal devoicing context
                    if oglushenie:
                        if not segments2[i].mark:
                            segments2[i].mark = '0'  # нормальное оглушение, не ошибка
                    else:
                        if not segments2[i].mark:
                            segments2[i].mark = segments2[i].mark + '7'
    return segments2


def mark1(segments2):
    """
    Mark other consonant pair substitutions.
    
    Pairs: ж/х, 
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    pairs = ['ж', 'х']
    pairs2 = ['х', 'ж']

    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + '1'
    return segments2

def mark2(segments2):
    """
    Mark other consonant pair substitutions.
    
    Pairs:  н/п, и/н
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    pairs  = ['н', 'п', 'н', 'и' ]
    pairs2 = ['п', 'н', 'и', 'н' ]


    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + '2'
    return segments2


def mark3(segments2):
    """
    Mark other consonant pair substitutions.
    
    Pairs:  в/з
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    pairs  = [ 'в', 'з' ]
    pairs2 = ['з',  'в' ]

    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + '3'
    return segments2

def mark4(segments2):
    """
    Mark other consonant pair substitutions.
    
    Pairs:  т/г
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    pairs  = ['т', 'г']
    pairs2 = [ 'г', 'т']


    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + '4'
    return segments2
def mark5(segments2):
    """
    Mark other consonant pair substitutions.
    
    Pairs:  р/ь/б
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    pairs  = [ 'р', 'ь','б','ь','б','р']
    pairs2 = [ 'ь', 'р','ь','б','р','б']


    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + '5'
    return segments2

def mark6(segments2):
    """
    Mark other consonant pair substitutions.
    
    Pairs:  о/ю
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    pairs = [ 'о', 'ю']
    pairs2 = [ 'ю', 'о']


    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + '6'
    return segments2

def mark8(segments2):
    """
    Mark other consonant pair substitutions.
    
    Pairs:  о/ю
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    pairs = [ 'х', 'к']
    pairs2 = [ 'к', 'х']


    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 in pairs:
                if segments2[i].labelt1 == pairs2[pairs.index(segments2[i].labelf2)]:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + '8'
    return segments2


def mark9(segments2):
    """
    Mark consonant cluster issues and deletions.
    
         H pauzy
         9 propusk soglasnoy na stechenii skameyka-kameyka
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(1, len(segments2) - 1):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 == '|':
                if segments2[i - 1].labelt1 == segments2[i - 1].labelf2 and \
                   segments2[i - 1].labelt1 == segments2[i].labelt1:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + 'H'
                else:
                    if segments2[i + 1].labelf2 in sogl  and segments2[i ].labelt1 in sogl:
                        if segments2[i].labelf2 != segments2[i + 1].labelf2:
                            if not segments2[i].mark:
                                segments2[i].mark = segments2[i].mark + '9'
    return segments2


def markJ(segments2):
    """
    Mark repetitions with pauses and word prefix elongation.
    
    '4': Sound repeated with pause between (stuttering pattern)
    '4': Extra phonemes before correct word (child produced extra material)
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(len(segments2) - 1):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelf2 != segments2[i + 1].labelf2:
                if segments2[i + 1].labelf2 == '|':
                    if i + 2 < len(segments2):
                        if segments2[i + 2].labelf2 == segments2[i].labelf2:
                            if not segments2[i].mark:
                                segments2[i].mark = segments2[i].mark + 'J'
        
        # Word prefix elongation: reference has pause, hypothesis has phoneme
        if segments2[i].labelt1 == '|' and (segments2[i].labelf2 in sogl or segments2[i].labelf2 in vogel):
            is_elongation = i > 0 and segments2[i].labelf2 == segments2[i - 1].labelf2
            if not is_elongation and (i == 0 or segments2[i - 1].labelf2 == '|' or segments2[i - 1].labelt1 != '|'):
                if not segments2[i].mark:
                    segments2[i].mark = segments2[i].mark + 'J'
    return segments2


def markB(segments2):
    """
    Mark vowel deletion between consonants.
    
    Pattern: consonant-vowel-consonant → consonant-consonant-consonant
    
    Args:
        segments2: List of Segment2 objects
    #пропуск гласной м/у согл
    
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(len(segments2) - 1):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelt1 in vogel:
                if segments2[i].labelf2 in sogl:
                    if i > 0:
                        if segments2[i - 1].labelt1 in sogl:
                            if not segments2[i].mark:
                                segments2[i].mark = segments2[i].mark + 'B'
    return segments2


def markK(segments2):
    """
    Mark stuttering: series of same phonemes in hypothesis.
    
    Detects when hypothesis has repeated phonemes (e.g., "изззз") and marks
    positions where hypothesis != reference (excluding word boundaries and
    vowel skips which get markC).
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    i = 0
    while i < len(segments2):
        label = segments2[i].labelf2
        if label == '|':
            i += 1
            continue
        j = i + 1
        while j < len(segments2) and segments2[j].labelf2 == label:
            j += 1
        if j - i > 1:
            # Check if at least one position matches (true stuttering)
            has_match = any(segments2[k].labelf2 == segments2[k].labelt1 for k in range(i, j))
            if has_match:
                for k in range(i, j):
                    if segments2[k].labelf2 != segments2[k].labelt1:
                        if segments2[k].labelt1 == '|':  # Word boundary, not stuttering
                            continue
                        if segments2[k].labelt1 in vogel:  # Vowel skip gets markC
                            continue
                        if not segments2[k].mark:
                            segments2[k].mark = segments2[k].mark + 'K'
        i = j
    return segments2


def markL(segments2):
    """
    Mark consonant elongation with vowel skip.
# удлинение согласной с пропуском гласной: t1=гласная, f2=та же согласная что и предыдущая    
    Pattern: reference has vowel, hypothesis has same consonant as previous
    (child held consonant instead of pronouncing vowel).
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(1, len(segments2)):
        if segments2[i].labelt1 in vogel:
            if segments2[i].labelf2 in sogl:
                if segments2[i].labelf2 == segments2[i - 1].labelf2:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + 'L'
    return segments2
def markA(segments2):
    """
    Mark consonant elongation with vowel skip.
# удлинение гласной с пропуском согласной: t1=согласная, f2=та же гласная что и предыдущая    
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(1, len(segments2)):
        if segments2[i].labelt1 in sogl:
            if segments2[i].labelf2 in vogel:
                if segments2[i].labelf2 == segments2[i - 1].labelf2:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + 'A'
    return segments2


def markD(segments2):
    """
    Mark vowel transpositions.
    
    Pattern: Two vowels swapped between positions i and j.
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(len(segments2) - 1):
        if segments2[i].labelf2 != segments2[i].labelt1 and \
           segments2[i].labelf2 in vogel and \
           segments2[i].labelt1 in vogel:
            if not segments2[i].mark:
                for j in range(i + 1, len(segments2)):
                    if segments2[j].labelf2 == segments2[i].labelt1:
                        if segments2[j].labelt1 == segments2[i].labelf2:
                            if not segments2[j].mark:
                                segments2[i].mark = segments2[i].mark + 'D'
                                segments2[j].mark = segments2[j].mark + 'D'
                                
    return segments2


def markC(segments2):
    """
    Mark arbitrary substitutions (catch-all for unmarked errors).
    
    '6': General substitution
    '9': Repeated sound (hypothesis matches previous hypothesis)
    
    Skips word boundaries (already handled by mark4).
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelt1 == '|':
                continue  # Word boundary handled by mark4
            if not segments2[i].mark:
                if i > 0:
                    if segments2[i].labelf2 == segments2[i - 1].labelf2:
                        pass  # Same letter = elongation, no mark
                    else:
                        segments2[i].mark = segments2[i].mark + 'C'
                else:
                    segments2[i].mark = segments2[i].mark + 'C'
    return segments2


def markE(segments2):
    """
    Mark consonant transpositions.
    
    Pattern: Two consonants swapped between positions i and j.
    
    Args:
        segments2: List of Segment2 objects
        
    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(len(segments2) - 1):
        if segments2[i].labelf2 != segments2[i].labelt1 and \
           segments2[i].labelf2 in sogl and \
           segments2[i].labelt1 in sogl:
            if not segments2[i].mark:
                for j in range(i + 1, len(segments2)):
                    if segments2[j].labelf2 == segments2[i].labelt1:
                        if segments2[j].labelt1 == segments2[i].labelf2:
                            if not segments2[j].mark:
                                segments2[i].mark = segments2[i].mark + 'E'
                                segments2[j].mark = segments2[j].mark + 'E'
    return segments2


def markG(segments2):
    """
    Mark softening of final vowel before word boundary.
    # смягчение окончания: последняя гласная в слове заменена на мягкую (а->я, о->ё, у->ю)
    # например оса -> ося

    Args:
        segments2: List of Segment2 objects

    Returns:
        segments2: Same list with .mark updated
    """
    soft_pairs = {'а': 'я', 'о': 'ё', 'у': 'ю'}
    soft_pairs_rev = {v: k for k, v in soft_pairs.items()}
    all_soft = {**soft_pairs, **soft_pairs_rev}

    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelt1 in all_soft and segments2[i].labelf2 == all_soft[segments2[i].labelt1]:
                is_last_before_boundary = (
                    (i + 1 < len(segments2) and segments2[i + 1].labelt1 == '|') or
                    i + 1 == len(segments2)
                )
                if is_last_before_boundary:
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + 'G'
    return segments2


def markF(segments2):
    """
    Mark extra sound added at end of word.

    Pattern: reference has '|' (word boundary), hypothesis has a sound (consonant or vowel),
    and the next segment's reference starts a new word (or end of sequence).
    # добавление лишнего звука в конце слова

    Args:
        segments2: List of Segment2 objects

    Returns:
        segments2: Same list with .mark updated
    """
    for i in range(len(segments2)):
        if segments2[i].labelf2 != segments2[i].labelt1:
            if segments2[i].labelt1 == '|' and segments2[i].labelf2 in sogl + vogel:
                if i > 0 and segments2[i - 1].labelt1 != '|':
                    # Не ставим F если звук — продолжение предыдущего (слияние/протяжка)
                    if i > 0 and (segments2[i - 1].labelt1 == segments2[i].labelf2 or
                                  segments2[i - 1].labelf2 == segments2[i].labelf2):
                        continue
                    if not segments2[i].mark:
                        segments2[i].mark = segments2[i].mark + 'F'
    return segments2


def markR(segments2, points, hidden_states):
    """
    Классификация звука 'р' с помощью CatBoost.
    Если labelt1 == 'р' и CatBoost считает произношение некорректным (a=0),
    ставит маркер 'R'.

    Args:
        segments2: List of Segment2 objects
        points: List of frame indices corresponding to each segment2
        hidden_states: tensor (1, num_frames, 1024) — last hidden state из wav2vec2
    """
    import numpy as np
    from catboost import CatBoostClassifier

    model_path = os.path.join(os.path.dirname(__file__), 'catboost_r_model.cbm')
    if not os.path.exists(model_path):
        print(f"markR: модель не найдена: {model_path}")
        return segments2

    cb_model = CatBoostClassifier()
    cb_model.load_model(model_path)

    for i in range(len(segments2)):
        if segments2[i].labelt1 == 'р':
            frame_idx = points[i]
            # Берём среднее hidden state по фреймам до следующего сегмента
            if i + 1 < len(points):
                end_frame = points[i + 1]
            else:
                end_frame = hidden_states.shape[1]
            hs = hidden_states[0, frame_idx:end_frame].numpy()
            if len(hs) == 0:
                continue
            hs_mean = np.mean(hs, axis=0).reshape(1, -1)
            pred = cb_model.predict(hs_mean)
            print("-----------------------")    
            print(pred)
            if int(pred[0]) == 0:
                segments2[i].mark = 'R'
    return segments2


def mark0(segments2):
    """
    Default/fallback marking function.

    Currently returns segments unchanged. Segments without errors will have
    empty .mark (converted to '0' in format_output_data()).

    Args:
        segments2: List of Segment2 objects

    Returns:
        segments2: Same list, unchanged
    """
    return segments2
