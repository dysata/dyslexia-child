```
python dysmarkcclsjson.py ./hwa12
```


## Использование в качестве библиотечных модулей

```python
# Example 1: Basic usage with analyses object
from stat import diagnose

data = {
    "analyses": [
        {"triples": [["a", "a", "0"], ["b", "c", "1"]]}
    ]
}
result = diagnose(data)
print(result["marker_results"])
```



```python
# Example 2: From JSON file
from stat import diagnose_from_file

result = diagnose_from_file("analysis_results.json")
print(result["marker_statistics"])
```


```python
# Example 3: Direct triples input
from stat import diagnose_from_triples

triples = [["a", "a", "0"], ["b", "c", "1"], ["d", "d", "0"]]
result = diagnose_from_triples(triples)
print(result["norma"])
```

```python
# Example 4: Integration with dysmark
from dysmarkccls_clean import get_markers_with_quality
from stat import diagnose

# Get markers from audio
markers_result = get_markers_with_quality("text.txt", "audio.wav")

# Create analyses structure
if markers_result["quality"] == "good":
    analyses_data = {
        "analyses": [
            {"triples": markers_result["triples"]}
        ]
    }
    
    # Get diagnosis
    diagnosis = diagnose(analyses_data)
    print(f"Risk group: {diagnosis['marker_results']}")
```
