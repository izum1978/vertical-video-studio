"""Модуль кинематографичной озвучки (100% бесплатно через Edge-TTS + FFmpeg мастеринг).

Превращает обычный текст в густой, низкий, атмосферный голос диктора трейлеров
с пословными таймкодами для караоке-субтитров.
"""
import asyncio
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

import edge_tts

FFMPEG_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).exists():
    FFMPEG_BIN = "ffmpeg"

FFPROBE_BIN = r"C:\OSPanel\addons\FFMpeg\bin\ffprobe.exe"
if not Path(FFPROBE_BIN).exists():
    FFPROBE_BIN = "ffprobe"


def _clean_text(text: str) -> str:
    """Удаляет маркеры ударений и акцентов для чистого синтеза."""
    t = re.sub(r"[*!]", "", text)
    t = re.sub(r"\[sfx:[^\]]+\]", "", t)
    return t.strip()


async def _synthesize_edge(
    text: str,
    raw_mp3: Path,
    voice: str = "ru-RU-SvetlanaNeural",
    rate: str = "-4%",
    pitch: str = "-4Hz",
) -> List[Dict]:
    """Синтезирует речь и собирает реальные пословные таймкоды от Microsoft TTS."""
    clean = _clean_text(text)
    
    # Пытаемся сначала запросить с WordBoundary
    try:
        communicate = edge_tts.Communicate(clean, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    except TypeError:
        communicate = edge_tts.Communicate(clean, voice, rate=rate, pitch=pitch)

    words = []
    with open(raw_mp3, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_sec = round(chunk["offset"] / 10_000_000, 3)
                dur_sec = round(chunk["duration"] / 10_000_000, 3)
                words.append({
                    "word": chunk["text"],
                    "start": start_sec,
                    "end": round(start_sec + dur_sec, 3),
                })
    return words


def _master_voice_audio(raw_mp3: Path, out_mp3: Path) -> Path:
    """Кинематографичный мастеринг голоса:

    1. highpass: срез ненужного низкочастотного гула ниже 60 Гц.
    2. equalizer: насыщение плотного баса на 110 Гц (+4.5 dB).
    3. acompressor: студийная плотность голоса (как на радио/в кино).
    4. loudnorm: профессиональная нормализация громкости под стриминги (-14 LUFS).
    """
    filters = (
        "highpass=f=60,"
        "equalizer=f=110:width_type=o:w=1.2:g=4.5,"
        "equalizer=f=3200:width_type=o:w=1.0:g=2.0,"
        "acompressor=threshold=-18dB:ratio=4:attack=5:release=60,"
        "loudnorm=I=-14:LRA=7:TP=-1.5"
    )

    cmd = [
        FFMPEG_BIN, "-y",
        "-i", str(raw_mp3),
        "-af", filters,
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(out_mp3),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_mp3


def generate_cinematic_voice(
    text: str,
    out_dir: Path,
    voice: str = "ru-RU-SvetlanaNeural",
    pitch: str = "-4Hz",
    rate: str = "-4%",
) -> Tuple[Path, List[Dict], float]:
    """Генерирует готовую озвучку, файл таймкодов и возвращает (путь_к_mp3, слова, длительность)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_mp3 = out_dir / "raw_voice.mp3"
    mastered_mp3 = out_dir / "cinematic_voice.mp3"
    words_json = out_dir / "words.json"

    # Синтез речи
    try:
        words = asyncio.run(_synthesize_edge(text, raw_mp3, voice=voice, rate=rate, pitch=pitch))
    except Exception:
        # Автоматический откат на Дмитрия без питча, если голос был недоступен
        fallback_voice = "ru-RU-DmitryNeural" if voice != "ru-RU-DmitryNeural" else "ru-RU-SvetlanaNeural"
        words = asyncio.run(_synthesize_edge(text, raw_mp3, voice=fallback_voice, rate=rate, pitch="+0Hz"))

    # Студийный мастеринг звука
    _master_voice_audio(raw_mp3, mastered_mp3)

    # Определение точной длительности через ffprobe
    cmd = [
        FFPROBE_BIN, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(mastered_mp3),
    ]
    try:
        dur_str = subprocess.check_output(cmd, text=True).strip()
        duration = float(dur_str)
    except Exception:
        duration = words[-1]["end"] if words else 5.0

    # Сохраняем слова в JSON
    words_json.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")

    # Удаляем черновик
    if raw_mp3.exists():
        raw_mp3.unlink()

    return mastered_mp3, words, duration
