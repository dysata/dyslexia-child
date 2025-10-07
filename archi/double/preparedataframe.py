from typing import List
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
import nltk
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from datasets import load_dataset, concatenate_datasets,DatasetDict
import librosa.display
import pandas as pd
import numpy as np

import glob  
from GPUtil import showUtilization as gpu_usage

# load model and tokenizer
processor = Wav2Vec2Processor.from_pretrained("dysata/Wav2Vec2-Ru-Child")
modelcpu = Wav2Vec2ForCTC.from_pretrained("dysata/Wav2Vec2-Ru-Child")
import torch.nn as nn
modelgpu= nn.DataParallel(modelcpu)
device = "cuda"
modelgpu     = modelgpu.to(device)
gpu_usage()


def get_trellis(emission: np.ndarray, tokens_ids: List[int],
                blank_id: int = 0) -> np.ndarray:
    assert isinstance(emission, np.ndarray)
    assert len(emission.shape) == 2
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
@dataclass
class Point:
    token_index: int
    time_index: int
    score: float


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
    #else:
    #    raise ValueError("Failed to align")
    return path[::-1]
def plot_trellis_with_path(trellis: np.ndarray, path: List[Point]):
    trellis_with_path = trellis.copy()
    for _, p in enumerate(path):
        trellis_with_path[p.time_index, p.token_index] = float("nan")
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


def merge_repeats(path: List[Point], tokenized: List[str]) -> List[Segment]:
    i1, i2 = 0, 0
    segments = []
    while i1 < len(path):
        while i2 < len(path) and path[i1].token_index == path[i2].token_index:
            i2 += 1
        score = sum(path[k].score for k in range(i1, i2)) / (i2 - i1)
        segments.append(
            Segment(
                tokenized[path[i1].token_index],
                path[i1].time_index,
                path[i2 - 1].time_index + 1,
                score,
            )
        )
        i1 = i2
    return segments


sounds_in_batch = [cur["array"] for cur in ds["audio"]]
true_texts_in_batch = [
    ' '.join(
        list(filter(lambda it: it.isalpha(), nltk.wordpunct_tokenize(cur)))
    ).lower().replace('¸', 'å').replace('r', 'ğ')
    for cur in ds["text"]
]




colran=range(1024)
collist=list(colran)
collistfull=collist
collistfull.append('label')
collistfull.append('score')
q=pd.DataFrame(columns=collistfull)

for each in range(1):
# tokenize
    processed = processor(sounds_in_batch, sampling_rate=16_000,
                      return_tensors="pt", padding="longest")
    with torch.no_grad():
        ts = modelgpu(processed.input_values.cuda(), attention_mask=processed.attention_mask.cuda(), output_hidden_states=True,return_dict=True)

    last_hidden_state = ts.hidden_states[-1].cpu() 

    logits = ts.logits.cpu()
   
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    feat_extract_output_lengths = modelcpu._get_feat_extract_output_lengths(processed.attention_mask.sum(dim=1)).numpy()
    emission_matrices = []
    for sample_idx in range(feat_extract_output_lengths.shape[0]):
        specgram_len = feat_extract_output_lengths[sample_idx]
        new_emission_matrix = torch.log_softmax(
            logits[sample_idx, 0:specgram_len],
            dim=-1
        ).numpy()
        assert len(new_emission_matrix.shape) == 2
        assert new_emission_matrix.shape[0] == specgram_len
        emission_matrices.append(new_emission_matrix)

    with processor.as_target_processor():
        processedtxt = processor(text=true_texts_in_batch,text_target=true_texts_in_batch)
    labels_ = processedtxt.input_ids    
    labels = []
    for sample_idx in range(len(labels_)):
        new_label_list = []
        for token_idx in range(len(labels_[sample_idx])):
            if labels_[sample_idx][token_idx] < 0:
                break
            new_label_list.append(int(labels_[sample_idx][token_idx]))
        labels.append(new_label_list)
        del new_label_list
    del labels_
       

    for sample_idx, ids in enumerate(labels):
        tokens = processor.tokenizer.convert_ids_to_tokens(ids, skip_special_tokens=False)
        trellis = get_trellis(emission_matrices[sample_idx], labels[sample_idx])
        path = backtrack(trellis, emission_matrices[sample_idx], labels[sample_idx])
        segments = merge_repeats(
            path=path,
            tokenized=processor.tokenizer.convert_ids_to_tokens(
                labels[sample_idx],
                skip_special_tokens=False
            )
        )
        for index in range(len(segments)):
            if segments[index].label=='ğ':
                for tmpi in range(segments[index].start,segments[index].end):
                    tmp=pd.DataFrame(tm01.reshape(1,-1),columns=list(range(1024)))
                    tmp['score']=segments[index].score
                    tmp['label']=segments[index].label
                    q=pd.concat([q, tmp], ignore_index=True)
q.to_parquet('dfname.parquet.gzip', compression='gzip')
#pd.read_parquet('dfname.parquet.gzip')