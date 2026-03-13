#!/usr/bin/env python3
"""
Dysmark Transcriber and Aligner
================================
This module performs speech recognition and error analysis by:
1. Transcribes audio using wav2vec2 model
2. Aligns the transcription with a reference text using forced alignment
3. Marks discrepancies between reference and hypothesis with error codes ("marks")
4. Remapping reference segments to match hypothesis timing (improved alignment)

Library Usage:
from dysmark import get_markers
triples = get_markers(reference_text="hello world", audio_path="audio.wav")

CLI Usage:
# Simple mode (2 positional args)
python3 dysmark.py text.txt audio.wav
# Directory mode (flags)
python3 dysmark.py -a <audio_dir> -t <reference_text_file> -o <output_base>
"""

import sys
import os
import json
import re
import csv
import argparse
from typing import List, Tuple, Any, Optional

import model as alignment
import marks

# =============================================================================
# Configuration
# =============================================================================
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

MODEL_PROC_PATH = "dysata/Wav2Vec2-Ru-Child"
MODEL_PATH = "dysata/Wav2Vec2-Ru-Child"

# =============================================================================
# Quality Validation Functions
# =============================================================================
import wave

def validate_audio_file(audio_path: str) -> Tuple[bool, Optional[str], Optional[int]]:
    if not audio_path.lower().endswith('.wav'):
        return False, "not a wav file", None

    try:
        with wave.open(audio_path, 'rb') as wav_file:
            actual_sr = wav_file.getframerate()
            if actual_sr < 16000:
                return False, f"SR={actual_sr}, should be 16kHz", actual_sr
            n_frames = wav_file.getnframes()
            if n_frames == 0:
                return False, "empty audio file", actual_sr
            return True, None, actual_sr
    except wave.Error:
        return False, "not a valid audio file", None
    except Exception as e:
        return False, f"audio read error: {str(e)}", None


def calculate_match_quality(triples: List[List[str]]) -> Tuple[float, int, int]:
    total_chars = 0
    matching_chars = 0
    for ref, hyp, mark in triples:
        total_chars += 1
        if ref == hyp:
            matching_chars += 1
    if total_chars == 0:
        return 0.0, 0, 0
    match_percentage = (matching_chars / total_chars) * 100
    return match_percentage, total_chars, matching_chars


def create_quality_error_output(problem: str, quality: str = "bad") -> List[List[str]]:
    return [[f"__quality__", problem, "0"]]


# =============================================================================
# Global Model Singleton
# =============================================================================
_model_cache = {
    "processor": None,
    "model": None
}


def _load_model_cached():
    if _model_cache["processor"] is None or _model_cache["model"] is None:
        sys.stderr.write("Loading model (first use)...\n")
        processor, model = alignment.load_model(MODEL_PROC_PATH, MODEL_PATH)
        _model_cache["processor"] = processor
        _model_cache["model"] = model
        sys.stderr.write("Model loaded.\n")
    return _model_cache["processor"], _model_cache["model"]


def clear_model_cache():
    _model_cache["processor"] = None
    _model_cache["model"] = None


# =============================================================================
# Error Marking
# =============================================================================
def _apply_error_marks(segments, points, last_hidden_state):
    segments = marks.markK(segments)
    segments = marks.mark7(segments)
    segments = marks.mark1(segments)
    segments = marks.mark2(segments)
    segments = marks.mark3(segments)
    segments = marks.mark4(segments)
    segments = marks.mark5(segments)
    segments = marks.mark6(segments)
    segments = marks.mark8(segments)
    segments = marks.mark9(segments)
    segments = marks.markJ(segments)
    segments = marks.markA(segments)
    segments = marks.markB(segments)
    segments = marks.markL(segments)
    segments = marks.markD(segments)
    segments = marks.markG(segments)
    segments = marks.markF(segments)
    segments = marks.markC(segments)
    segments = marks.markE(segments)
    segments = marks.markI(segments, points, last_hidden_state)
    segments = marks.mark0(segments)


    return segments


def _format_output_data(segments):
    output_data = []
    for seg in segments:
        mark = seg.mark if seg.mark else "0"
        output_data.append([seg.labelt1, seg.labelf2, mark])
    return output_data


# =============================================================================
# Core Processing
# =============================================================================
def _process_audio_text_pair(reference_text, audio_path, processor, model):
    segments2, points, last_hidden_state = \
        alignment.process_audio(reference_text, audio_path, processor, model)

    marked_segments = _apply_error_marks(segments2, points, last_hidden_state)
    output_data = _format_output_data(marked_segments)
    return output_data


