from typing import List
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import numpy as np
from dataclasses import dataclass
import librosa
import pandas as pd
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Загрузка модели
processor = Wav2Vec2Processor.from_pretrained("model0proc")
model = Wav2Vec2ForCTC.from_pretrained("model7m")
device = "cpu"
model = model.to(device)
model.eval()

vocab = processor.tokenizer.get_vocab()
r_token_id = vocab['р']


@dataclass
class Point:
    token_index: int
    time_index: int
    score: float


@dataclass
class Segment:
    label: str
    start: int
    end: int
    score: float

    def __repr__(self):
        return f"{self.label}\t({self.score:4.2f}): [{self.start:5d}, {self.end:5d})"

    @property
    def length(self):
        return self.end - self.start


def get_trellis(emission: np.ndarray, tokens_ids: List[int],
                blank_id: int = 0) -> np.ndarray:
    num_frame = emission.shape[0]
    num_tokens = len(tokens_ids)
    trellis = np.empty((num_frame + 1, num_tokens + 1), dtype=np.float64)
    trellis[0, 0] = 0
    trellis[1:, 0] = np.cumsum(emission[:, 0], 0)
    trellis[0, -num_tokens:] = -float("inf")
    trellis[-num_tokens:, 0] = float("inf")
    for t in range(num_frame):
        trellis[t + 1, 1:] = np.maximum(
            trellis[t, 1:] + emission[t, blank_id],
            trellis[t, :-1] + emission[t, tokens_ids]
        )
    return trellis


def backtrack(trellis: np.ndarray, emission: np.ndarray, tokens_ids: List[int],
              blank_id: int = 0) -> List[Point]:
    j = trellis.shape[1] - 1
    t_start = np.argmax(trellis[:, j])
    path = []
    for t in range(t_start, 0, -1):
        stayed = trellis[t - 1, j] + emission[t - 1, blank_id]
        changed = trellis[t - 1, j - 1] + emission[t - 1, tokens_ids[j - 1]]
        prob = np.exp(emission[t - 1, tokens_ids[j - 1] if changed > stayed else 0])
        path.append(Point(j - 1, t - 1, prob))
        if changed > stayed:
            j -= 1
            if j == 0:
                break
    return path[::-1]


def merge_repeats(path: List[Point], tokenized: List[str]) -> List[Segment]:
    i1, i2 = 0, 0
    segments = []
    while i1 < len(path):
        while i2 < len(path) and path[i1].token_index == path[i2].token_index:
            i2 += 1
        score = sum(path[k].score for k in range(i1, i2)) / (i2 - i1)
        segments.append(Segment(
            tokenized[path[i1].token_index],
            path[i1].time_index,
            path[i2 - 1].time_index + 1,
            score,
        ))
        i1 = i2
    return segments


def process_dir(audio_dir, label_a):
    """Обрабатывает каталог: извлекает hidden states фреймов 'р' из каждого wav."""
    rows = []
    search = f'{audio_dir}/*.wav'
    files = sorted(glob.glob(search))
    print(f"Каталог {audio_dir}: {len(files)} файлов, a={label_a}")

    for filepath in files:
        audio, sr = librosa.load(filepath, sr=16000)

        # Текст из имени файла: от последнего '_' до '.'
        basename = filepath.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
        text = basename.rsplit('.', 1)[0].rsplit('_', 1)[-1].lower().replace('ё', 'е')

        inputs = processor(audio, return_tensors="pt", sampling_rate=16000, padding="longest")
        with torch.no_grad():
            ts = model(inputs.input_values.to(device),
                       attention_mask=inputs.attention_mask.to(device),
                       output_hidden_states=True, return_dict=True)

        logits = ts.logits.cpu()
        last_hidden_state = ts.hidden_states[-1].cpu()
        specgram_len = model._get_feat_extract_output_lengths(
            inputs.attention_mask.sum(dim=1)
        ).numpy()[0]

        emission = torch.log_softmax(logits[0, :specgram_len], dim=-1).numpy()

        # softmax вероятность "р" на каждом фрейме
        probs = torch.softmax(logits[0, :specgram_len], dim=-1)
        r_probs = probs[:, r_token_id].numpy()

        with processor.as_target_processor():
            processedtxt = processor(text=text, text_target=text)
        token_ids = [tid for tid in processedtxt.input_ids if tid >= 0]

        trellis = get_trellis(emission, token_ids)
        path = backtrack(trellis, emission, token_ids)
        segments = merge_repeats(
            path=path,
            tokenized=processor.tokenizer.convert_ids_to_tokens(token_ids, skip_special_tokens=False)
        )

        r_frames = 0
        for seg in segments:
            if seg.label == 'р':
                for tmpi in range(seg.start, seg.end):
                    prob = float(r_probs[tmpi])
                    hs = last_hidden_state[0, tmpi].numpy()
                    row = list(hs) + [prob]
                    rows.append(row)
                    r_frames += 1

        print(f"  {filepath}: {r_frames} фреймов 'р'")

    return rows


# Обработка двух каталогов
good_rows = process_dir('./audio/good', 1)
bad_rows = process_dir('./audio/notgood', 0)

# Формирование DataFrame
columns = list(range(1024)) + ['prob']
rdf = pd.DataFrame(good_rows, columns=columns)
rdf['a'] = 1
bdf = pd.DataFrame(bad_rows, columns=columns)
bdf['a'] = 0

df = pd.concat([rdf, bdf], ignore_index=True)
df.to_parquet('interp_df.parquet.gzip', compression='gzip')
df.head()
print(f"\nИтого: good={len(rdf)}, notgood={len(bdf)}, всего={len(df)}")
print(f"Сохранено: interp_df.parquet.gzip")
