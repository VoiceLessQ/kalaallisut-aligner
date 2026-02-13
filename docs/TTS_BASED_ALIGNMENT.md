# TTS-Based Alignment

Using Oqaasileriffik's Martha TTS to do forced alignment and transcription search without training an ASR model.

## The idea

Instead of speech-to-text, flip it around: generate audio from candidate texts via TTS, then compare against the source recording using MFCC features and Dynamic Time Warping.

```
Traditional ASR:     Audio -> Model -> Text
This approach:       Audio + TTS(candidate) -> DTW similarity -> Best match
```

## What you need

- Martha TTS API: `https://oqaasileriffik.gl/martha/tts/` (free, non-commercial)
- Python libs: `librosa`, `dtaidistance`, `numpy`, `scipy`, `requests`
- Your aligned corpus for candidate sentences

```bash
pip install librosa dtaidistance numpy scipy requests
```

## Forced alignment (audio + known text -> timestamps)

If you already have the transcript and want word-level timing:

```python
from src.tts_aligner import TTSBasedAligner

aligner = TTSBasedAligner()
result = aligner.align_audio(
    source_audio="recording.wav",
    text="Takussaanga Kalaallit Nunaat",
    output_dir="output"
)

for word, start, end in result['word_timings']:
    print(f"  {word}: {start:.2f}s - {end:.2f}s")
```

Martha returns word-level timestamps with its TTS output. DTW maps those timestamps from the synthetic audio onto your real recording.

## Transcription search (audio only -> find matching text)

If you don't know what's being said, search your corpus:

```bash
python src/audio_transcriber.py unknown.wav --top 5 --max-candidates 100
```

This generates TTS for each candidate sentence, compares MFCCs via DTW, and ranks by distance (lower = better match).

Works best when the answer is actually in your corpus. Not magic -- it won't transcribe novel sentences.

### Speeding it up

- Filter candidates by estimated duration (the transcriber does this automatically, ~3 chars/sec)
- Start with `--max-candidates 30` to test, scale up if results look promising
- Cache TTS results so you don't re-generate the same sentence twice

## Limitations

- Each candidate requires a TTS API call (~2-3 seconds each). Be polite with rate limiting (`--delay 1.5`).
- DTW is O(n^2) for long audio.
- Accuracy depends on how close the speaker's voice is to Martha's synthetic voice.
- Only finds sentences that exist in your candidate set.

## When to use this vs. traditional ASR

Use this when:
- You have a limited set of known sentences to match against
- You're aligning audiobooks or recordings with existing transcripts
- No Kalaallisut ASR model is available

Use a real ASR model when:
- You need open-vocabulary transcription
- You're processing lots of audio quickly
- Speaker variability matters

## References

- Martha TTS: https://github.com/Oqaasileriffik/martha
- librosa: https://librosa.org/
- dtaidistance: https://github.com/wannesm/dtaidistance
- Sakoe & Chiba (1978), "Dynamic programming algorithm optimization for spoken word recognition"
- McAuliffe et al. (2017), "Montreal Forced Aligner"
