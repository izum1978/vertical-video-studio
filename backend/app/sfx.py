import math
import os
import random
import re
import struct
import wave
from pathlib import Path

from .config import ROOT

SFX_DIR = ROOT / "backend" / "assets" / "sfx"
SFX_DIR.mkdir(parents=True, exist_ok=True)


def _write_wav(path: Path, samples: list[float], sample_rate: int = 44100):
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)  # mono
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        # Clip and convert to 16-bit int
        raw = bytearray()
        for s in samples:
            val = max(-1.0, min(1.0, s))
            raw.extend(struct.pack("<h", int(val * 32767)))
        wf.writeframes(raw)


def ensure_default_sfx() -> dict[str, Path]:
    """Генерирует базовый набор студийных SFX в формате 16-bit WAV, если они отсутствуют."""
    SR = 44100
    files = {
        "whoosh": SFX_DIR / "whoosh.wav",
        "glitch": SFX_DIR / "glitch.wav",
        "impact": SFX_DIR / "impact.wav",
        "boom": SFX_DIR / "impact.wav",
        "click": SFX_DIR / "click.wav",
        "pop": SFX_DIR / "click.wav",
        "riser": SFX_DIR / "riser.wav",
        "heartbeat": SFX_DIR / "heartbeat.wav",
    }

    # 1. Whoosh (свист перехода, 0.38с)
    if not files["whoosh"].exists():
        dur = 0.38
        N = int(SR * dur)
        samples = []
        rng = random.Random(42)
        for i in range(N):
            t = i / SR
            norm_t = t / dur
            # Hanning-like envelope
            env = math.sin(norm_t * math.pi) ** 1.8
            # White noise + swept sine
            freq = 300 + 2600 * math.sin(norm_t * math.pi)
            noise = (rng.random() * 2 - 1) * 0.45
            tonal = math.sin(2 * math.pi * freq * t) * 0.55
            samples.append((noise + tonal) * env * 0.8)
        _write_wav(files["whoosh"], samples, SR)

    # 2. Glitch (цифровой скрежет/сбой, 0.28с)
    if not files["glitch"].exists():
        dur = 0.28
        N = int(SR * dur)
        samples = []
        rng = random.Random(108)
        freqs = [80, 240, 1200, 3200, 480, 80]
        for i in range(N):
            t = i / SR
            f_idx = int((t / dur) * len(freqs)) % len(freqs)
            f = freqs[f_idx]
            # Bitcrushed square wave
            wave_val = 1.0 if math.sin(2 * math.pi * f * t) > 0 else -1.0
            noise = (rng.random() * 2 - 1) * 0.25
            env = max(0.0, 1.0 - (t / dur) ** 0.8)
            samples.append((wave_val * 0.6 + noise) * env * 0.6)
        _write_wav(files["glitch"], samples, SR)

    # 3. Impact / Boom (глубокий кинематографичный саб-удар, 1.2с)
    if not (SFX_DIR / "impact.wav").exists():
        dur = 1.2
        N = int(SR * dur)
        samples = []
        for i in range(N):
            t = i / SR
            # Pitch drop from 140Hz down to 36Hz
            freq = 36 + 104 * math.exp(-t * 9.0)
            phase = 2 * math.pi * (36 * t + (104 / 9.0) * (1 - math.exp(-t * 9.0)))
            # Sub-bass sine with soft saturation
            raw = math.sin(phase)
            sub = math.tanh(raw * 1.5)
            # High-end transient click at t=0
            click = math.sin(2 * math.pi * 950 * t) * math.exp(-t * 120.0) * 0.45
            env = math.exp(-t * 3.2)
            samples.append((sub * 0.8 + click) * env * 0.9)
        _write_wav(SFX_DIR / "impact.wav", samples, SR)

    # 4. Click / Pop (мягкий щелчок интерфейса, 0.08с)
    if not (SFX_DIR / "click.wav").exists():
        dur = 0.08
        N = int(SR * dur)
        samples = []
        for i in range(N):
            t = i / SR
            freq = 1900 + 400 * math.exp(-t * 80.0)
            env = math.exp(-t * 60.0)
            tone = math.sin(2 * math.pi * freq * t)
            samples.append(tone * env * 0.65)
        _write_wav(SFX_DIR / "click.wav", samples, SR)

    # 5. Riser (нарастающий саспенс-подъем, 1.4с)
    if not files["riser"].exists():
        dur = 1.4
        N = int(SR * dur)
        samples = []
        for i in range(N):
            t = i / SR
            norm_t = t / dur
            # Exponential pitch rise from 110Hz to 1400Hz
            freq = 110 * (1400 / 110) ** norm_t
            # Phase integral
            phase = 2 * math.pi * 110 * ((1400 / 110) ** norm_t - 1) / math.log(1400 / 110)
            # Vibrato
            vib = math.sin(2 * math.pi * 6.0 * t) * 0.1
            env = norm_t ** 1.6
            tone = math.sin(phase + vib)
            samples.append(tone * env * 0.7)
        _write_wav(files["riser"], samples, SR)

    # 6. Heartbeat (глухой двойной удар сердца, 0.9с)
    if not files["heartbeat"].exists():
        dur = 0.9
        N = int(SR * dur)
        samples = []
        for i in range(N):
            t = i / SR
            val = 0.0
            # Thump 1 at t=0.0
            if t < 0.35:
                t1 = t
                env1 = math.exp(-t1 * 12.0)
                freq1 = 54 + 20 * math.exp(-t1 * 25.0)
                val += math.sin(2 * math.pi * freq1 * t1) * env1 * 0.8
            # Thump 2 at t=0.28
            if t >= 0.28 and t < 0.65:
                t2 = t - 0.28
                env2 = math.exp(-t2 * 14.0)
                freq2 = 46 + 18 * math.exp(-t2 * 25.0)
                val += math.sin(2 * math.pi * freq2 * t2) * env2 * 0.65
            samples.append(val)
        _write_wav(files["heartbeat"], samples, SR)

    return files


