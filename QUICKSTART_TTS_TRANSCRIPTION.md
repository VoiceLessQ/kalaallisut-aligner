# Quick Start: TTS-Based Audio Transcription

**Goal**: You have Kalaallisut audio → get transcription using Martha TTS

## How It Works

```
Your Audio (unknown text)
    ↓
Generate candidates from corpus (6,812 sentences)
    ↓
For each candidate:
  ├─ Martha TTS → generate audio
  ├─ Compare to your audio (MFCC + DTW)
  └─ Calculate similarity score
    ↓
Return best matches
```

**No ASR model needed!** Uses TTS "in reverse" to find matching text.

---

## Installation

```bash
# Install audio processing dependencies
pip install librosa dtaidistance numpy scipy requests

# Or install all optional dependencies
pip install -r requirements.txt
```

---

## Basic Usage

### Transcribe Single Audio File

```bash
python src/audio_transcriber.py my_audio.wav --top 5
```

**Output**:
```
TRANSCRIPTION RESULTS: my_audio.wav
============================================================

1. [Distance: 12.45]
   Kalaallit Nunaat

2. [Distance: 15.78]
   Aasaqqussuaq aappaluttaavoq

3. [Distance: 18.92]
   Takussaanga imaqa

...
```

Lower distance = better match!

---

## Advanced Options

### Limit Search Space

```bash
# Test only 50 candidates (faster)
python src/audio_transcriber.py audio.wav --max-candidates 50
```

### Use Custom Corpus

```bash
# Use your own sentence list
python src/audio_transcriber.py audio.wav --corpus my_sentences.txt
```

### Save Results

```bash
# Save to JSON
python src/audio_transcriber.py audio.wav --output results.json --top 10
```

### Adjust API Rate Limiting

```bash
# 2 second delay between TTS requests (be respectful!)
python src/audio_transcriber.py audio.wav --delay 2.0
```

---

## Python API

```python
from pathlib import Path
from src.audio_transcriber import AudioTranscriber

# Initialize with your corpus
transcriber = AudioTranscriber(
    corpus_path=Path("data/aligned/corpus_6798_pairs.txt")
)

# Transcribe audio
results = transcriber.transcribe(
    audio_path=Path("my_audio.wav"),
    top_k=5,
    max_candidates=100,
    delay_between_requests=1.5
)

# Print results
for text, distance in results:
    print(f"[{distance:.2f}] {text}")
```

### Batch Processing

```python
# Transcribe multiple files
audio_files = [
    Path("audio1.wav"),
    Path("audio2.wav"),
    Path("audio3.wav"),
]

results = transcriber.transcribe_batch(
    audio_files,
    output_json=Path("batch_results.json"),
    top_k=3,
    max_candidates=50
)
```

---

## Performance

### Speed
- **~2-3 seconds** per candidate (TTS call + download + comparison)
- **100 candidates** = ~3-5 minutes
- **Parallel**: Run multiple processes for different audio files

### Accuracy
- **Best for**: Sentences that exist in your corpus
- **Works well**: Short utterances (< 10 seconds)
- **Challenges**: Novel sentences, strong accents, background noise

### Cost
- **Martha TTS**: Free API (be respectful - use delays!)
- **Compute**: CPU only (no GPU needed)
- **Storage**: ~50KB per cached audio file

---

## Tips for Better Results

### 1. Duration-Based Filtering

The transcriber automatically filters candidates by length:
- Estimates ~3 characters/second for Kalaallisut
- Keeps candidates within ±30% of audio duration
- Reduces search space significantly

### 2. Corpus Quality

Better corpus = better results:
```python
# Use domain-specific sentences
transcriber = AudioTranscriber(
    corpus_path=Path("government_docs_corpus.txt")  # If audio is from gov docs
)
```

### 3. Candidate Pruning

For very long audio, pre-filter candidates:
```python
# Filter by keywords
def filter_by_keywords(candidates, keywords):
    return [c for c in candidates if any(kw in c for kw in keywords)]

# Filter by starting words
def filter_by_start(candidates, start_word):
    return [c for c in candidates if c.startswith(start_word)]
```

### 4. Iterative Refinement

```python
# First pass: Quick search (50 candidates)
top_50 = transcriber.transcribe(audio, max_candidates=50)

# Analyze top results, generate similar variations
# Second pass: Test variations
```

---

## Common Issues

### ImportError: No module named 'librosa'

```bash
pip install librosa dtaidistance
```

### TTS Request Timeout

Increase delay:
```bash
python src/audio_transcriber.py audio.wav --delay 3.0
```

### No Matches Found

- Check audio quality (clear speech, no background noise)
- Try more candidates: `--max-candidates 200`
- Check corpus contains similar sentences
- Verify audio is Kalaallisut (not Danish or other language)

### DTW Distance Very High

- Source audio may not match any corpus sentence
- Try different corpus
- Audio quality issues
- Wrong language or strong accent

---

## Example: Transcribe Unknown Audio

Suppose you have `mystery_audio.wav` (5 seconds of Kalaallisut speech):

```bash
# Step 1: Quick test with 30 candidates
python src/audio_transcriber.py mystery_audio.wav \
    --max-candidates 30 \
    --top 3 \
    --output quick_test.json

# Step 2: Check results
cat quick_test.json

# Step 3: If matches look promising, run full search
python src/audio_transcriber.py mystery_audio.wav \
    --max-candidates 200 \
    --top 10 \
    --output full_results.json
```

---

## Workflow Diagram

```
┌─────────────────────────────────────────────┐
│  Input: mystery_audio.wav (Kalaallisut)     │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Extract MFCC features                      │
│  Duration: 5.2s                             │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Load candidates from corpus                │
│  6,812 sentences → filter by duration       │
│  → 423 candidates (15-20 chars)             │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Limit to max_candidates (100)              │
│  Sample evenly from 423 → 100               │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  For each candidate (100):                  │
│    1. Martha TTS → generate audio           │
│    2. Download MP3                          │
│    3. Extract MFCC                          │
│    4. DTW distance to source                │
│    5. Clean cache                           │
│    6. Sleep 1.5s (rate limit)               │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Sort by DTW distance (ascending)           │
│  Return top 5 matches                       │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Output:                                    │
│  1. [12.4] "Kalaallit Nunaat"              │
│  2. [15.7] "Aasaqqussuaq"                  │
│  3. [18.2] "Takussaanga imaqa"             │
│  4. [21.5] "Nuuk Qallunaaq"                │
│  5. [23.8] "Imaqa aappaluttaavoq"          │
└─────────────────────────────────────────────┘
```

---

## Next Steps

1. **Try it**: Run on sample audio
2. **Tune parameters**: Adjust max_candidates and delay
3. **Evaluate**: Check if top matches are correct
4. **Expand corpus**: Add more candidate sentences
5. **Optimize**: Implement caching, parallel processing

See `docs/TTS_BASED_ALIGNMENT.md` for detailed documentation.

---

**Questions?** Open an issue at https://github.com/VoiceLessQ/kalaallisut-aligner/issues
