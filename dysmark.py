from typing import List
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
import nltk
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
import librosa.display
import torch.nn as nn

import pandas as pd

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
@dataclass
class Segment2:
    labelt1: str
    labelf2: str
    mark: str

    def __repr__(self):
        return f"{self.labelt1} {self.labelf2} {self.mark}"

    @property
    def length(self):
        return self.end - self.start

def main():
    parser = ArgumentParser()
    parser.add_argument('-a', '--audio', dest='input_name', type=str, required=True,
                        help='The input sound file name.')
    parser.add_argument('-t', '--text', dest='text', type=str, required=False, default=None,
                        help='The text read.')
    parser.add_argument('-o', '--output', dest='output_name', type=str, required=True,
                        help='The output report file name.')
    args = parser.parse_args()


# load model and tokenizer
   processor = Wav2Vec2Processor.from_pretrained("dysata/Wav2Vec2-Ru-Child")
   model = Wav2Vec2ForCTC.from_pretrained("dysata/Wav2Vec2-Ru-Child")

   aw=args.input_name
   audio, sr = librosa.load(aw, sr=16000)
   true_texts_in_batch=[args.text]
   sounds_in_batch=[audio]
   with torch.no_grad():
    logits = model(processed.input_values, attention_mask=processed.attention_mask).logits
   predicted_ids = torch.argmax(logits, dim=-1)
   transcription = processor.decode(predicted_ids[0])
   feat_extract_output_lengths = model._get_feat_extract_output_lengths(processed.attention_mask.sum(dim=1)).numpy()
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
   trellis = get_trellis(emission_matrices[0], labels[0])
   path = backtrack(trellis, emission_matrices[0], labels[0])
   patht1=path
   tokenst1=processor.tokenizer.convert_ids_to_tokens(
        labels[0],
        skip_special_tokens=False
    )
   segments = merge_repeats(
    path=path,
    tokenized=processor.tokenizer.convert_ids_to_tokens(
        labels[0],
        skip_special_tokens=False
    )
   )
   segmentst1=segments
   true_texts_in_batch=[transcription]
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
   for ids, txt in zip(labels, true_texts_in_batch):
    print(f'ids = {ids}, text = {txt}')
   trellis = get_trellis(emission_matrices[0], labels[0])
   path = backtrack(trellis, emission_matrices[0], labels[0])
   segments = merge_repeats(
    path=path,
    tokenized=processor.tokenizer.convert_ids_to_tokens(
        labels[0],
        skip_special_tokens=False
    )
   )
   tokensf2=processor.tokenizer.convert_ids_to_tokens(
        labels[0],
        skip_special_tokens=False
    )
   pathf2=path
   segmentsf2=segments
   points=[]
   pointst1=[]
   pointsf2=[]
   for i in range(len(segmentst1)):
    pointst1.append(segmentst1[i].start)
   for i in range(len(segmentsf2)):
    pointsf2.append(segmentsf2[i].start)
   points=list(dict.fromkeys(pointst1+pointsf2))
   points.sort()
   wt1='|'
   wf2='|'
   segments2=[]
   for i in points:

    if i in pointst1:
        wt1=segmentst1[pointst1.index(i)  ].label
    if i in pointsf2:
        wf2=segmentsf2[pointsf2.index(i) ].label
#    print(i,wt1,wf2)    
    segments2.append(
            Segment2(wt1,wf2,'')
            )
   for seg in segments2:
    print(seg)        

#parnos
   pairs=['д','т','б','п','з','с','г','к','в','ф']
   pairs2=['т','д','п','б','с','з','к','г','ф','в']


   for i in range(len(segments2)):
#    print(i,segments2[i].labelt1,segments2[i].labelf2)
    if segments2[i].labelf2 != segments2[i].labelt1:
        if segments2[i].labelf2 in pairs:
            if segments2[i].labelt1 == pairs2[ pairs.index(segments2[i].labelf2) ]:
                segments2[i].mark=segments2[i].mark+'1'
