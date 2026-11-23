"""Модуль процедурного саунд-дизайна и SFX-эффектов (100% бесплатно и локально).

Генерирует высококачественные кинематографичные звуковые эффекты (44.1kHz / 16-bit):
- Тяжёлый глухой удар двери (heavy_door_slam)
- Суб-басовый дроп / импакт (sub_boom)
- Физиологичный испуганный вдох персонажа (breath)
- Затухающий потусторонний шёпот (whisper)
- Двойной низкочастотный стук сердца (heartbeat)
- Скрип старых деревянных половиц (footstep_creak)
- Звонкая капля в пустом бункере с эхом (water_drip)
- Треск и гудение неоновой лампы (electric_flicker)
- Нарастающий диссонирующий саспенс-гул (tension_riser)
- Тиканье старых часов (clock_tick)
- Глубокий кинематографичный пролёт камеры (whoosh)
- Цифровой сбой и помехи (glitch)

Обеспечивает точечную привязку звуков к мимике персонажей (LivePortrait) и саспенс-моментам.
"""
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import scipy.signal as signal

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SFX_DIR = WORKSPACE_ROOT / "backend" / "assets" / "sfx"
DEFAULT_SFX_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100


def _norm(sig: np.ndarray, peak: float = 0.92) -> np.ndarray:
    """Нормализует амплитуду и конвертирует в int16."""
    mx = np.max(np.abs(sig))
    if mx > 1e-6:
        sig = sig / mx * peak
    return (sig * 32767).astype(np.int16)


# ---------------------------------------------------------------------------
# ПРОЦЕДУРНЫЕ ГЕНЕРАТОРЫ ГОЛЛИВУДСКИХ КИНЕМАТОГРАФИЧНЫХ ЗВУКОВ
# ---------------------------------------------------------------------------

def synth_heavy_door_slam(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Глухой массивный удар закрывающейся тяжёлой двери с саб-басовым резонансом."""
    t = np.linspace(0, 1.8, int(sr * 1.8), endpoint=False)
    # Низкочастотный спад основного тона
    f_sweep = 140 * np.exp(-5.5 * t) + 38
    body = np.sin(2 * np.pi * np.cumsum(f_sweep) / sr) * np.exp(-3.5 * t)
    # Металлический/деревянный щелчок в момент захлопывания
    noise = np.random.normal(0, 1, len(t))
    b, a = signal.butter(2, [140 / (sr / 2), 700 / (sr / 2)], btype="band")
    transient = signal.lfilter(b, a, noise) * np.exp(-40 * t)
    # Сатурация для плотности баса
    out = np.tanh(1.6 * (body + 1.4 * transient))
    return _norm(out, peak=0.95)


def synth_sub_boom(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Инфразвуковой кинематографичный дроп (30-75Hz), сотрясающий сабвуфер/наушники."""
    t = np.linspace(0, 2.2, int(sr * 2.2), endpoint=False)
    f = 75 * np.exp(-1.8 * t) + 26
    sub = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-1.9 * t)
    sub_harmonic = 0.45 * np.sin(4 * np.pi * np.cumsum(f) / sr) * np.exp(-2.5 * t)
    out = np.tanh(2.0 * (sub + sub_harmonic))
    return _norm(out, peak=0.96)


