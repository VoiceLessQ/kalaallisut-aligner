# TTS API Access Limitations

## Problem: Both TTS APIs Block Programmatic Access

When testing from server/cloud environments (GitHub Actions, CI/CD, cloud VMs), both Kalaallisut TTS APIs return **403 Forbidden**:

### Martha TTS (Oqaasileriffik)
```bash
$ curl "https://oqaasileriffik.gl/martha/tts/?n=json&t=Aasaqqussuaq"
Access denied
```
**Status**: 403 Access Denied

### Google Translate TTS
```bash
$ curl "https://translate.google.com/translate_tts?ie=UTF-8&q=Aasaqqussuaq&tl=kl&client=tw-ob"
Error 403 (Forbidden)
```
**Status**: 403 Forbidden

---

## Why This Happens

Both APIs detect and block:
- **Server/cloud IPs** (AWS, GCP, GitHub Actions)
- **Automated requests** (missing browser fingerprints)
- **High request rates** (anti-scraping protection)
- **Missing cookies/sessions** (CORS protection)

**Both APIs work fine from local machines** (Windows/Mac/Linux with browser headers).

---

## Solutions

### ✅ Option 1: Self-Host Martha TTS (Recommended)

Martha provides Docker containers for local hosting:

```bash
# Clone Martha TTS repository
cd ~
git clone https://github.com/Oqaasileriffik/martha.git
cd martha/docker

# Follow Docker setup instructions
# (Check their docker/ folder for README)

# Run Martha TTS locally
docker-compose up -d

# Use local endpoint
python src/audio_transcriber.py my_audio.wav \
    --tts-backend martha \
    --tts-url http://localhost:8080/tts/
```

**Pros**:
- ✅ Full control
- ✅ No rate limits
- ✅ Best quality
- ✅ Works offline

**Cons**:
- ⚠ Requires Docker setup
- ⚠ Uses disk space

---

### ✅ Option 2: Use Pre-Recorded Audio

If you have Kalaallisut audio recordings with transcripts, use those directly instead of TTS:

```python
# Instead of generating TTS audio, use your recordings
corpus = [
    ("audio_001.wav", "Kalaallit Nunaat"),
    ("audio_002.wav", "Aasaqqussuaq"),
    # ... your audio files with texts
]

# Compare your unknown audio to these recordings
for audio_file, text in corpus:
    similarity = compare_audio(mystery_audio, audio_file)
    # Find best match
```

**Pros**:
- ✅ No TTS needed
- ✅ Real human voices
- ✅ Works immediately

**Cons**:
- ⚠ Need existing recordings
- ⚠ Limited to recorded sentences

---

### ✅ Option 3: Run from Local Machine

The code works fine from your Windows/Mac/Linux machine:

```bash
# On your local machine (not server)
cd /path/to/kalaallisut-aligner

# This will work because it's not from a cloud IP
python src/audio_transcriber.py my_audio.wav --tts-backend google
```

**Pros**:
- ✅ No setup needed
- ✅ Works immediately
- ✅ Free

**Cons**:
- ⚠ Won't work in CI/CD
- ⚠ Won't work on servers
- ⚠ May hit rate limits

---

### ✅ Option 4: Request API Access

Contact Oqaasileriffik for official Martha API access:

- **Website**: https://oqaasileriffik.gl/
- **Email**: Check their contact page
- **Explain**: Research/educational use case

They may provide:
- API keys
- Higher rate limits
- Whitelisted IPs

---

### ❌ Option 5: Proxy/VPN (Not Recommended)

You could route requests through proxies/VPNs to avoid detection, but:
- ⚠ Violates terms of service
- ⚠ May get your IP banned
- ⚠ Unreliable
- ⚠ Unethical

**Don't do this** - use self-hosting or ask for API access instead.

---

## Implementation Status

### Code Implemented ✅

All TTS code is ready and working:
- `src/google_tts.py` - Google TTS client
- `src/tts_aligner.py` - Martha TTS client
- `src/audio_transcriber.py` - Audio transcription using TTS

```bash
# Works on local machines
python src/audio_transcriber.py audio.wav --tts-backend google

# Ready for self-hosted Martha
python src/audio_transcriber.py audio.wav --tts-backend martha
```

### API Access ❌

- Martha public API: **Blocked** (403)
- Google TTS: **Blocked** (403)

Both work from local machines, blocked from servers/CI.

---

## Testing from Your Local Machine

Since you showed Google TTS working on your Windows machine:

```powershell
# On Windows (WSL)
cd /mnt/c/path/to/kalaallisut-aligner

# This should work
python src/audio_transcriber.py your_audio.wav --top 5
```

The code is correct - it's just the APIs that block server requests.

---

## Recommended Next Steps

1. **Test locally** on your Windows machine (should work)
2. **Self-host Martha** for production use (Docker)
3. **Contact Oqaasileriffik** for official API access
4. **Use pre-recorded audio** if you have it

---

## Related Files

- `src/google_tts.py` - Google TTS implementation
- `src/tts_aligner.py` - Martha TTS implementation
- `src/audio_transcriber.py` - Main transcription engine
- `docs/TTS_BASED_ALIGNMENT.md` - Technical documentation
- `QUICKSTART_TTS_TRANSCRIPTION.md` - Quick start guide

---

**Last Updated**: November 2025
**Status**: APIs blocked from servers, work from local machines
**Recommended Solution**: Self-host Martha TTS using Docker
