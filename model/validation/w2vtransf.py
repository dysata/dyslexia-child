from typing import List
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
#import nltk
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from dataclasses import dataclass
import librosa#.display
import torch.nn as nn
import sys
#import argparse
#import csv
import os
#import re

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

