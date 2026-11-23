"""
Cartoon SFX Module: Synthesizes sound effects for 2D explainer videos (100% offline).
- Coin / Cash Register Chime (for balance HUD updates)
- Bubble Pop (for speech bubbles and pills)
- Shock / Dramatic Tension Hit (for cliffhangers & plot twists)
"""

import wave
from pathlib import Path
import numpy as np

SAMPLE_RATE = 44100


def _save_wav(path: Path, data: np.ndarray, sr: int = SAMPLE_RATE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    mx = np.max(np.abs(data))
    if mx > 1e-6:
        data = data / mx * 0.92
    data_int16 = (data * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(data_int16.tobytes())
    return path


def synth_coin_ding(out_path: Path) -> Path:
    """Bright metallic twin-bell chime for money/balance counters."""
    t = np.linspace(0, 1.2, int(SAMPLE_RATE * 1.2), endpoint=False)
    # 2 high harmonic frequencies
    bell1 = np.sin(2 * np.pi * 2093.0 * t) * np.exp(-4.5 * t)  # C7
    bell2 = np.sin(2 * np.pi * 3136.0 * t) * np.exp(-6.0 * t)  # G7
    bell3 = np.sin(2 * np.pi * 4186.0 * t) * np.exp(-9.0 * t)  # C8
    audio = 0.5 * bell1 + 0.35 * bell2 + 0.15 * bell3
    return _save_wav(out_path, audio)


def synth_bubble_pop(out_path: Path) -> Path:
    """Short cheerful pop sound for appearing bubbles and badges."""
    dur = 0.12
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    # Quick frequency pitch rise from 160Hz to 680Hz
    freq = 160 + 520 * (t / dur) ** 0.5
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    audio = np.sin(phase) * np.exp(-28 * t)
    return _save_wav(out_path, audio)


def synth_alert_sting(out_path: Path) -> Path:
    """Dramatic tension hit for plot twists, surprises, and alarms."""
    dur = 1.6
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    # Dissonant chord + low impact boom
    low_boom = np.sin(2 * np.pi * 65.0 * t) * np.exp(-3.5 * t)
    dissonant1 = np.sin(2 * np.pi * 587.3 * t) * np.exp(-4.0 * t)  # D5
    dissonant2 = np.sin(2 * np.pi * 622.2 * t) * np.exp(-4.0 * t)  # Eb5 (minor second clash)
    noise = np.random.uniform(-0.1, 0.1, len(t)) * np.exp(-7.0 * t)
    audio = 0.6 * low_boom + 0.25 * dissonant1 + 0.25 * dissonant2 + 0.1 * noise
    return _save_wav(out_path, audio)


def synth_whoosh(out_path: Path) -> Path:
    """Crisp modern cinematic whip-pan whoosh for scene/location transitions."""
    dur = 0.35
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), endpoint=False)
    # Filtered white noise swept with bell envelope
    noise = np.random.uniform(-1.0, 1.0, len(t))
    # Simple moving average lowpass sweeping via amplitude envelope
    env = np.sin(np.pi * (t / dur)) ** 1.8
    # Low-mid body tone sweep
    freq = 120 + 420 * np.sin(np.pi * (t / dur))
    body = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE) * env * 0.45
    # Smooth noise slightly
    kernel = np.ones(18) / 18.0
    smooth_noise = np.convolve(noise, kernel, mode="same") * env * 0.7
    return _save_wav(out_path, body + smooth_noise)
