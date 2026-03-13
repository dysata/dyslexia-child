"""
Модуль выравнивания: wav2vec2 forced alignment + remap.

Копия модельного кода из оригинального dysmarkcclsjson.py.

Экспортирует:
  - load_model(proc_path, model_path) -> (processor, model)
  - process_audio(reference_text, audio_path, processor, model)
      -> (comparison_segments, points, last_hidden_state)
"""
import torch
import numpy as np
import librosa

from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

import w2vtransf as w2vtr
from w2vtransf import Segment2
from remap import remap_t1_to_rightmost

SAMPLING_RATE = 16000


def load_model(proc_path, model_path):
    processor = Wav2Vec2Processor.from_pretrained(proc_path)
    model = Wav2Vec2ForCTC.from_pretrained(model_path)
    return processor, model


def process_audio(reference_text, audio_path, processor, model):
    """
    Загрузка аудио, получение emission, forced alignment для t1 и f2,
    remap, построение comparison_segments.

    Returns:
        (comparison_segments, points, last_hidden_state)
    """
    audio, sr = librosa.load(audio_path, sr=SAMPLING_RATE)
    sounds_in_batch = [audio]

    processed = processor(sounds_in_batch, sampling_rate=16_000,
                          return_tensors="pt", padding="longest")

    with torch.no_grad():
        outputs = model(processed.input_values,
                        attention_mask=processed.attention_mask,
                        output_hidden_states=True, return_dict=True)
        logits = outputs.logits
        last_hidden_state = outputs.hidden_states[-1].cpu()
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.decode(predicted_ids[0])
    feat_extract_output_lengths = model._get_feat_extract_output_lengths(
        processed.attention_mask.sum(dim=1)
    ).numpy()
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

    def _align_text(text_list):
        with processor.as_target_processor():
            processedtxt = processor(text=text_list, text_target=text_list)
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
        trellis = w2vtr.get_trellis(emission_matrices[0], labels[0])
        path = w2vtr.backtrack(trellis, emission_matrices[0], labels[0])
        tokens = processor.tokenizer.convert_ids_to_tokens(
            labels[0],
            skip_special_tokens=False
        )
        segments = w2vtr.merge_repeats(
            path=path,
            tokenized=tokens
        )
        return segments, labels, path, tokens

    segmentst1, _, patht1, tokenst1 = _align_text([reference_text])

    segmentsf2, labels, pathf2, tokensf2 = _align_text([transcription])

    segmentst1 = [s for s in segmentst1 if s.label != '<unk>']
    segmentsf2 = [s for s in segmentsf2 if s.label != '<unk>']
    segmentst1 = remap_t1_to_rightmost(segmentst1, segmentsf2)

    # Построение comparison
    pointst1 = []
    pointsf2 = []
    for i in range(len(segmentst1)):
        pointst1.append(segmentst1[i].start)
    for i in range(len(segmentsf2)):
        pointsf2.append(segmentsf2[i].start)

    points = list(dict.fromkeys(pointst1 + pointsf2))
    points.sort()
    wt1 = '|'
    wf2 = '|'
    segments2 = []
    for i in points:
        if i in pointst1:
            wt1 = segmentst1[pointst1.index(i)].label
        if i in pointsf2:
            wf2 = segmentsf2[pointsf2.index(i)].label
        S2 = Segment2(wt1, wf2, '')
        segments2.append(S2)

    return segments2, points, last_hidden_state