def synth_breath_gasp(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Естественный испуганный вдох персонажа при открытии рта."""
    t = np.linspace(0, 0.65, int(sr * 0.65), endpoint=False)
    # Огибающая: быстрый вдох (0.2с) и мягкое затухание
    env = np.where(t < 0.20, (t / 0.20) ** 1.8, np.exp(-5.5 * (t - 0.20)))
    noise = np.random.normal(0, 1, len(t))
    # Форманты человеческого горла (600-1100Hz и 1600-2400Hz)
    b1, a1 = signal.butter(2, [600 / (sr / 2), 1100 / (sr / 2)], btype="band")
    b2, a2 = signal.butter(2, [1600 / (sr / 2), 2400 / (sr / 2)], btype="band")
    formants = signal.lfilter(b1, a1, noise) * 0.6 + signal.lfilter(b2, a2, noise) * 0.4
    return _norm(formants * env, peak=0.85)


def synth_whisper_eerie(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Затухающий мистический шёпот с пространственным эхом."""
    t = np.linspace(0, 1.4, int(sr * 1.4), endpoint=False)
    env = np.sin(np.pi * t / 1.4) ** 1.5
    noise = np.random.normal(0, 1, len(t))
    b, a = signal.butter(3, [1200 / (sr / 2), 3400 / (sr / 2)], btype="band")
    w = signal.lfilter(b, a, noise) * env
    echo = 0.35 * np.roll(w, int(sr * 0.14)) + 0.18 * np.roll(w, int(sr * 0.28))
    return _norm(w + echo, peak=0.80)


def synth_heartbeat(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Двойной физиологичный стук сердца (45-65Hz) с суб-басом."""
    t = np.linspace(0, 0.9, int(sr * 0.9), endpoint=False)
    lub = np.sin(2 * np.pi * 50 * t) * np.exp(-((t - 0.05) ** 2) / 0.003)
    dub = 0.72 * np.sin(2 * np.pi * 65 * t) * np.exp(-((t - 0.29) ** 2) / 0.003)
    return _norm(lub + dub, peak=0.92)


def synth_footstep_creak(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Зловещий скрип старых деревянных половиц под шагом."""
    t = np.linspace(0, 0.75, int(sr * 0.75), endpoint=False)
    f_mod = 420 + 80 * np.sin(2 * np.pi * 18 * t)
    noise = np.random.normal(0, 1, len(t))
    b, a = signal.butter(2, [350 / (sr / 2), 1200 / (sr / 2)], btype="band")
    filtered = signal.lfilter(b, a, noise)
    creak = filtered * np.sin(2 * np.pi * np.cumsum(f_mod) / sr)
    env = np.where(t < 0.15, t / 0.15, np.exp(-4 * (t - 0.15)))
    return _norm(creak * env, peak=0.88)


def synth_water_drip(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Звонкая одиночная капля в сыром подвале/бункере с кавернозным эхом."""
    t = np.linspace(0, 0.85, int(sr * 0.85), endpoint=False)
    f = 2300 * np.exp(-65 * t) + 1100
    drip = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-18 * t)
    echo = 0.35 * np.roll(drip, int(sr * 0.13)) + 0.18 * np.roll(drip, int(sr * 0.26))
    return _norm(drip + echo, peak=0.88)


def synth_electric_flicker(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Треск и зуммер умирающей неоновой лампы перед выключением."""
    t = np.linspace(0, 0.85, int(sr * 0.85), endpoint=False)
    hum = np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t)
    gate = (np.sin(2 * np.pi * 7 * t) > 0.2).astype(float)
    sparks = np.random.normal(0, 1, len(t)) * (np.random.rand(len(t)) > 0.985)
    b, a = signal.butter(1, 4000 / (sr / 2), btype="high")
    sparks = signal.lfilter(b, a, sparks) * 4.0
    out = (hum * gate * 0.4 + sparks) * np.exp(-2.0 * t)
    return _norm(out, peak=0.85)


def synth_tension_riser(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Нарастающий диссонирующий саспенс-гул перед кульминацией."""
    t = np.linspace(0, 3.2, int(sr * 3.2), endpoint=False)
    f = 65 * np.exp(0.65 * t)
    phase1 = 2 * np.pi * np.cumsum(f) / sr
    phase2 = 2 * np.pi * np.cumsum(f * 1.015) / sr
    tones = 0.5 * np.sin(phase1) + 0.5 * np.sin(phase2)
    noise = np.random.normal(0, 1, len(t))
    b, a = signal.butter(1, 1500 / (sr / 2), btype="high")
    noise = signal.lfilter(b, a, noise)
    env = (t / 3.2) ** 2.2
    return _norm((tones * 0.7 + noise * 0.3) * env, peak=0.92)


def synth_clock_tick(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Чёткий механический щелчок маятниковых часов."""
    t = np.linspace(0, 0.25, int(sr * 0.25), endpoint=False)
    click = np.sin(2 * np.pi * 3400 * t) * np.exp(-60 * t)
    thump = 0.6 * np.sin(2 * np.pi * 380 * t) * np.exp(-35 * t)
    return _norm(click + thump, peak=0.90)


def synth_whoosh(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Глубокий кинематографичный переход/пролёт камеры."""
    t = np.linspace(0, 1.1, int(sr * 1.1), endpoint=False)
    env = np.sin(np.pi * t / 1.1) ** 2
    noise = np.random.normal(0, 1, len(t))
    b, a = signal.butter(2, [250 / (sr / 2), 2400 / (sr / 2)], btype="band")
    out = signal.lfilter(b, a, noise) * env
    return _norm(out, peak=0.92)


def synth_glitch(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Радиопомехи, скачок частоты и цифровой сбой."""
    t = np.linspace(0, 0.45, int(sr * 0.45), endpoint=False)
    tone = np.sin(2 * np.pi * 950 * t * (1 + 0.3 * np.sin(2 * np.pi * 45 * t)))
    burst = np.random.normal(0, 1, len(t)) * (np.sin(2 * np.pi * 12 * t) > 0.0)
    out = (tone * 0.6 + burst * 0.4) * np.exp(-3.0 * t)
    return _norm(out, peak=0.88)


# Словарь всех генераторов
SFX_REGISTRY = {
    "door_slam": synth_heavy_door_slam,
    "heavy_door_slam": synth_heavy_door_slam,
    "impact": synth_sub_boom,
    "sub_boom": synth_sub_boom,
    "breath": synth_breath_gasp,
    "breath_gasp": synth_breath_gasp,
    "whisper": synth_whisper_eerie,
    "heartbeat": synth_heartbeat,
    "heartbeat_pulse": synth_heartbeat,
    "footstep_creak": synth_footstep_creak,
    "water_drip": synth_water_drip,
    "electric_flicker": synth_electric_flicker,
    "tension_riser": synth_tension_riser,
    "riser": synth_tension_riser,
    "clock_tick": synth_clock_tick,
    "click": synth_clock_tick,
    "whoosh": synth_whoosh,
    "glitch": synth_glitch,
}


def generate_sfx_file(sfx_name: str, out_path: Optional[Path] = None, sr: int = SAMPLE_RATE) -> Path:
    """Генерирует конкретный звуковой эффект в WAV файл."""
    gen_func = SFX_REGISTRY.get(sfx_name, synth_whoosh)
    audio_i16 = gen_func(sr=sr)

    if out_path is None:
        out_path = DEFAULT_SFX_DIR / f"{sfx_name}.wav"
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with wave.open(str(out_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_i16.tobytes())

    return out_path


def ensure_sfx_library(target_dir: Optional[Path] = None) -> Path:
    """Гарантирует наличие всех 12 звуковых эффектов в директории SFX."""
    sfx_dir = Path(target_dir) if target_dir else DEFAULT_SFX_DIR
    sfx_dir.mkdir(parents=True, exist_ok=True)

    # Уникальные имена файлов для генерации
    unique_names = [
        "door_slam",
        "impact",
        "sub_boom",
        "breath",
        "whisper",
        "heartbeat",
        "footstep_creak",
        "water_drip",
        "electric_flicker",
        "riser",
        "tension_riser",
        "click",
        "clock_tick",
        "whoosh",
        "glitch",
    ]

    for name in unique_names:
        p = sfx_dir / f"{name}.wav"
        if not p.exists() or p.stat().st_size < 1000:
            generate_sfx_file(name, out_path=p)

    return sfx_dir


# ---------------------------------------------------------------------------
# АВТОМАТИЧЕСКАЯ РЕЖИССУРА ЗВУКА И ТОЧЕЧНАЯ ПРИВЯЗКА К СЦЕНАМ
# ---------------------------------------------------------------------------

def get_scene_sfx_events(
    scenes: list,
    timings: List[Tuple[float, float]],
) -> List[Tuple[float, str, float]]:
    """Строит детальный звуковой таймлайн событий:
    
    Returns:
        List of (timestamp_seconds, sfx_name, volume_factor)
    """
    events: List[Tuple[float, str, float]] = []

    for idx, (scene, (s_start, s_dur)) in enumerate(zip(scenes, timings)):
        # 1. Атмосферный фоли-звук на старте кадра
        cue = getattr(scene, "sfx_cue", None)
        if cue:
            events.append((round(s_start, 2), cue, 0.75))
        elif idx == 0:
            events.append((round(s_start, 2), "impact", 0.85))

        # 2. Точечная привязка к анимации персонажей LivePortrait:
        if getattr(scene, "is_character", False):
            # Вздох персонажа точно перед началом реплики (через 0.12 сек после появления)
            breath_time = round(s_start + 0.12, 2)
            events.append((breath_time, "breath", 0.55))

            # Стук сердца в кульминации реплики
            if s_dur > 1.8:
                tension_point = round(s_start + s_dur * 0.50, 2)
                events.append((tension_point, "heartbeat", 0.65))

        # 3. Финальный клиффхэнгер: нагнетание саспенса перед тишиной
        if idx == len(scenes) - 1 and s_dur > 2.0:
            riser_time = max(0.0, round(s_start + s_dur - 2.8, 2))
            events.append((riser_time, "tension_riser", 0.70))

    # Сортируем события по времени
    events.sort(key=lambda x: x[0])
    return events


if __name__ == "__main__":
    print("Генерация полной коллекции кинематографичных SFX...")
    d = ensure_sfx_library()
    files = list(d.glob("*.wav"))
    print(f"Готово! В библиотеке {len(files)} звуковых эффектов:")
    for f in sorted(files):
        print(f" - {f.name} ({f.stat().st_size} bytes)")
