#!/usr/bin/env python3
"""
Wav2Vec2 Forced Alignment Module
=================================
This module implements forced alignment between audio emissions and text tokens
using Dynamic Time Warping (DTW) with a trellis-based approach.

Purpose:
- Align reference text to audio time steps using model emission probabilities
- Find the optimal path through the trellis that maximizes alignment score
- Merge repeated tokens into segments with start/end times

Key Concepts:
- Trellis: 2D matrix [time_steps x tokens] storing cumulative alignment scores
- Emission: Log-probabilities from Wav2Vec2 model [time_steps x vocab_size]
- Path: Optimal alignment sequence through the trellis (Viterbi algorithm)
- Segment: Merged consecutive tokens with time boundaries
"""

from typing import List
from dataclasses import dataclass
import numpy as np


# =============================================================================
# Trellis Construction (Dynamic Time Warping Forward Pass)
# =============================================================================

def get_trellis(emission: np.ndarray, tokens_ids: List[int],
                blank_id: int = 0) -> np.ndarray:
    """
    Build a trellis matrix for forced alignment using Dynamic Time Warping.
    
    The trellis stores cumulative log-probability scores for aligning each
    token to each time frame. This is the forward pass of the Viterbi algorithm.
    
    Trellis Structure:
    - Rows: Time frames (0 to num_frame)
    - Columns: Token positions (0 to num_tokens)
    - Cell [t, k]: Best score to align first k tokens to first t frames
    
    At each cell, we consider two transitions:
    1. Stay on same token (emit blank): trellis[t-1, k] + emission[t, blank]
    2. Move to next token (emit token): trellis[t-1, k-1] + emission[t, token]
    
    Args:
        emission: Log-probability matrix [num_frames x vocab_size] from model
        tokens_ids: List of token IDs to align (from reference text)
        blank_id: Token ID for CTC blank token (default: 0)
        
    Returns:
        trellis: 2D array [num_frames+1 x num_tokens+1] with cumulative scores
    """
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


# =============================================================================
# Path Backtracking (Viterbi Backward Pass)
# =============================================================================

@dataclass
class Point:
    """
    Represents a single point in the alignment path.
    """
    token_index: int
    time_index: int
    score: float


def backtrack(trellis: np.ndarray, emission: np.ndarray, tokens_ids: List[int],
              blank_id: int = 0) -> List[Point]:
    """
    Backtrack through the trellis to find the optimal alignment path.
    
    This is the backward pass of the Viterbi algorithm. Starting from the
    best ending position, we trace back through the trellis by choosing
    the transition (stay vs. move) that gave the maximum score at each step.
    
    Args:
        trellis: Cumulative score matrix from get_trellis()
        emission: Original log-probability matrix from model
        tokens_ids: List of token IDs that were aligned
        blank_id: Token ID for CTC blank token (default: 0)
        
    Returns:
        path: List of Point objects representing optimal alignment,
              ordered from start to end (reversed before returning)
    """
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


# =============================================================================
# Segment Creation (Merge Consecutive Tokens)
# =============================================================================

@dataclass
class Segment:
    """
    Represents a time-aligned segment for a single token.
    """
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
    """
    Merge consecutive points with the same token into single segments.
    
    Args:
        path: List of Point objects from backtrack() (chronological order)
        tokenized: List of token strings corresponding to token indices
        
    Returns:
        segments: List of Segment objects with merged time ranges
    """
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


# =============================================================================
# Comparison Segment (For Reference vs Hypothesis Alignment)
# =============================================================================

@dataclass
class Segment2:
    """
    Represents a comparison segment between reference and hypothesis.
    
    Attributes:
        labelt1: Label from reference text (text 1)
        labelf2: Label from model transcription (text 2 / hypothesis)
        mark: Error mark code (populated by marks.py functions)
    """
    labelt1: str
    labelf2: str
    mark: str

    def __repr__(self):
        return f"{self.labelt1} {self.labelf2} {self.mark}"

    @property
    def length(self):
        # Interface compatibility only, Segment2 doesn't track time directly
        return 0