def extract_sfx_events(
    script_text: str,
    total_duration: float,
    scenes: list[dict] | None = None,
    word_timestamps: list[dict] | None = None,
    preset: str = "facts",
) -> list[dict]:
    """Извлекает явные теги [sfx: ...] из сценария и дополняет их кинематографическими авто-SFX

    (переходы между сценами, стартовый хук, тревожные моменты).
    """
    sfx_files = ensure_default_sfx()
    events: list[dict] = []

    # 1. Стартовый удар в момент хука (t=0.1s)
    first_sound = "glitch" if preset == "horror_rules" else "impact"
    events.append({
        "type": first_sound,
        "file": sfx_files.get(first_sound, sfx_files["impact"]),
        "offset": 0.08,
        "volume": 0.40,
    })

    # 2. Явные теги [sfx: tag_name] в тексте
    # Ищем позицию тега в процентах от длины текста
    clean_len = max(1, len(re.sub(r"\[sfx:\s*\w+\]", "", script_text)))
    for m in re.finditer(r"\[sfx:\s*([a-zA-Z0-9_]+)\]", script_text, flags=re.I):
        tag = m.group(1).lower()
        if tag in sfx_files:
            # Вычисляем относительный тайминг
            char_pos = m.start()
            ratio = min(0.95, max(0.05, char_pos / clean_len))
            est_time = round(ratio * total_duration, 2)
            events.append({
                "type": tag,
                "file": sfx_files[tag],
                "offset": est_time,
                "volume": 0.45,
            })

    # 3. Авто-SFX на переходах между сценами
    num_scenes = len(scenes) if scenes else 4
    if num_scenes > 1:
        scene_interval = total_duration / num_scenes
        for s_idx in range(1, num_scenes):
            t_trans = round(s_idx * scene_interval, 2)
            # Избегаем наложения на близкие существующие SFX (< 0.5с)
            if any(abs(e["offset"] - t_trans) < 0.6 for e in events):
                continue
            
            # В зависимости от пресета выбираем звук перехода
            if preset == "horror_rules":
                trans_snd = "glitch" if (s_idx % 2 == 1) else "heartbeat"
            elif preset in ("it", "tech"):
                trans_snd = "glitch" if (s_idx % 2 == 1) else "whoosh"
            else:
                trans_snd = "whoosh"

            events.append({
                "type": trans_snd,
                "file": sfx_files.get(trans_snd, sfx_files["whoosh"]),
                "offset": t_trans,
                "volume": 0.32,
            })

    # 4. Финальный SFX перед CTA карточкой
    if total_duration > 4.5:
        cta_time = round(max(1.5, total_duration - 2.5), 2)
        if not any(abs(e["offset"] - cta_time) < 0.6 for e in events):
            events.append({
                "type": "click",
                "file": sfx_files["click"],
                "offset": cta_time,
                "volume": 0.35,
            })

    # Сортируем события по времени
    events.sort(key=lambda x: x["offset"])
    return events
