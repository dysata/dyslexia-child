#!/usr/bin/env python3
"""
Dysmark Diagnostic Statistics and Classification Tool
======================================================

This module analyzes speech recognition error markers from JSON data and
classifies subjects into risk groups for dyslexia assessment.

Classification Methodology (preserved from original):
- Counts all non-zero markers across all audio samples
- Compares total marker count against thresholds based on total phonemes
- Thresholds: norma = total/30, worry = 3*norma, risk = 0.07*total

Risk Groups:
- 'no risk': Marker count <= norma (no significant issues)
- 'worry about': Marker count <= 0.07*total (some signs, needs monitoring)
- 'risk group': Marker count > 0.07*total (full dyslexia assessment recommended)

Library Usage:
    from statdiag import diagnose
    result = diagnose({"analyses": [{"triples": [...]}]})

CLI Usage:
    # Simple mode (stdin/stdout)
    cat results.json | python3 statdiag.py --stdin

    # Directory mode
    python3 statdiag.py -d <json_directory>
"""

import sys
import os
import json
import math
import argparse
from typing import Dict, List, Any
from collections import Counter


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_DIRECTORY = './marks/hwa123'
OUTPUT_FILE = 'out.json'


# =============================================================================
# Core Statistics and Classification Logic (PRESERVED FROM ORIGINAL)
# =============================================================================

def extract_markers_from_triples(triples: List[List[str]]) -> List[str]:
    """
    Extract all marker codes from a list of triples.
    
    Each triple has format: [reference_char, hypothesis_char, marker]
    We collect all markers that are not "0" (no error).
    
    Args:
        triples: List of [ref, hyp, mark] triples from JSON
        
    Returns:
        List of marker strings (excluding "0")
    """
    markers = []
    for triple in triples:
        if isinstance(triple, list) and len(triple) == 3:
            mark = triple[2]
            if mark != "0":
                markers.append(mark)
    return markers


def compute_marker_statistics(markers: List[str]) -> Dict[str, int]:
    """
    Compute marker frequency statistics.
    
    Args:
        markers: List of all marker codes from all samples
        
    Returns:
        Dictionary mapping marker code -> count
    """
    mark_count = {}
    for mark in markers:
        mark_count[mark] = mark_count.get(mark, 0) + 1
    return mark_count


def classify_risk_group(total_markers: int, total_phonemes: int) -> str:
    """
    Classify subject into risk group based on marker density.
    
    Args:
        total_markers: Total count of non-zero markers
        total_phonemes: Total count of all phonemes analyzed
        
    Returns:
        Risk group string: 'no risk', 'worry about', or 'risk group'
    """
    totalnorma = math.ceil(total_phonemes / 30)
    totalworry = total_phonemes * 0.07
    
    if total_markers <= totalnorma:
        return 'no risk'
    elif total_markers < totalworry:
        return 'worry about'
    else:
        return 'risk group'


def analyze_markers(markers: List[str], total_phonemes: int) -> Dict[str, Any]:
    """
    Perform complete marker analysis and classification.
    
    This is the core function that preserves the original methodology.
    
    Args:
        markers: List of all marker codes from all samples
        total_phonemes: Total count of all phonemes analyzed
        
    Returns:
        Dictionary with marker_statistics, norma, and marker_results
    """
    marker_statistics = compute_marker_statistics(markers)
    total_markers = len(markers)
    marker_results = classify_risk_group(total_markers, total_phonemes)
    norma = math.ceil(total_phonemes / 30)
    
    result = {
        "total_phonemes": total_phonemes,
        "total_markers": total_markers,
        "marker_statistics": marker_statistics,
        "norma": norma,
        "risk_group": marker_results
    }
    
    return result


# =============================================================================
# Public Library Interface (NEW)
# =============================================================================