#питать жх нпи вз тг рь 
   pairs =['ж','х','н','п','н','и','в','з','т','г','р','ь','о','ю']
   pairs2=['х','ж','п','н','и','н','з','в','г','т','ь','р','ю','о']


   for i in range(len(segments2)):
#    print(i,segments2[i].labelt1,segments2[i].labelf2)
    if segments2[i].labelf2 != segments2[i].labelt1:
        if segments2[i].labelf2 in pairs:
            if segments2[i].labelt1 == pairs2[ pairs.index(segments2[i].labelf2) ]:
                segments2[i].mark=segments2[i].mark+'2'
#М1 3 стечение пропуск согл Скамейка
   sogl=['б','в','г','д','ж','з','к','л','м','н','п','р','с','т','ф','х','ц','ч','ш','щ']
   for i in range(len(segments2)-1): #-2
    if segments2[i].labelf2 != segments2[i].labelt1:
        if segments2[i].labelf2 == '|':
            if segments2[i+1].labelf2 in sogl:
                if segments2[i].labelf2 != segments2[i+1].labelf2:
                    segments2[i].mark=segments2[i].mark+'3'
# gpovtor
   for i in range(len(segments2)-1): #-2
    if segments2[i].labelf2 != segments2[i].labelt1:
        if segments2[i].labelf2 != segments2[i+1].labelf2:
            if segments2[i+1].labelf2 == '|':
                if segments2[i+2].labelf2 == segments2[i].labelf2:
                    segments2[i].mark=segments2[i].mark+'4'
#пропуск гласной м/у согл
   sogl=['б','в','г','д','ж','з','к','л','м','н','п','р','с','т','ф','х','ц','ч','ш','щ']
   vogel=['а','е','и','о','у','э','ю','я','ы']
   for i in range(len(segments2)-1): #-2
    if segments2[i].labelf2 != segments2[i].labelt1:
        if segments2[i].labelt1 in vogel:
            if segments2[i].labelf2 in sogl:
             if segments2[i-1].labelt1 in sogl:
                    segments2[i].mark=segments2[i].mark+'5'
        
#произвольная замена
   for i in range(len(segments2)): #-2
    if segments2[i].labelf2 != segments2[i].labelt1:
        if not segments2[i].mark:
            if i>0:
                if segments2[i].labelf2 == segments2[i-1].labelf2:
                    segments2[i].mark=segments2[i].mark+'9'
                else:
                    segments2[i].mark=segments2[i].mark+'6'
            else:        
                    segments2[i].mark=segments2[i].mark+'6'
#произвольная замена

   for i in range(len(segments2)-1): #-2
    if segments2[i].labelf2 != segments2[i].labelt1 and segments2[i].labelf2 in vogel and segments2[i].labelt1 in vogel:
        j=i
        print(j)
        for j in range (i+1,len(segments2)):
            if segments2[j].labelf2 == segments2[i].labelt1: 
              if segments2[j].labelt1 == segments2[i].labelf2:  
                segments2[i].mark=segments2[i].mark+'7'
                segments2[j].mark=segments2[j].mark+'7'

   for i in range(len(segments2)-1): #-2
    if segments2[i].labelf2 != segments2[i].labelt1 and segments2[i].labelf2 in sogl and segments2[i].labelt1 in sogl:
        j=i
        print(j)
        for j in range (i+1,len(segments2)):
            if segments2[j].labelf2 == segments2[i].labelt1: 
              if segments2[j].labelt1 == segments2[i].labelf2:  
                segments2[i].mark=segments2[i].mark+'8'
                segments2[j].mark=segments2[j].mark+'8'
   Scsvfile = open(args.output_name, 'a', newline='')
   Swriter = csv.writer(Scsvfile, delimiter=' ',quotechar='|', quoting=csv.QUOTE_MINIMAL)
   for seg in segments2:
      Swriter.writerow([seg])
   Scsvfile.close()
    
    
















