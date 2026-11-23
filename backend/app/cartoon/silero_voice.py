"""
Silero Local Neural TTS Engine (100% Offline, GPU/CPU).
Provides realistic, expressive Russian voices:
- eugene: energetic young male storyteller (ideal for YouTube shorts / crypto drama)
- aidar: deep baritone, radio/podcast host
- baya: warm female storyteller
- kseniya: clear female narrator
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import scipy.io.wavfile as wavfile
import subprocess
import torch

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

_SILERO_MODEL = None


def get_silero_model():
    global _SILERO_MODEL
    if _SILERO_MODEL is None:
        device = torch.device("cpu")
        local_hub = Path.home() / ".cache/torch/hub/snakers4_silero-models_master"
        if local_hub.exists():
            model, _ = torch.hub.load(
                str(local_hub),
                "silero_tts",
                language="ru",
                speaker="v5_6_ru",
                source="local",
            )
        else:
            model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-models",
                model="silero_tts",
                language="ru",
                speaker="v5_6_ru",
                trust_repo=True,
            )
        model.to(device)
        _SILERO_MODEL = model
    return _SILERO_MODEL


def synthesize_silero_script(
    sentences: List[str],
    speaker: str = "eugene",  # "eugene", "aidar", "baya", "kseniya"
    out_wav: Path = Path("output/silero_master.wav"),
    sample_rate: int = 48000,
) -> Tuple[Path, List[Dict], float]:
    """Synthesizes text sentences, joins with natural pauses, and returns words with timestamps."""
    model = get_silero_model()
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    all_audio = []
    words_data = []
    current_time = 0.0
    pause_samples = int(0.20 * sample_rate)  # 200ms natural breath pause between sentences

    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        # Apply Silero v5.6 TTS with automatic Russian stress & homograph disambiguation
        audio_tensor = model.apply_tts(
            text=s_clean,
            speaker=speaker,
            sample_rate=sample_rate,
            put_accent=True,
            put_yo=True,
            put_stress_homo=True,
            put_yo_homo=True,
        )
        audio_np = audio_tensor.numpy()
        dur = len(audio_np) / sample_rate

        # Split into words for karaoke subtitles
        s_words = s_clean.replace(".", "").replace("!", "").replace("?", "").replace(",", "").split()
        if s_words:
            w_dur = dur / len(s_words)
            for i, w in enumerate(s_words):
                w_start = current_time + i * w_dur
                words_data.append({
                    "word": w,
                    "start": round(w_start, 3),
                    "end": round(w_start + w_dur * 0.9, 3),
                })

        all_audio.append(audio_np)
        current_time += dur

        # Add pause
        all_audio.append(np.zeros(pause_samples, dtype=np.float32))
        current_time += 0.20

    full_audio = np.concatenate(all_audio)
    # Master audio: Normalize to -1 dB peak
    mx = np.max(np.abs(full_audio))
    if mx > 1e-6:
        full_audio = full_audio / mx * 0.94
    audio_int16 = (full_audio * 32767).astype(np.int16)

    raw_wav = out_wav.parent / f"raw_{out_wav.name}"
    wavfile.write(str(raw_wav), sample_rate, audio_int16)

    # Master through FFmpeg (broadcast EQ & compression)
    master_filters = (
        "highpass=f=70,"
        "equalizer=f=3500:width_type=o:w=1.0:g=2.0,"
        "acompressor=threshold=-16dB:ratio=3:attack=10:release=80,"
        "loudnorm=I=-14:LRA=7:TP=-1.5"
    )
    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(raw_wav),
        "-af", master_filters,
        str(out_wav),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if raw_wav.exists():
        raw_wav.unlink()

    total_duration = len(full_audio) / sample_rate
    return out_wav, words_data, total_duration