def diagnose(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main library function: Analyze markers and classify risk group.
    
    This is the primary interface for using statdiag.py as a library module.
    It accepts an analyses object and returns diagnostic results.
    
    Args:
        input_data: Dictionary with "analyses" key containing list of analyses.
                   Each analysis should have "triples" array.
                   Format:
                   {
                       "analyses": [
                           {
                               "triples": [["ref", "hyp", "mark"], ...]
                           },
                           ...
                       ]
                   }
    
    Returns:
        Dictionary with diagnostic results:
        {
            "marker_statistics": {"1": 5, "B": 2, ...},
            "norma": 10,
            "marker_results": "worry about",
            "total_phonemes": 300,
            "total_markers": 25
        }
    
    Raises:
        ValueError: If input_data is missing required keys
        TypeError: If input_data is not a dictionary
    
    Example:
        >>> from stat import diagnose
        >>> data = {"analyses": [{"triples": [["a", "a", "0"], ["b", "c", "1"]]}]}
        >>> result = diagnose(data)
        >>> print(result["marker_results"])
        'no risk'
    """
    if not isinstance(input_data, dict):
        raise TypeError("input_data must be a dictionary")
    
    if "analyses" not in input_data:
        raise ValueError("input_data must contain 'analyses' key")
    
    analyses = input_data["analyses"]
    
    if not isinstance(analyses, list):
        raise ValueError("'analyses' must be a list")
    
    all_markers = []
    total_phonemes = 0
    
    for analysis in analyses:
        if not isinstance(analysis, dict):
            continue
        
        if "triples" in analysis:
            triples = analysis["triples"]
            if isinstance(triples, list):
                total_phonemes += len(triples)
                markers = extract_markers_from_triples(triples)
                all_markers.extend(markers)
    
    result = analyze_markers(all_markers, total_phonemes)
    
    result["total_phonemes"] = total_phonemes
    result["total_markers"] = len(all_markers)
    
    return result


def diagnose_from_file(input_path: str) -> Dict[str, Any]:
    """
    Library function: Read JSON from file and diagnose.
    
    Args:
        input_path: Path to JSON file with analyses data
    
    Returns:
        Dictionary with diagnostic results (see diagnose())
    
    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    return diagnose(input_data)


def diagnose_from_triples(triples: List[List[str]]) -> Dict[str, Any]:
    """
    Library function: Diagnose directly from triples list.
    
    This is a convenience function for simple cases where you have
    a single list of triples (not wrapped in analyses structure).
    
    Args:
        triples: List of [ref, hyp, mark] triples
    
    Returns:
        Dictionary with diagnostic results (see diagnose())
    
    Example:
        >>> from stat import diagnose_from_triples
        >>> triples = [["a", "a", "0"], ["b", "c", "1"], ["d", "d", "0"]]
        >>> result = diagnose_from_triples(triples)
        >>> print(result["marker_results"])
    """
    input_data = {
        "analyses": [
            {"triples": triples}
        ]
    }
    return diagnose(input_data)


# =============================================================================
# Simple Mode (stdin/stdout Interface)
# =============================================================================

def run_simple_mode():
    """
    Simple Mode: Read JSON from stdin, output classification to stdout.
    
    Expected Input Format (from stdin):
    {
        "analyses": [
            {
                "triples": [["ref", "hyp", "mark"], ...]
            },
            ...
        ]
    }
    
    Output Format (to stdout):
    {
        "marker_statistics": {"1": 5, "B": 2, ...},
        "norma": 10,
        "marker_results": "worry about"
    }
    
    All status messages go to stderr to keep stdout clean for piping.
    """
    try:
        sys.stderr.write("Reading input from stdin...\n")
        input_data = json.load(sys.stdin)
        
        if "analyses" not in input_data:
            raise ValueError("Input JSON must contain 'analyses' key")
        
        analyses = input_data["analyses"]
        
        all_markers = []
        total_phonemes = 0
        
        for analysis in analyses:
            if "triples" in analysis:
                triples = analysis["triples"]
                total_phonemes += len(triples)
                markers = extract_markers_from_triples(triples)
                all_markers.extend(markers)
        
        sys.stderr.write(f"Processed {len(analyses)} analyses, {total_phonemes} phonemes\n")
        sys.stderr.write(f"Found {len(all_markers)} error markers\n")
        
        result = analyze_markers(all_markers, total_phonemes)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: Invalid JSON input - {e}\n")
        sys.exit(1)
    except ValueError as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


# =============================================================================
# Directory Mode (Original Behavior)
# =============================================================================

def run_directory_mode(directory: str):
    """
    Directory Mode: Process all .json files in directory, save out.json.
    
    This preserves the original developer behavior exactly:
    - Scans directory for .json files < 1MB
    - Reads each file and extracts markers
    - Aggregates statistics across all files
    - Saves result to out.json
    
    Args:
        directory: Path to directory containing .json analysis files
    """
    print(f"Scanning directory: {directory}")
    
    unsortedList = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            size = os.stat(path).st_size
            if size < 1000000:
                if ".json" in file:
                    unsortedList.append(os.path.join(root, file))
    
    print(f'{len(unsortedList)} files found.')
    
    all_markers = []
    total_phonemes = 0
    
    for filename in unsortedList:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            total_phonemes += len(data)
            markers = extract_markers_from_triples(data)
            all_markers.extend(markers)
            
        except FileNotFoundError:
            print(f"Error: File not found - {filename}")
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON {filename} - {e}")
        except Exception as e:
            print(f"Unexpected error processing {filename}: {e}")
    
    result = analyze_markers(all_markers, total_phonemes)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Statistics successfully written to {OUTPUT_FILE}:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """
    Entry point: detect mode from arguments, dispatch to handler.
    
    Mode Detection:
    - Simple Mode: --stdin flag or stdin pipe -> python3 statdiag.py --stdin
    - Directory Mode: -d flag with directory path -> python3 statdiag.py -d <dir>
    """
    parser = argparse.ArgumentParser(
        description='Dysmark Diagnostic Statistics and Classification Tool'
    )
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default=None,
        help=f'Directory containing .json analysis files (default: {DEFAULT_DIRECTORY})'
    )
    parser.add_argument(
        '--stdin',
        action='store_true',
        help='Read from stdin instead of directory (simple mode)'
    )
    
    args = parser.parse_args()
    
    if args.stdin or (not args.directory and not sys.stdin.isatty()):
        run_simple_mode()
        return
    
    directory = args.directory if args.directory else DEFAULT_DIRECTORY
    
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        sys.exit(1)
    
    run_directory_mode(directory)


if __name__ == "__main__":
    main()
