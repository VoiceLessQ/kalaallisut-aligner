# TTS-Based Alignment: Reverse Engineering Approach

This document explains how to use Oqaasileriffik's **Martha TTS** (Text-to-Speech) system for forced alignment and transcription assistance through a "reverse engineering" approach.

## Overview

Instead of using traditional ASR (Automatic Speech Recognition), we can use TTS in reverse:

```
Traditional ASR:  Audio → Model → Text
TTS-based approach:  Audio + TTS(candidate_text) → Similarity → Best Match
```

This is known as **synthesis-by-analysis** or **TTS-based ASR**.

---

## Available Resources

### Martha TTS (Oqaasileriffik)

- **API Endpoint**: `https://oqaasileriffik.gl/martha/tts/`
- **Audio Files**: `https://oqaasileriffik.gl/martha/data/`
- **Documentation**: https://github.com/Oqaasileriffik/martha
- **License**: Free for non-commercial use
- **Limit**: 10,000 Unicode characters per request

**Features**:
- Generates MP3 audio from Kalaallisut text
- Returns word-level timing synchronization data
- High-quality neural TTS voice
- Public API (please don't abuse it)

### What We Have

- **6,812 aligned sentence pairs** (Danish-Kalaallisut corpus)
- **16,819 dictionary entries** (Kalaallisut-English)
- **FST morphological analyzer** (lang-kal)
- **Statistical aligner** (hunalign)

---

## Approach 1: Forced Alignment

**Goal**: You have audio + text → you want word-level timestamps

### Use Cases

1. **Audiobook alignment**: Sync text with audio recordings
2. **Subtitle generation**: Create timed subtitles for Kalaallisut videos
3. **Pronunciation verification**: Compare learner audio to reference
4. **Speech corpus annotation**: Add timestamps to training data

### Workflow

```python
# Input
source_audio = "recording.wav"  # Your Kalaallisut audio
text = "Takussaanga Kalaallit Nunaat"  # Transcript

# Step 1: Generate reference via TTS
tts_result = martha_tts.synthesize(text)
# Returns: reference.mp3 + word-level timestamps

# Step 2: Extract features
source_mfcc = extract_mfcc(source_audio)
reference_mfcc = extract_mfcc(tts_result['audio_url'])

# Step 3: Dynamic Time Warping alignment
dtw_path = compute_dtw(source_mfcc, reference_mfcc)

# Step 4: Map timestamps
# Martha says: "Takussaanga" = 0.0-1.2s, "Kalaallit" = 1.2-1.8s, "Nunaat" = 1.8-2.5s
# DTW maps reference frames to source frames
# Result: Your audio timestamps for each word
```

### Implementation

```python
from src.tts_aligner import TTSBasedAligner

aligner = TTSBasedAligner()

result = aligner.align_audio(
    source_audio="my_recording.wav",
    text="Kalaallit Nunaat",
    output_dir="alignment_output"
)

print(result['word_timings'])  # [(word, start, end), ...]
print(result['dtw_distance'])  # Similarity score
```

### Advantages

✓ **No ASR model needed** - Just use TTS + DTW
✓ **Word-level timestamps** - Martha provides timing data
✓ **Language-specific** - Optimized for Kalaallisut
✓ **Free API** - No training data or GPU required

### Challenges

⚠ **Speaker variability** - Accuracy depends on voice similarity
⚠ **Accent differences** - Different dialects may align poorly
⚠ **Computational cost** - DTW is O(n²) for long sequences
⚠ **Requires libraries** - librosa, dtaidistance, scipy

---

## Approach 2: Transcription Search

**Goal**: You have audio only → you want the text

### Use Cases

1. **Corpus verification**: Match audio to text in your corpus
2. **Audio search**: Find which sentence matches this audio
3. **Constrained transcription**: Limited vocabulary (e.g., government docs)
4. **Quality assurance**: Verify recorded audio matches script

### Workflow

```python
# Input
source_audio = "unknown_audio.wav"

# Step 1: Generate candidates
candidates = [
    "Kalaallit Nunaat",
    "Aasaqqussuaq",
    "Takussaanga",
    # ... from corpus or language model
]

# Step 2: For each candidate
scores = []
for candidate_text in candidates:
    # 2a. Generate TTS audio
    tts_audio = martha_tts.synthesize(candidate_text)

    # 2b. Extract features
    candidate_mfcc = extract_mfcc(tts_audio)
    source_mfcc = extract_mfcc(source_audio)

    # 2c. Compute similarity
    dtw_distance = compute_dtw(source_mfcc, candidate_mfcc)
    scores.append((candidate_text, dtw_distance))

# Step 3: Rank by similarity (lower distance = better)
best_match = min(scores, key=lambda x: x[1])
print(f"Best match: {best_match[0]} (distance: {best_match[1]:.2f})")
```

### Candidate Generation Strategies

**Strategy 1: Corpus Search**
```python
# Use your existing aligned corpus
from src.utils import load_aligned_pairs

pairs = load_aligned_pairs("data/aligned/corpus_6798_pairs.txt")
candidates = [kal for da, kal in pairs]  # 6,812 sentences
```

**Strategy 2: Dictionary N-grams**
```python
# Combine common words/phrases
from glosser.kalaallisut_english_dict import load_dictionary

dict_entries = load_dictionary()  # 16,819 entries
candidates = generate_ngrams(dict_entries, n=1-3)
```

**Strategy 3: Morphological Generation**
```python
# Use lang-kal FST to generate valid forms
from src.morphology import analyze_word

# Generate morphological variations
candidates = generate_forms("taku")  # see → takussaanga, takuvoq, etc.
```

### Advantages

✓ **No ASR training** - Use existing TTS
✓ **Constrained vocabulary** - Works well with known sentence set
✓ **Corpus alignment** - Match audio to text corpus
✓ **Quality control** - Verify recordings

### Challenges

⚠ **Computationally expensive** - N candidates = N TTS calls
⚠ **API rate limits** - Martha requests politeness (1-2 sec delay)
⚠ **Scalability** - Best for < 1000 candidates
⚠ **Novel sentences** - Won't find text not in candidates

---

## Implementation Details

### MFCC Feature Extraction

**MFCC** (Mel-Frequency Cepstral Coefficients) represents audio's spectral characteristics.

```python
import librosa

def extract_mfcc(audio_file, n_mfcc=13):
    """Extract MFCC features from audio."""
    y, sr = librosa.load(audio_file, sr=16000)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc  # Shape: (n_mfcc, time_frames)
```

**Parameters**:
- `n_mfcc=13`: Standard for speech (13 coefficients)
- `sr=16000`: 16kHz sample rate (speech quality)

### Dynamic Time Warping (DTW)

**DTW** finds optimal alignment between two sequences of different lengths.

```python
from dtaidistance import dtw

def align_sequences(seq1, seq2):
    """Align two feature sequences using DTW."""
    distance = dtw.distance(seq1, seq2)
    path = dtw.warping_path(seq1, seq2)
    return distance, path
```

**Output**:
- `distance`: Similarity score (lower = more similar)
- `path`: List of (index1, index2) mappings

### Martha TTS Integration

```python
from src.tts_aligner import MarthaTTS

tts = MarthaTTS()

# Synthesize text
result = tts.synthesize("Kalaallit Nunaat")

# Response structure:
{
    "fn": "abcd1234.mp3",           # Filename
    "du": 2.5,                       # Duration (seconds)
    "sz": 40960,                     # Size (bytes)
    "ts": [...],                     # Timestamps (word-level)
    "audio_url": "https://..."       # Download URL
}

# Download audio
audio_path = tts.download_audio(
    result['audio_url'],
    Path("output/reference.mp3")
)
```

---

## Practical Examples

### Example 1: Align Audio with Known Text

```python
from src.tts_aligner import TTSBasedAligner
from pathlib import Path

# Initialize
aligner = TTSBasedAligner()

# Align
result = aligner.align_audio(
    source_audio=Path("recordings/sentence_001.wav"),
    text="Takussaanga Kalaallit Nunaat imaqa aasaqqussuaq",
    output_dir=Path("alignment_results")
)

# Check results
print(f"Alignment quality: {result['dtw_distance']:.2f}")
print(f"Word timings:")
for word, start, end in result['word_timings']:
    print(f"  {word}: {start:.2f}s - {end:.2f}s")
```

### Example 2: Find Matching Sentence from Corpus

```python
from src.tts_aligner import MarthaTTS
from src.utils import load_aligned_pairs
import librosa
from dtaidistance import dtw

# Load corpus
pairs = load_aligned_pairs("data/aligned/corpus_6798_pairs.txt")

# Your audio
source_audio = "unknown_recording.wav"
source_mfcc = librosa.feature.mfcc(*librosa.load(source_audio, sr=16000))

# Search corpus
tts = MarthaTTS()
best_match = None
best_distance = float('inf')

for i, (danish, kalaallisut) in enumerate(pairs[:100]):  # First 100
    # Generate TTS
    tts_result = tts.synthesize(kalaallisut)

    # Download and extract features
    ref_audio = tts.download_audio(tts_result['audio_url'], f"temp_{i}.mp3")
    ref_mfcc = librosa.feature.mfcc(*librosa.load(ref_audio, sr=16000))

    # Compare
    distance = dtw.distance(source_mfcc.T, ref_mfcc.T)

    if distance < best_distance:
        best_distance = distance
        best_match = (danish, kalaallisut)

    # Rate limiting
    time.sleep(1.5)

print(f"Best match: {best_match[1]}")
print(f"Danish: {best_match[0]}")
print(f"Distance: {best_distance:.2f}")
```

### Example 3: Batch Process Audio Files

```python
from src.tts_aligner import TTSBasedAligner
from pathlib import Path

aligner = TTSBasedAligner()

# Audio files with corresponding texts
data = [
    ("audio_001.wav", "Kalaallit Nunaat"),
    ("audio_002.wav", "Aasaqqussuaq aappaluttaavoq"),
    ("audio_003.wav", "Takussaanga imaqa"),
]

results = []
for audio_file, text in data:
    result = aligner.align_audio(
        source_audio=Path(audio_file),
        text=text,
        output_dir=Path("batch_output")
    )
    results.append(result)

# Analyze quality
avg_distance = sum(r['dtw_distance'] for r in results) / len(results)
print(f"Average alignment quality: {avg_distance:.2f}")
```

---

## Performance Considerations

### Speed

**TTS API call**: ~2-5 seconds per request
**MFCC extraction**: ~0.1s per second of audio
**DTW alignment**: ~0.5s for 10s audio (13 MFCC coefficients)

**Total for forced alignment**: ~3-6 seconds per sentence

### Memory

**MFCC features**: ~52 KB per second of audio (13 coefficients, 50 fps)
**DTW matrix**: O(n × m) where n, m = sequence lengths

**For 10-second audio**: ~520 KB MFCCs, ~2.5 MB DTW matrix

### Cost

**Martha TTS**: Free (but be respectful)
**Compute**: CPU-only (no GPU needed)
**Libraries**: Free and open-source

---

## Best Practices

### API Usage

```python
# ✓ GOOD: Add delays between requests
results = tts.batch_synthesize(texts, delay=1.5)

# ✗ BAD: Rapid-fire requests
for text in texts:
    tts.synthesize(text)  # No delay!
```

### Error Handling

```python
# ✓ GOOD: Handle API failures gracefully
try:
    result = tts.synthesize(text)
except requests.Timeout:
    logger.error("TTS request timed out")
    result = None
except requests.RequestException as e:
    logger.error(f"TTS API error: {e}")
    result = None
```

### Candidate Pruning

```python
# ✓ GOOD: Pre-filter candidates by length
def filter_candidates(audio_duration, candidates):
    """Keep only candidates of similar length."""
    return [
        c for c in candidates
        if 0.8 * audio_duration < estimate_duration(c) < 1.2 * audio_duration
    ]

# Reduces search space significantly
```

---

## Comparison with Traditional ASR

| Aspect | TTS-based Approach | Traditional ASR |
|--------|-------------------|-----------------|
| **Training Data** | Not needed | Requires hours of transcribed audio |
| **Model** | Uses existing TTS | Requires trained ASR model |
| **Accuracy** | Depends on speaker similarity | Depends on training data quality |
| **Speed** | Slower (multiple TTS calls) | Faster (single forward pass) |
| **Vocabulary** | Limited to candidates | Open vocabulary |
| **Setup** | Easy (just API calls) | Hard (model training) |
| **Best for** | Constrained vocab, alignment | Open-ended transcription |

---

## Future Improvements

### Short Term

- [ ] Implement full timestamp mapping using DTW path
- [ ] Add unit tests for TTS integration
- [ ] Benchmark alignment accuracy on test set
- [ ] Add caching for TTS results

### Medium Term

- [ ] Develop language model for candidate generation
- [ ] Implement phoneme-level alignment
- [ ] Add confidence scoring for alignments
- [ ] Create evaluation metrics

### Long Term

- [ ] Train acoustic model using TTS-generated data
- [ ] Hybrid TTS-ASR approach
- [ ] Real-time alignment interface
- [ ] Multi-speaker adaptation

---

## References

### Academic Background

**Dynamic Time Warping**:
- Sakoe, H., & Chiba, S. (1978). "Dynamic programming algorithm optimization for spoken word recognition." *IEEE TASSP*, 26(1), 43-49.

**TTS-based ASR**:
- Watts, O., et al. (2015). "Where do the improvements come from in sequence-to-sequence neural TTS?" *arXiv:1503.03382*.
- Zen, H., et al. (2019). "LibriTTS: A corpus derived from LibriSpeech for text-to-speech." *Interspeech 2019*.

**Forced Alignment**:
- McAuliffe, M., et al. (2017). "Montreal Forced Aligner: Trainable text-speech alignment using Kaldi." *Interspeech 2017*.

### Software

**Martha TTS**: https://github.com/Oqaasileriffik/martha
**librosa**: https://librosa.org/
**dtaidistance**: https://github.com/wannesm/dtaidistance

---

## Getting Help

**Issues**: Open an issue at https://github.com/VoiceLessQ/kalaallisut-aligner/issues
**Martha TTS**: Contact Oqaasileriffik at https://oqaasileriffik.gl/
**Documentation**: See `docs/GUIDE.md` for general usage

---

**Last Updated**: November 2025
**Author**: VoiceLessQ
**License**: MIT (code), CC-BY-SA 4.0 (data)