# =============================================================================
# Public Library Interface
# =============================================================================
def get_markers(
    reference_text: str,
    audio_path: str
) -> dict[str, Any]:
    processor, model = _load_model_cached()

    is_valid, problem, actual_sr = validate_audio_file(audio_path)
    if not is_valid:
        return {
            "triples": create_quality_error_output(problem),
            "quality": "bad",
            "problem": problem
        }

    triples = _process_audio_text_pair(
        reference_text, audio_path, processor, model
    )

    match_pct, total, matching = calculate_match_quality(triples)

    if match_pct < 60.0:
        error_pct = 100 - match_pct
        problem = f"more than {error_pct:.0f}% errors"
        return {
            "triples": triples,
            "quality": "bad",
            "problem": problem
        }

    return {
        "triples": triples,
        "quality": "good"
    }


def get_markers_from_file(
    text_path: str,
    audio_path: str
) -> dict[str, Any]:
    if not os.path.exists(text_path):
        return {
            "triples": create_quality_error_output("text file not found"),
            "quality": "bad",
            "problem": "text file not found"
        }
    with open(text_path, 'r', encoding='utf-8') as f:
        reference_text = f.read().strip()
    return get_markers(reference_text, audio_path)

# =============================================================================
# CLI Mode Handlers
# =============================================================================
def run_simple_mode(text_path: str, audio_path: str, processor, model):
    if not os.path.exists(text_path):
        sys.stderr.write(f"Error: Text file not found: {text_path}\n")
        sys.exit(1)
    if not os.path.exists(audio_path):
        sys.stderr.write(f"Error: Audio file not found: {audio_path}\n")
        sys.exit(1)

    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            reference_text = f.read().strip()
        result = get_markers(reference_text, audio_path)
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        sys.stderr.write(f"Processing Error: {str(e)}\n")
        sys.exit(1)


def run_directory_processing_mode(args, processor, model):
    print('Directory transcriber mode')
    src = args.input_name
    if not src or not os.path.isdir(src):
        print(f"Error: Input directory '{src}' is invalid.")
        return

    print(f"Scanning directory: {src}")
    unsortedList = []
    for root, dirs, files in os.walk(src):
        for file in files:
            path = os.path.join(root, file)
            size = os.stat(path).st_size
            if size < 1000000 and ".wav" in file:
                unsortedList.append(os.path.join(root, file))
    print(f'{len(unsortedList)} files found.')

    filein = args.text
    if not filein or not os.path.isfile(filein):
        print(f"Error: Correct file name was not provided with -t option ({filein})")
        return

    text_map = []
    if os.path.exists(filein):
        with open(filein, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t', quotechar='|')
            for row in reader:
                text_map.append(row)
    print(f'Text mapping loaded: {len(text_map)} entries')

    for filename in unsortedList:
        print(f'Processing: {filename}')
        match = re.search(r'\d+\.wav', str(filename))
        segmindex = match.group()[:-4] if match else 0
        argstext = ""
        try:
            argstexttmp = text_map[int(segmindex) - 1]
            argstext = argstexttmp[0]
        except (IndexError, ValueError):
            print(f"Warning: Could not map text for segment {segmindex}")

        argsoutput_name = filename.replace('.wav', '.json')
        output_data = _process_audio_text_pair(
            argstext, filename, processor, model
        )
        with open(argsoutput_name, 'w', encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"Saved: {argsoutput_name}")

    print("Batch processing Done")


# =============================================================================
# Main Entry Point
# =============================================================================
def main():
    if len(sys.argv) == 3 and not any(arg.startswith('-') for arg in sys.argv[1:]):
        text_path = sys.argv[1]
        audio_path = sys.argv[2]
        processor, model = _load_model_cached()
        run_simple_mode(text_path, audio_path, processor, model)
        return

    parser = argparse.ArgumentParser(description='Dysmark Speech Analysis Tool')
    parser.add_argument(
        '-a', '--audio',
        dest='input_name',
        type=str,
        required=False,
        help='Input sound directory.'
    )
    parser.add_argument(
        '-t', '--text',
        dest='text',
        type=str,
        required=False,
        default=None,
        help='Text read.'
    )
    parser.add_argument(
        '-o', '--output',
        dest='output_name',
        type=str,
        required=False,
        help='Output report file name.'
    )
    args = parser.parse_args()

    if not args.input_name:
        parser.error("Directory Processing Mode requires -a/--audio (directory path).")

    processor, model = _load_model_cached()
    run_directory_processing_mode(args, processor, model)


if __name__ == "__main__":
    main()
